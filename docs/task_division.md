# OPS-X Task Division Strategy

## 🎯 Critical Path (Must be done first)
Both team members should collaborate on these in the first 2 hours:

1. **Environment Setup** (30 min)
   - Copy `.env.example` to `.env`
   - Get API keys from Slack/registration:
     - Creao invitation code
     - Janitor AI API key
     - Fetch.ai codes (CalHack2025, CalHack2025AV)
   - Run `make setup`

2. **Basic Creao Integration** (1.5 hours)
   - Register on Creao platform
   - Create basic "Hello World" MCP
   - Test API connection
   - This unblocks everything else!

---

## 👤 Person A: Backend & Integration Specialist
**Branch**: `feat/backend-integrations`

### Phase 1: Core MCP Implementation (Hours 2-6)
```
backend/mcp/
├── creao_build.py       # PRIORITY 1: Implement Creao build endpoint
├── repo_patch.py        # PRIORITY 2: GitHub integration
├── chat_summarize.py    # PRIORITY 3: Janitor AI integration
└── conflict_scan.py     # PRIORITY 4: Conflict detection
```

### Phase 2: External Integrations (Hours 6-10)
```
backend/integrations/
├── creao_api.py         # Creao API client
├── janitor_api.py       # Janitor JLLM (25K context)
├── github_api.py        # GitHub REST API
└── coderabbit_api.py    # PR reviews
```

### Phase 3: Agents & Database (Hours 10-14)
```
backend/agents/
├── planner_agent.py     # Main orchestrator
└── backend_agent.py     # Backend specialist

backend/db/
├── chroma_handler.py    # Vector storage
└── schemas.py           # Data models
```

### Key Deliverables:
- [ ] Working Creao build from prompt
- [ ] GitHub branch creation and PR submission
- [ ] Janitor AI multiplayer chat backend
- [ ] Chroma context storage

---

## 👤 Person B: Frontend & Agent Deployment Specialist
**Branch**: `feat/frontend-agents`

### Phase 1: UI Foundation (Hours 2-6)
```
frontend/src/components/
├── CreaoPromptInput.tsx    # PRIORITY 1: Input interface
├── ChatRoom.tsx           # PRIORITY 2: Multiplayer chat UI
├── StakeholderDashboard.tsx # PRIORITY 3: Role management
└── BranchVisualizer.tsx   # PRIORITY 4: Git visualization
```

### Phase 2: Fetch.ai Agent Deployment (Hours 6-10)
```
opsx_agents/
├── planner_uagent.py      # Deploy to Agentverse
├── facilitator_uagent.py  # Chat protocol implementation
└── frontend_uagent.py     # Or use Mastra TypeScript
```

**Critical**: Register all agents on Agentverse with chat protocol!

### Phase 3: Services & Integration (Hours 10-14)
```
frontend/src/
├── services/
│   ├── api.ts            # Backend API client
│   └── websocket.ts      # Real-time chat
└── hooks/
    ├── useWebSocket.ts   # WebSocket management
    └── useMastra.ts      # Mastra integration
```

### Key Deliverables:
- [ ] Working UI for prompt input
- [ ] Real-time multiplayer chat interface
- [ ] 2+ agents deployed on Agentverse
- [ ] Frontend connected to backend APIs

---

## 🔄 Sync Points & Handoffs

### T+2 Hours: Initial Sync
- Confirm Creao API working
- Share API endpoint URLs
- Verify environment setup

### T+6 Hours: Integration Check
- Frontend calls backend MCP endpoints
- Test prompt → build flow
- Deploy first agent to Agentverse

### T+10 Hours: Feature Complete
- Full flow working end-to-end
- All agents deployed
- Begin testing & polish

### T+14 Hours: Demo Prep
- Record demo video
- Prepare Postman flow
- Submit to all prize tracks

---

##  Quick Start Commands

### Person A (Backend):
```bash
git checkout -b feat/backend-integrations
cd backend
# Start with creao_build.py
make run-backend
```

### Person B (Frontend):
```bash
git checkout -b feat/frontend-agents  
cd frontend
npm install
# Start with CreaoPromptInput.tsx
make run-frontend
```

---

## 📱 Communication Protocol

1. **Slack Channel**: #team-opsx (create it)
2. **Quick Syncs**: Every 2 hours
3. **Blocker Alert**: Immediate ping if stuck
4. **Shared Doc**: Keep track of API keys/endpoints

---

## 🎯 Prize Focus by Person

### Person A targets:
- Creao: Smartest AI Agent ($1,250)
- CodeRabbit: Best Use (Ray-Bans)
- Chroma: Best AI Application ($200/member)

### Person B targets:
- Janitor AI: Multiplayer Chat ($200K internship)
- Fetch.ai: Best Deployment ($1,500)
- Postman: Best Use (iPad)

---

## ⚡ If Running Behind:

### Must Have (MVP):
1. Creao one-prompt → app
2. Basic multiplayer chat
3. One agent on Agentverse
4. Postman flow export

### Nice to Have:
- Full conflict detection
- All 5 specialized agents
- YC pack generation
- Voice pitch with Deepgram
