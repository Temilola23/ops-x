"""
Janitor AI Multiplayer Chat Integration
Handles multi-user chat with JLLM (25k context)
"""

import os
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Configuration
JANITOR_API_ENDPOINT = os.getenv("JANITOR_API_ENDPOINT", "https://janitorai.com/hackathon/completions")
JANITOR_API_KEY = os.getenv("JANITOR_API_KEY", "calhacks2047")

# In-memory storage for demo (use Redis/DB in production)
chat_rooms: Dict[str, List[Dict]] = {}
user_contexts: Dict[str, Dict] = {}


class ChatMessage(BaseModel):
    room_id: str
    user_id: str
    role: str  # Founder, FE, BE, Investor, Facilitator
    content: str


class ChatSummaryRequest(BaseModel):
    room_id: str
    max_messages: int = 50


class MultiUserPrompt(BaseModel):
    room_id: str
    messages: List[Dict]
    current_speaker: str
    current_role: str


@router.post("/chat/send")
async def send_message(message: ChatMessage):
    """Send a message to the multiplayer chat room"""
    
    # Initialize room if doesn't exist
    if message.room_id not in chat_rooms:
        chat_rooms[message.room_id] = []
    
    # Add message to room history
    chat_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": message.user_id,
        "role": message.role,
        "content": message.content
    }
    chat_rooms[message.room_id].append(chat_entry)
    
    # Get AI response for multiplayer context
    ai_response = await get_ai_response_for_room(message)
    
    return {
        "message_id": len(chat_rooms[message.room_id]) - 1,
        "ai_response": ai_response,
        "timestamp": chat_entry["timestamp"]
    }


@router.post("/chat/summarize")
async def summarize_chat(request: ChatSummaryRequest):
    """Summarize chat for context management (25k limit)"""
    
    if request.room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    messages = chat_rooms[request.room_id][-request.max_messages:]
    
    # Create summary prompt
    summary_prompt = create_summary_prompt(messages)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                JANITOR_API_ENDPOINT,
                headers={
                    "Authorization": JANITOR_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {"role": "system", "content": "You are a technical facilitator summarizing a multiplayer development discussion."},
                        {"role": "user", "content": summary_prompt}
                    ]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Store summary for context
                if request.room_id not in user_contexts:
                    user_contexts[request.room_id] = {}
                user_contexts[request.room_id]["summary"] = summary
                
                return {"summary": summary, "messages_processed": len(messages)}
            else:
                raise HTTPException(status_code=response.status_code, detail="Janitor AI error")
                
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"API connection error: {str(e)}")


async def get_ai_response_for_room(message: ChatMessage) -> Dict:
    """Get AI response considering multiplayer context"""
    
    # Build context from recent messages
    recent_messages = chat_rooms[message.room_id][-10:]  # Last 10 messages
    
    # Create multiplayer-aware prompt
    system_prompt = f"""You are facilitating a startup development session.
Current speaker: {message.user_id} (Role: {message.role})
Other participants: Various roles including Frontend, Backend, Investor, Founder.

Respond appropriately considering:
1. The speaker's role and expertise
2. Other participants in the room
3. The technical context of the discussion
4. Keep responses concise and actionable"""

    # Build conversation history
    conversation = [{"role": "system", "content": system_prompt}]
    
    for msg in recent_messages[:-1]:  # Exclude the current message
        conversation.append({
            "role": "assistant" if msg.get("ai_response") else "user",
            "content": f"[{msg['role']}] {msg['content']}"
        })
    
    # Add current message
    conversation.append({
        "role": "user",
        "content": f"[{message.role}] {message.content}"
    })
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                JANITOR_API_ENDPOINT,
                headers={
                    "Authorization": JANITOR_API_KEY,
                    "Content-Type": "application/json"
                },
                json={"messages": conversation},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Store AI response in chat history
                chat_rooms[message.room_id].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": "facilitator",
                    "role": "Facilitator",
                    "content": ai_content,
                    "ai_response": True
                })
                
                return {
                    "content": ai_content,
                    "role": "Facilitator",
                    "considers_role": message.role
                }
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Connection error: {str(e)}"}


def create_summary_prompt(messages: List[Dict]) -> str:
    """Create a summary prompt for context management"""
    
    # Group messages by role
    role_messages = {}
    for msg in messages:
        role = msg.get('role', 'Unknown')
        if role not in role_messages:
            role_messages[role] = []
        role_messages[role].append(msg['content'])
    
    prompt = "Summarize this multiplayer development discussion:\n\n"
    
    for role, contents in role_messages.items():
        prompt += f"{role} contributions:\n"
        for content in contents[-5:]:  # Last 5 messages per role
            prompt += f"- {content[:100]}...\n"
        prompt += "\n"
    
    prompt += "\nProvide a concise summary highlighting key decisions, conflicts, and action items."
    
    return prompt


@router.get("/chat/rooms")
async def list_rooms():
    """List all active chat rooms"""
    return {
        "rooms": [
            {
                "room_id": room_id,
                "message_count": len(messages),
                "participants": len(set(msg['user_id'] for msg in messages))
            }
            for room_id, messages in chat_rooms.items()
        ]
    }


@router.get("/chat/room/{room_id}")
async def get_room_messages(room_id: str, limit: int = 50):
    """Get recent messages from a room"""
    
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = chat_rooms[room_id][-limit:]
    
    return {
        "room_id": room_id,
        "messages": messages,
        "total_messages": len(chat_rooms[room_id])
    }
