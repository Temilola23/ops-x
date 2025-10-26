"""
Chat API - Real-time team collaboration chat with Janitor AI
Integrates with Socket.IO for real-time messaging
"""

import os
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models import ChatMessage, Project, Stakeholder, User, Refinement
from integrations.jllm_api import jllm_agent
from integrations.fetchai_router import fetchai_router

router = APIRouter()


class SendMessageRequest(BaseModel):
    message: str
    stakeholder_id: int


class ChatMessageResponse(BaseModel):
    id: int
    project_id: int
    user_id: Optional[int]
    message: str
    role: str
    is_ai: bool
    created_at: datetime
    author_name: str
    
    class Config:
        from_attributes = True


def should_janitor_respond(message: str, recent_messages: List[ChatMessage]) -> bool:
    """
    Determine if Janitor AI should respond to this message
    
    Respond when:
    - Message is a question (contains ?)
    - Message mentions tasks/features
    - Multiple stakeholders are chatting (moderation needed)
    - Someone asks for help
    """
    message_lower = message.lower()
    
    # Always respond to questions
    if "?" in message:
        return True
    
    # Respond to direct requests
    help_keywords = ["help", "suggest", "recommend", "what should", "how do", "janitor"]
    if any(kw in message_lower for kw in help_keywords):
        return True
    
    # Respond occasionally to keep conversation going
    # (every 3rd message approximately)
    if len(recent_messages) % 3 == 0:
        return True
    
    return False


async def broadcast_message(sio, project_id: int, messages: List[dict]):
    """Broadcast messages to all clients in project room"""
    try:
        await sio.emit(
            "chat:message",
            {
                "project_id": project_id,
                "messages": messages
            },
            room=str(project_id)
        )
    except Exception as e:
        print(f"❌ WebSocket broadcast error: {e}")


