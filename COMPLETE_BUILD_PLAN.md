# OPS-X COMPLETE BUILD PLAN
## Every Feature, Zero Compromises

**Status**: GitHub fixed. Building EVERYTHING.

---

## PHASE 1: Core Infrastructure (2-3 hours)

### 1.1 MCP Server (CRITICAL - Creao Prize)
**File**: `mcp_server/server.py`
```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("OPS-X")

@mcp.tool()
async def build_app(prompt: str) -> dict:
    """Build a complete app from a prompt"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/app/build/v0",
            json={"project_name": "generated", "requirements": prompt}
        )
        return response.json()

@mcp.tool()
async def detect_conflicts(repo_url: str) -> list:
    """Scan repo for merge conflicts"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/conflict/scan",
            json={"repo_url": repo_url}
        )
        return response.json()

@mcp.tool()
async def generate_pitch(project_data: dict) -> dict:
    """Generate investor pitch"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/pitch/generate",
            json=project_data
        )
        return response.json()
```

**TODO**:
- [ ] Install: `pip install mcp fastmcp`
- [ ] Create `mcp_server/server.py`
- [ ] Create `mcp_server/requirements.txt`
- [ ] Test with MCP inspector
- [ ] Add to main README

---

### 1.2 Chroma Memory (Chroma Prize)
**File**: `backend/integrations/chroma_db.py`
```python
import chromadb
from typing import List, Dict
from datetime import datetime

class ChromaMemory:
    def __init__(self):
        self.client = chromadb.Client()
        self.builds_collection = self.client.get_or_create_collection("builds")
        self.chats_collection = self.client.get_or_create_collection("chats")
        self.decisions_collection = self.client.get_or_create_collection("decisions")
    
    def store_build(self, project_id: str, prompt: str, files: Dict[str, str], metadata: Dict):
        """Store build artifacts and context"""
        self.builds_collection.add(
            ids=[project_id],
            documents=[f"{prompt}\n\nFiles: {', '.join(files.keys())}"],
            metadatas=[{
                "project_id": project_id,
                "file_count": len(files),
                "timestamp": datetime.now().isoformat(),
                **metadata
            }]
        )
    
    def store_chat(self, room_id: str, message: str, user: str, role: str):
        """Store chat messages"""
        chat_id = f"{room_id}_{datetime.now().timestamp()}"
        self.chats_collection.add(
            ids=[chat_id],
            documents=[message],
            metadatas={"room_id": room_id, "user": user, "role": role}
        )
    
    def store_decision(self, project_id: str, decision: str, context: str):
        """Store architectural decisions"""
        decision_id = f"{project_id}_{datetime.now().timestamp()}"
        self.decisions_collection.add(
            ids=[decision_id],
            documents=[f"{decision}\n\nContext: {context}"],
            metadatas={"project_id": project_id}
        )
    
    def query_context(self, query: str, n_results: int = 5) -> List[Dict]:
        """Query build history"""
        results = self.builds_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def get_chat_history(self, room_id: str, limit: int = 50) -> List[Dict]:
        """Get recent chat messages"""
        results = self.chats_collection.query(
            query_texts=[""],
            where={"room_id": room_id},
            n_results=limit
        )
        return results
```

**TODO**:
- [ ] Install: `pip install chromadb`
- [ ] Create `backend/integrations/chroma_db.py`
- [ ] Initialize in `backend/main.py`
- [ ] Integrate with build endpoint
- [ ] Add to requirements.txt

---

### 1.3 WebSocket Server (Real-time)
**File**: `backend/websocket_server.py`
```python
from fastapi import FastAPI
from socketio import AsyncServer
import uvicorn

app = FastAPI()
sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Store active rooms
rooms = {}

@sio.on('connect')
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('join_room')
async def join_room(sid, data):
    room_id = data['room_id']
    user = data['user']
    role = data['role']
    
    await sio.enter_room(sid, room_id)
    
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append({"sid": sid, "user": user, "role": role})
    
    await sio.emit('user_joined', {
        "user": user,
        "role": role,
        "users": rooms[room_id]
    }, room=room_id)

@sio.on('send_message')
async def send_message(sid, data):
    room_id = data['room_id']
    message = data['message']
    user = data['user']
    role = data['role']
    
    # Store in Chroma
    from integrations.chroma_db import chroma_memory
    chroma_memory.store_chat(room_id, message, user, role)
    
    # Send to Janitor AI
    from integrations.janitor_ai import janitor_client
    ai_response = await janitor_client.chat(message, role)
    
    # Broadcast to room
    await sio.emit('message', {
        "user": user,
        "role": role,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }, room=room_id)
    
    # Send AI response
    if ai_response:
        await sio.emit('message', {
            "user": "Facilitator AI",
            "role": "Facilitator",
            "message": ai_response,
            "timestamp": datetime.now().isoformat()
        }, room=room_id)

@sio.on('agent_update')
async def agent_update(sid, data):
    """Broadcast agent status updates"""
    await sio.emit('agent_status', data, room=data['project_id'])

@sio.on('build_progress')
async def build_progress(sid, data):
    """Broadcast build progress"""
    await sio.emit('build_update', data, room=data['project_id'])
```

**TODO**:
- [ ] Install: `pip install python-socketio`
- [ ] Create `backend/websocket_server.py`
- [ ] Mount in `backend/main.py`
- [ ] Add to requirements.txt

---

## PHASE 2: Janitor AI Integration (2 hours)

### 2.1 Janitor AI Client
**File**: `backend/integrations/janitor_ai.py`
```python
import httpx
import os

class JanitorAIClient:
    def __init__(self):
        self.endpoint = "https://janitorai.com/hackathon/completions"
        self.api_key = "calhacks2047"
    
    async def chat(self, message: str, role: str = "user") -> str:
        """Send message to Janitor AI JLLM"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint,
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a {role} in a startup collaboration. Provide helpful, role-specific insights."
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ]
                }
            )
            return response.json()['choices'][0]['message']['content']
    
    async def summarize_chat(self, messages: list) -> str:
        """Summarize chat conversation"""
        summary_prompt = "Summarize the following conversation:\n\n" + "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages
        ])
        return await self.chat(summary_prompt, "Facilitator")

janitor_client = JanitorAIClient()
```

**TODO**:
- [ ] Create `backend/integrations/janitor_ai.py`
- [ ] Update `backend/mcp/chat_summarize.py`
- [ ] Test chat endpoint
- [ ] Integrate with WebSocket

---

### 2.2 Complete Chat Endpoint
**File**: `backend/mcp/chat_summarize.py`
```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from integrations.janitor_ai import janitor_client
from integrations.chroma_db import chroma_memory

router = APIRouter()

class ChatMessage(BaseModel):
    room_id: str
    user: str
    role: str
    message: str

class ChatSummaryRequest(BaseModel):
    room_id: str

@router.post("/mcp/chat/send")
async def send_chat_message(msg: ChatMessage):
    """Send a chat message and get AI response"""
    
    # Store in Chroma
    chroma_memory.store_chat(msg.room_id, msg.message, msg.user, msg.role)
    
    # Get AI facilitation
    ai_response = await janitor_client.chat(msg.message, msg.role)
    
    return {
        "success": True,
        "ai_response": ai_response
    }

@router.post("/mcp/chat/summarize")
async def summarize_chat(request: ChatSummaryRequest):
    """Summarize chat history"""
    
    # Get chat history from Chroma
    history = chroma_memory.get_chat_history(request.room_id)
    
    # Summarize with Janitor AI
    summary = await janitor_client.summarize_chat(history)
    
    return {
        "success": True,
        "summary": summary,
        "message_count": len(history)
    }
```

**TODO**:
- [ ] Complete chat_summarize.py
- [ ] Add WebSocket integration
- [ ] Test chat flow

---

## PHASE 3: Agent System (3-4 hours)

### 3.1 Fetch.ai Agent Framework
**File**: `opsx_agents/base_agent.py`
```python
from uagents import Agent, Context, Model
from typing import List, Dict

class TaskRequest(Model):
    task_id: str
    description: str
    context: Dict

class TaskResponse(Model):
    task_id: str
    status: str
    result: Dict

class OPSXAgent:
    def __init__(self, name: str, role: str):
        self.agent = Agent(name=name)
        self.role = role
        self.tasks = []
    
    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Override in subclasses"""
        raise NotImplementedError
    
    def start(self):
        """Start the agent"""
        self.agent.run()
```