@router.post("/projects/{project_id}/chat/message")
async def send_chat_message(
    project_id: int,
    request: SendMessageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send a chat message
    
    Flow:
    1. Save user message to database
    2. Analyze with Fetch.ai router (is this a task?)
    3. If task detected → create refinement, trigger agent
    4. Decide if Janitor AI should respond
    5. Save AI response if applicable
    6. Broadcast all messages via WebSocket
    """
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify stakeholder
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == request.stakeholder_id).first()
        if not stakeholder:
            raise HTTPException(status_code=404, detail="Stakeholder not found")
        
        # Get stakeholder's user
        user_id = stakeholder.user_id
        author_name = stakeholder.name
        
        print(f"📝 Sending message: stakeholder_id={stakeholder.id}, user_id={user_id}, email={stakeholder.email}")
        
        # Critical: Ensure user_id is not NULL
        if not user_id:
            print(f"⚠️ Stakeholder {stakeholder.id} has no user_id! Looking up user by email...")
            # Try to link stakeholder to user by email
            user = db.query(User).filter(User.email == stakeholder.email).first()
            if user:
                stakeholder.user_id = user.id
                stakeholder.status = "active"
                db.commit()
                user_id = user.id
                print(f"✅ Linked stakeholder to user {user_id}")
            else:
                print(f"❌ No user found for email {stakeholder.email}")
                raise HTTPException(
                    status_code=400,
                    detail=f"User account not found for {stakeholder.email}. Please sign in first."
                )
        
        # 1. Save user message
        user_msg = ChatMessage(
            project_id=project_id,
            user_id=user_id,
            message=request.message,
            role=stakeholder.role,
            is_ai=False
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        
        print(f"✅ Message saved: id={user_msg.id}, user_id={user_id}")
        
        messages_to_broadcast = [{
            "id": user_msg.id,
            "project_id": user_msg.project_id,
            "message": user_msg.message,
            "role": user_msg.role,
            "is_ai": False,
            "created_at": user_msg.created_at.isoformat(),
            "author_name": author_name
        }]
        
        # 2. Analyze with Fetch.ai router - is this a code change request?
        task_analysis = fetchai_router.route_refinement(
            request_text=request.message,
            stakeholder_role=stakeholder.role,
            ai_model_preference="auto"
        )
        
        print(f"🤖 Fetch.ai analysis: {task_analysis}")
        
        # 3. If high confidence task detected → create refinement
        if task_analysis["confidence"] > 0.6:
            refinement = Refinement(
                project_id=project_id,
                stakeholder_id=stakeholder.id,
                request_text=request.message,
                ai_model_preference="auto",
                ai_model_used=task_analysis["model"],
                status="pending"
            )
            db.add(refinement)
            db.commit()
            
            print(f"✅ Created refinement {refinement.id} for {task_analysis['model']} agent")
            
            # Trigger agent in background
            background_tasks.add_task(
                execute_refinement_task,
                refinement.id,
                task_analysis["model"],
                db
            )
        
        # 4. Get recent chat history for context
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.project_id == project_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        
        # 5. Decide if Janitor AI should respond (with error handling)
        try:
            if should_janitor_respond(request.message, recent_messages):
                print("🤖 Janitor AI responding...")
                
                # Build context
                team_members = db.query(Stakeholder).filter(
                    Stakeholder.project_id == project_id
                ).all()
                
                team_context = [
                    {
                        "name": s.name,
                        "email": s.email,
                        "role": s.role
                    }
                    for s in team_members
                ]
                
                chat_history = [
                    {
                        "role": "assistant" if msg.is_ai else "user",
                        "content": msg.message
                    }
                    for msg in reversed(recent_messages[1:])  # Exclude current message
                ]
                
                # Get Janitor AI response
                janitor_response = await jllm_agent.get_response(
                    message=request.message,
                    chat_history=chat_history,
                    project_context=f"{project.name}: {project.prompt}",
                    team_members=team_context
                )
                
                # Add info about task detection
                if task_analysis["confidence"] > 0.6:
                    janitor_response += f"\n\n🤖 I detected this as a {task_analysis['reasoning']}. Routing to {task_analysis['model']} agent..."
                
                # Save AI message
                ai_msg = ChatMessage(
                    project_id=project_id,
                    user_id=None,  # AI has no user
                    message=janitor_response,
                    role="Facilitator",
                    is_ai=True
                )
                db.add(ai_msg)
                db.commit()
                db.refresh(ai_msg)
                
                print(f"✅ Janitor AI response saved: id={ai_msg.id}")
                
                messages_to_broadcast.append({
                    "id": ai_msg.id,
                    "project_id": ai_msg.project_id,
                    "message": ai_msg.message,
                    "role": "Facilitator",
                    "is_ai": True,
                    "created_at": ai_msg.created_at.isoformat(),
                    "author_name": "Janitor AI"
                })
        except Exception as janitor_error:
            print(f"⚠️ Janitor AI error (non-fatal): {str(janitor_error)}")
            # Continue without Janitor AI response - not critical
        
        # 6. Broadcast via WebSocket
        from main import sio
        await broadcast_message(sio, project_id, messages_to_broadcast)
        
        return {
            "success": True,
            "data": messages_to_broadcast
        }
        
    except Exception as e:
        print(f"❌ Chat message error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/chat/messages")
async def get_chat_messages(
    project_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat message history"""
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.project_id == project_id
        ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
        
        # Enrich with author names
        result = []
        for msg in messages:
            if msg.is_ai:
                author_name = "Janitor AI"
            elif msg.user_id:
                stakeholder = db.query(Stakeholder).filter(
                    Stakeholder.user_id == msg.user_id,
                    Stakeholder.project_id == project_id
                ).first()
                author_name = stakeholder.name if stakeholder else "Unknown"
            else:
                author_name = "System"
            
            result.append({
                "id": msg.id,
                "project_id": msg.project_id,
                "message": msg.message,
                "role": msg.role,
                "is_ai": msg.is_ai,
                "created_at": msg.created_at.isoformat(),
                "author_name": author_name,
                "timestamp": msg.created_at.isoformat()  # For compatibility
            })
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Get messages error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_refinement_task(refinement_id: int, model: str, db: Session):
    """
    Execute a refinement task with the appropriate AI agent
    Actually calls v0 or Claude to generate code changes
    """
    try:
        refinement = db.query(Refinement).filter(Refinement.id == refinement_id).first()
        if not refinement:
            print(f"❌ Refinement {refinement_id} not found")
            return
        
        project = db.query(Project).filter(Project.id == refinement.project_id).first()
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == refinement.stakeholder_id).first()
        
        refinement.status = "processing"
        db.commit()
        
        # Send "working on it" message
        working_msg = ChatMessage(
            project_id=project.id,
            user_id=None,
            message=f"🤖 Working on it...\n\nTask: {refinement.request_text}\nAgent: {model.upper()}",
            role="Facilitator",
            is_ai=True
        )
        db.add(working_msg)
        db.commit()
        db.refresh(working_msg)
        
        # Broadcast "working" message
        from main import sio
        await broadcast_message(sio, project.id, [{
            "id": working_msg.id,
            "project_id": working_msg.project_id,
            "message": working_msg.message,
            "role": "Facilitator",
            "is_ai": True,
            "created_at": working_msg.created_at.isoformat(),
            "author_name": "Janitor AI"
        }])
        
        print(f"🚀 Executing refinement {refinement_id} with {model} agent")
        
        # Import agents
        from integrations.claude_api import claude_agent
        import httpx
        
        files_changed = []
        new_preview_url = None
        success = False
        error_msg = None
        
        try:
            if model == "v0" and project.v0_chat_id:
                # Frontend task - call v0 SDK via frontend API
                # We need to call the Next.js server action
                print(f"📱 Calling v0 for chat_id: {project.v0_chat_id}")
                
                # For now, we'll use v0 API directly (TypeScript SDK is frontend-only)
                # This is a workaround - ideally frontend handles v0
                v0_api_key = os.getenv("V0_API_KEY")
                if v0_api_key:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            "https://api.v0.dev/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {v0_api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "messages": [
                                    {"role": "user", "content": refinement.request_text}
                                ],
                                "model": "v0-v1"
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            # Extract preview URL if available
                            if "choices" in result and len(result["choices"]) > 0:
                                content = result["choices"][0].get("message", {}).get("content", "")
                                # v0 returns markdown with preview URLs
                                import re
                                preview_match = re.search(r'https://v0\.dev/chat/[a-zA-Z0-9\-]+', content)
                                if preview_match:
                                    new_preview_url = preview_match.group(0)
                                    print(f"✅ Got new preview URL: {new_preview_url}")
                            
                            files_changed = ["UI components updated"]
                            success = True
                        else:
                            error_msg = f"v0 API error: {response.status_code}"
                            print(f"❌ {error_msg}")
                else:
                    error_msg = "V0_API_KEY not configured"
                    print(f"❌ {error_msg}")
            
            elif model == "claude":
                # Backend task - use Claude
                print(f"🧠 Calling Claude for backend task")
                
                if claude_agent:
                    # Get existing code context (simplified)
                    current_files = {}  # Would fetch from GitHub in production
                    
                    result_files = claude_agent.generate_backend_code(
                        refinement_request=refinement.request_text,
                        current_files=current_files,
                        project_context=f"Project: {project.name}\n{project.prompt}",
                        allowed_files=[]  # All files allowed
                    )
                    
                    if result_files:
                        files_changed = list(result_files.keys())
                        success = True
                        print(f"✅ Claude generated {len(files_changed)} files")
                    else:
                        error_msg = "Claude returned no files"
                        print(f"❌ {error_msg}")
                else:
                    error_msg = "Claude agent not configured"
                    print(f"❌ {error_msg}")
            
            # Update refinement status
            refinement.status = "completed" if success else "failed"
            refinement.files_changed = files_changed
            refinement.error_message = error_msg
            refinement.completed_at = datetime.now(timezone.utc)
            
            # Update preview URL if we got a new one
            if new_preview_url:
                project.v0_preview_url = new_preview_url
            
            db.commit()
            
            # Send completion message
            if success:
                completion_msg = ChatMessage(
                    project_id=project.id,
                    user_id=None,
                    message=f"✅ Task completed!\n\n" +
                            f"Changes: {', '.join(files_changed) if files_changed else 'UI updated'}\n" +
                            (f"Preview: {new_preview_url}" if new_preview_url else "Check the preview panel →"),
                    role="Facilitator",
                    is_ai=True
                )
            else:
                completion_msg = ChatMessage(
                    project_id=project.id,
                    user_id=None,
                    message=f"❌ Task failed: {error_msg}\n\n" +
                            "You can try refining your request or check the logs.",
                    role="Facilitator",
                    is_ai=True
                )
            
            db.add(completion_msg)
            db.commit()
            db.refresh(completion_msg)
            
            # Broadcast completion
            await broadcast_message(sio, project.id, [{
                "id": completion_msg.id,
                "project_id": completion_msg.project_id,
                "message": completion_msg.message,
                "role": "Facilitator",
                "is_ai": True,
                "created_at": completion_msg.created_at.isoformat(),
                "author_name": "Janitor AI"
            }])
            
            print(f"✅ Refinement {refinement_id} {'completed' if success else 'failed'}!")
            
        except Exception as agent_error:
            print(f"❌ Agent execution error: {str(agent_error)}")
            import traceback
            traceback.print_exc()
            
            # Send error message
            error_msg_obj = ChatMessage(
                project_id=project.id,
                user_id=None,
                message=f"❌ Error executing task: {str(agent_error)}",
                role="Facilitator",
                is_ai=True
            )
            db.add(error_msg_obj)
            db.commit()
            db.refresh(error_msg_obj)
            
            await broadcast_message(sio, project.id, [{
                "id": error_msg_obj.id,
                "project_id": error_msg_obj.project_id,
                "message": error_msg_obj.message,
                "role": "Facilitator",
                "is_ai": True,
                "created_at": error_msg_obj.created_at.isoformat(),
                "author_name": "Janitor AI"
            }])
            
            refinement.status = "failed"
            refinement.error_message = str(agent_error)
            db.commit()
        
    except Exception as e:
        print(f"❌ Refinement execution error: {str(e)}")
        import traceback
        traceback.print_exc()