**TODO**:
- [ ] Create `opsx_agents/base_agent.py`
- [ ] Install: `pip install uagents`
- [ ] Add to requirements.txt

---

### 3.2 Planner Agent
**File**: `opsx_agents/planner_agent.py`
```python
from base_agent import OPSXAgent, TaskRequest, TaskResponse
from integrations.gemini_code_generator import gemini_generator

class PlannerAgent(OPSXAgent):
    def __init__(self):
        super().__init__("planner", "Planner")
    
    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Break down user prompt into tasks"""
        
        prompt = f"""
        Break down this startup idea into tasks:
        {task.description}
        
        Return JSON:
        {{
            "ui_tasks": ["task1", "task2"],
            "backend_tasks": ["task1", "task2"],
            "deployment_tasks": ["task1"]
        }}
        """
        
        plan = await gemini_generator.generate_plan(prompt)
        
        return TaskResponse(
            task_id=task.task_id,
            status="completed",
            result=plan
        )
```

**TODO**:
- [ ] Create `opsx_agents/planner_agent.py`
- [ ] Test task breakdown

---

### 3.3 Frontend Agent
**File**: `opsx_agents/fe_agent.py`
```python
from base_agent import OPSXAgent, TaskRequest, TaskResponse
from integrations.v0_clean import v0_clean_generator

class FrontendAgent(OPSXAgent):
    def __init__(self):
        super().__init__("frontend", "Frontend Specialist")
    
    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Build UI components with V0"""
        
        files = await v0_clean_generator.generate_full_app(
            project_name=task.context['project_name'],
            user_requirements=task.description,
            pages=task.context.get('pages', ['Home'])
        )
        
        return TaskResponse(
            task_id=task.task_id,
            status="completed",
            result={"files": files}
        )
```

**TODO**:
- [ ] Create `opsx_agents/fe_agent.py`
- [ ] Integrate with V0

---

### 3.4 Backend Agent
**File**: `opsx_agents/be_agent.py`
```python
from base_agent import OPSXAgent, TaskRequest, TaskResponse
from integrations.gemini_code_generator import gemini_generator

class BackendAgent(OPSXAgent):
    def __init__(self):
        super().__init__("backend", "Backend Specialist")
    
    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Build API endpoints"""
        
        api_code = await gemini_generator.generate_api(task.description)
        
        return TaskResponse(
            task_id=task.task_id,
            status="completed",
            result={"api_code": api_code}
        )
```

**TODO**:
- [ ] Create `opsx_agents/be_agent.py`
- [ ] Add API generation to Gemini

---

### 3.5 Orchestrator
**File**: `opsx_agents/orchestrator.py`
```python
from planner_agent import PlannerAgent
from fe_agent import FrontendAgent
from be_agent import BackendAgent
import asyncio

class AgentOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.fe_agent = FrontendAgent()
        self.be_agent = BackendAgent()
    
    async def build_project(self, prompt: str, project_name: str):
        """Orchestrate multi-agent build"""
        
        # 1. Planner breaks down tasks
        plan = await self.planner.process_task(TaskRequest(
            task_id="plan_1",
            description=prompt,
            context={"project_name": project_name}
        ))
        
        # 2. FE and BE agents work in parallel
        fe_task = self.fe_agent.process_task(TaskRequest(
            task_id="fe_1",
            description="\n".join(plan.result['ui_tasks']),
            context={"project_name": project_name}
        ))
        
        be_task = self.be_agent.process_task(TaskRequest(
            task_id="be_1",
            description="\n".join(plan.result['backend_tasks']),
            context={"project_name": project_name}
        ))
        
        fe_result, be_result = await asyncio.gather(fe_task, be_task)
        
        return {
            "plan": plan.result,
            "frontend": fe_result.result,
            "backend": be_result.result
        }

orchestrator = AgentOrchestrator()
```

**TODO**:
- [ ] Create `opsx_agents/orchestrator.py`
- [ ] Add endpoint in backend
- [ ] Test orchestration

---

## PHASE 4: Frontend Components (4-5 hours)

### 4.1 ChatRoom Component
**File**: `frontend/src/components/ChatRoom.tsx`
```tsx
'use client';

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
  user: string;
  role: string;
  message: string;
  timestamp: string;
}

interface ChatRoomProps {
  chatId: string;
  userName: string;
  userRole: string;
}

export function ChatRoom({ chatId, userName, userRole }: ChatRoomProps) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    const socketInstance = io(process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000');
    
    socketInstance.on('connect', () => {
      socketInstance.emit('join_room', { 
        room_id: chatId, 
        user: userName, 
        role: userRole 
      });
    });
    
    socketInstance.on('message', (msg: Message) => {
      setMessages(prev => [...prev, msg]);
    });
    
    setSocket(socketInstance);
    
    return () => {
      socketInstance.disconnect();
    };
  }, [chatId, userName, userRole]);

  const sendMessage = () => {
    if (!newMessage.trim() || !socket) return;
    
    socket.emit('send_message', {
      room_id: chatId,
      user: userName,
      role: userRole,
      message: newMessage
    });
    
    setNewMessage('');
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 p-4">
        {messages.map((msg, i) => (
          <div key={i} className="mb-4">
            <div className="text-sm font-bold">{msg.user} ({msg.role})</div>
            <div className="text-sm">{msg.message}</div>
            <div className="text-xs text-gray-500">{msg.timestamp}</div>
          </div>
        ))}
      </ScrollArea>
      
      <div className="flex gap-2 p-4">
        <Input
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <Button onClick={sendMessage}>Send</Button>
      </div>
    </div>
  );
}
```

**TODO**:
- [ ] Create `frontend/src/components/ChatRoom.tsx`
- [ ] Install socket.io-client
- [ ] Add ScrollArea component
- [ ] Test real-time chat

---

### 4.2 AgentPanel Component
**File**: `frontend/src/components/AgentPanel.tsx`
```tsx
'use client';

import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Agent {
  name: string;
  role: string;
  status: 'idle' | 'working' | 'completed' | 'error';
  currentTask?: string;
  progress?: number;
}

export function AgentPanel({ projectId }: { projectId: string }) {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_WS_URL!);
    
    socket.on('agent_status', (data: Agent) => {
      setAgents(prev => {
        const existing = prev.find(a => a.name === data.name);
        if (existing) {
          return prev.map(a => a.name === data.name ? data : a);
        }
        return [...prev, data];
      });
    });
    
    return () => { socket.disconnect(); };
  }, [projectId]);

  return (
    <div className="grid gap-4">
      {agents.map(agent => (
        <Card key={agent.name}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {agent.role}
              <Badge variant={agent.status === 'completed' ? 'success' : 'default'}>
                {agent.status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {agent.currentTask && (
              <p className="text-sm">{agent.currentTask}</p>
            )}
            {agent.progress !== undefined && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ width: `${agent.progress}%` }}
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

**TODO**:
- [ ] Create `frontend/src/components/AgentPanel.tsx`
- [ ] Add Badge component
- [ ] Test agent updates

---

### 4.3 BranchVisualizer Component
**File**: `frontend/src/components/BranchVisualizer.tsx`
```tsx
'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';

interface Branch {
  name: string;
  commits: number;
  pr_status?: 'open' | 'merged' | 'closed';
  conflicts?: number;
}

export function BranchVisualizer({ projectId }: { projectId: string }) {
  const [branches, setBranches] = useState<Branch[]>([]);

  useEffect(() => {
    loadBranches();
  }, [projectId]);

  const loadBranches = async () => {
    const result = await apiClient.getBranches(projectId);
    if (result.success) {
      setBranches(result.data);
    }
  };

  return (
    <div className="space-y-4">
      {branches.map(branch => (
        <div key={branch.name} className="flex items-center gap-4">
          <div className="flex-1">
            <div className="font-bold">{branch.name}</div>
            <div className="text-sm text-gray-500">
              {branch.commits} commits
            </div>
          </div>
          {branch.pr_status && (
            <Badge variant={branch.pr_status === 'merged' ? 'success' : 'default'}>
              {branch.pr_status}
            </Badge>
          )}
          {branch.conflicts && branch.conflicts > 0 && (
            <Badge variant="destructive">{branch.conflicts} conflicts</Badge>
          )}
        </div>
      ))}
    </div>
  );
}
```

**TODO**:
- [ ] Create `frontend/src/components/BranchVisualizer.tsx`
- [ ] Add getBranches to API client
- [ ] Test visualization

---

### 4.4 ConflictResolver Component
**File**: `frontend/src/components/ConflictResolver.tsx`
```tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/services/api';

interface Conflict {
  file: string;
  line: number;
  ours: string;
  theirs: string;
  suggestion: string;
}

export function ConflictResolver({ repoUrl }: { repoUrl: string }) {
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState(false);

  const scanConflicts = async () => {
    setLoading(true);
    const result = await apiClient.scanConflicts(repoUrl);
    if (result.success) {
      setConflicts(result.data);
    }
    setLoading(false);
  };

  const resolveConflict = async (conflict: Conflict, choice: 'ours' | 'theirs' | 'suggestion') => {
    await apiClient.resolveConflict(repoUrl, conflict.file, conflict.line, choice);
    setConflicts(prev => prev.filter(c => c !== conflict));
  };

  return (
    <div className="space-y-4">
      <Button onClick={scanConflicts} disabled={loading}>
        {loading ? 'Scanning...' : 'Scan for Conflicts'}
      </Button>
      
      {conflicts.map((conflict, i) => (
        <Card key={i}>
          <CardHeader>
            <CardTitle>{conflict.file}:{conflict.line}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div>
                <div className="font-bold">Ours:</div>
                <code>{conflict.ours}</code>
              </div>
              <div>
                <div className="font-bold">Theirs:</div>
                <code>{conflict.theirs}</code>
              </div>
              <div>
                <div className="font-bold">AI Suggestion:</div>
                <code>{conflict.suggestion}</code>
              </div>
              <div className="flex gap-2">
                <Button onClick={() => resolveConflict(conflict, 'ours')}>Use Ours</Button>
                <Button onClick={() => resolveConflict(conflict, 'theirs')}>Use Theirs</Button>
                <Button onClick={() => resolveConflict(conflict, 'suggestion')}>Use AI</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

**TODO**:
- [ ] Create `frontend/src/components/ConflictResolver.tsx`
- [ ] Add conflict endpoints to API
- [ ] Test resolution flow

---

### 4.5 StakeholderDashboard Component
**File**: `frontend/src/components/StakeholderDashboard.tsx`
```tsx
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/services/api';
import { Badge } from '@/components/ui/badge';

interface Stakeholder {
  id: string;
  name: string;
  role: string;
  active: boolean;
  lastSeen?: string;
}

export function StakeholderDashboard({ projectId }: { projectId: string }) {
  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([]);

  useEffect(() => {
    loadStakeholders();
  }, [projectId]);

  const loadStakeholders = async () => {
    const result = await apiClient.getStakeholders(projectId);
    if (result.success) {
      setStakeholders(result.data);
    }
  };

  return (
    <div className="grid gap-4">
      {stakeholders.map(stakeholder => (
        <Card key={stakeholder.id}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {stakeholder.name}
              <Badge variant={stakeholder.active ? 'success' : 'secondary'}>
                {stakeholder.active ? 'Active' : 'Offline'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-500">{stakeholder.role}</div>
            {stakeholder.lastSeen && (
              <div className="text-xs text-gray-400">
                Last seen: {stakeholder.lastSeen}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

**TODO**:
- [ ] Create `frontend/src/components/StakeholderDashboard.tsx`
- [ ] Add stakeholder tracking
- [ ] Test presence updates

---

## PHASE 5: Additional Integrations (2-3 hours)

### 5.1 CodeRabbit Integration
**File**: `backend/integrations/coderabbit_api.py`
```python
import httpx
from typing import Dict

class CodeRabbitClient:
    def __init__(self):
        # CodeRabbit auto-detects GitHub PRs
        pass
    
    async def trigger_review(self, repo_url: str, pr_number: int) -> Dict:
        """Trigger CodeRabbit review on PR"""
        # CodeRabbit watches GitHub webhooks automatically
        # Just create PR and it will review
        return {"status": "CodeRabbit will review automatically"}

coderabbit_client = CodeRabbitClient()
```

**TODO**:
- [ ] Create `backend/integrations/coderabbit_api.py`
- [ ] Set up GitHub webhook for CodeRabbit
- [ ] Test PR reviews

---

### 5.2 Vercel Deployment (Fix)
**File**: `backend/integrations/vercel_api.py` (update)
```python
# Add actual deployment logic
async def deploy_project(self, github_url: str, project_name: str) -> Dict:
    """Actually deploy to Vercel"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Create Vercel project
        create_response = await client.post(
            f"{self.base_url}/projects",
            headers=self.headers,
            json={
                "name": project_name,
                "gitRepository": {
                    "repo": github_url,
                    "type": "github"
                }
            }
        )
        
        if create_response.status_code == 201:
            project = create_response.json()
            
            # Trigger deployment
            deploy_response = await client.post(
                f"{self.base_url}/deployments",
                headers=self.headers,
                json={
                    "name": project_name,
                    "gitSource": {
                        "type": "github",
                        "repo": github_url
                    }
                }
            )
            
            if deploy_response.status_code == 200:
                deployment = deploy_response.json()
                return {
                    "success": True,
                    "url": f"https://{deployment['url']}"
                }
    
    return {"success": False}
```

**TODO**:
- [ ] Fix Vercel deployment
- [ ] Add Vercel token to .env
- [ ] Test actual deployments

---

### 5.3 Conflict Detection (Complete)
**File**: `backend/mcp/conflict_scan.py` (finish)
```python
from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from typing import List

router = APIRouter()

class ConflictScanRequest(BaseModel):
    repo_url: str

class Conflict(BaseModel):
    file: str
    line: int
    ours: str
    theirs: str
    suggestion: str

@router.post("/mcp/conflict/scan")
async def scan_conflicts(request: ConflictScanRequest):
    """Scan repo for merge conflicts"""
    
    # Clone repo and scan for conflicts
    # Use GitPython to detect conflicts
    import git
    import tempfile
    import os
    
    conflicts = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone repo
        repo = git.Repo.clone_from(request.repo_url, tmpdir)
        
        # Check for conflicts
        for item in repo.index.diff(None):
            if item.change_type == 'U':  # Unmerged
                conflicts.append(Conflict(
                    file=item.a_path,
                    line=0,  # Would need to parse file
                    ours="...",
                    theirs="...",
                    suggestion="AI suggestion here"
                ))
    
    return {
        "success": True,
        "conflicts": conflicts,
        "count": len(conflicts)
    }
```

**TODO**:
- [ ] Install GitPython
- [ ] Complete conflict detection
- [ ] Add AI suggestions

---

## TESTING & DEPLOYMENT

### Integration Tests
```bash
# Test MCP server
mcp test

# Test WebSocket
cd frontend && npm run test:ws

# Test agents
cd opsx_agents && python -m pytest

# Test full flow
./scripts/test_full_flow.sh
```

**TODO**:
- [ ] Write integration tests
- [ ] Create test script
- [ ] Test all features

---

## DEMO PREPARATION

### Video Demo (3-5 min)
1. Show one-prompt build
2. Show multiplayer chat with AI
3. Show agents working in parallel
4. Show conflict resolution
5. Show deployed app

### Pitch Deck
- Problem: Building MVPs is slow
- Solution: OPS-X one-prompt platform
- Tech: MCP + Janitor AI + Fetch.ai + Chroma + V0
- Demo: Live build

**TODO**:
- [ ] Record demo video
- [ ] Create pitch deck
- [ ] Prepare live demo

---

## PRIZE ALIGNMENT

**Creao**: MCP server exposing OPS-X tools ✓
**Janitor AI**: Multiplayer chat with JLLM ✓
**Fetch.ai**: Multi-agent orchestration ✓
**Chroma**: Context storage & retrieval ✓
**V0**: UI generation ✓
**GitHub**: VCS integration ✓
**Vercel**: Auto-deployment ✓
**CodeRabbit**: PR reviews ✓

---

## TIMELINE

**Next 12 hours**: Build EVERYTHING above
**Hour 13-14**: Test & debug
**Hour 15**: Demo prep
**Hour 16**: Submit

---

Ready to build ALL OF THIS?

