# Cal Hacks 12.0 Sponsor Integration Guide

## 🎯 Priority Sponsor Integrations for OPS-X

### 1. **Creao AI** - $4,000 Prize Pool
**Prize Tracks:**
- Best Real-World Productivity Tool: $1,750
- Smartest AI Agent Prize: $1,250  
- Best Designed Web App: $1,000

**Integration Requirements:**
- Must include at least one custom MCP integration
- Register custom APIs on Creao platform
- Use Creao for vibe-coding the initial MVP

**OPS-X Implementation:**
- `MCP.creao.build_app` - Core build endpoint
- Custom MCP for each agent interaction
- API registration for all OPS-X endpoints

### 2. **Janitor AI** - $200K Internship + AirPods Max
**Challenge:** Build a Multiplayer AI Chat Experience

**Key Requirements:**
- Real-time multiplayer chat room
- Coherent multi-user conversations
- Creative prompting solution
- JLLM API: `https://janitorai.com/hackathon/completions`
- 25K context length

**OPS-X Implementation:**
- Multiplayer refinement room with role-based chat
- Context management with Chroma summarization
- Role-aware prompting (Founder, FE, BE, Investor)

### 3. **Fetch.ai** - $5,000 Prize Pool + Internships
**Prize Tracks:**
- Best Use of Fetch.ai: $2,500
- Best Deployment of Agentverse: $1,500
- Most Viral ASI:One Personal AI: $1,000

**Requirements:**
- Register agents on Agentverse
- Implement Chat Protocol
- Integrate Claude as reasoning engine
- Make agents discoverable via ASI:One

**OPS-X Implementation:**
- Deploy all specialized agents on Agentverse
- Chat protocol for each agent type
- ASI:One integration for agent discovery

### 4. **Postman** - iPad + Electronics
**Requirements:**
- Best Use of Postman
- Create replayable workflows
- Visual orchestration

**OPS-X Implementation:**
- `MCP.postman.export_flow` endpoint
- Complete Flow documentation
- Action URL for judges

### 5. **CodeRabbit** - Ray-Ban Meta AI Glasses
**Requirements:**
- Best Use of CodeRabbit AI
- Automated code reviews

**OPS-X Implementation:**
- PR review integration
- Conflict detection enhancement

### 6. **Chroma** - $200 per team member
**Requirements:**
- Best AI application using Chroma
- Vector storage implementation

**OPS-X Implementation:**
- Context management system
- Role-based memory stores
- Artifact tracking

### 7. **Deepgram** - TTS Integration
**OPS-X Implementation:**
- 60-second pitch audio generation
- Voice output for demos

## 📋 Technical Integration Checklist

### Creao Integration
```python
# backend/integrations/creao_api.py
- [ ] Creao API authentication
- [ ] Build endpoint implementation
- [ ] Component schema mapping
- [ ] MCP registration
```

### Janitor AI Integration
```python
# backend/integrations/janitor_api.py
- [ ] JLLM API client
- [ ] Context management (25K limit)
- [ ] Role-based prompting
- [ ] Multi-user state tracking
```

### Fetch.ai Integration
```python
# opsx_agents/*.py
- [ ] uAgent framework setup
- [ ] Chat protocol implementation
- [ ] Agentverse registration
- [ ] ASI:One compatibility
```

### Mastra Integration (TypeScript Agent)
```typescript
// frontend/src/hooks/useMastra.ts
- [ ] Mastra framework integration
- [ ] TypeScript agent for frontend
- [ ] Agent-to-agent communication
```

## 🏆 Prize Optimization Strategy

1. **Primary Targets** (Direct alignment with OPS-X):
   - Creao: Smartest AI Agent Prize
   - Janitor AI: Multiplayer Chat
   - Fetch.ai: Best Use + Best Deployment
   - Postman: Workflow visualization

2. **Secondary Targets** (Natural fit):
   - CodeRabbit: PR reviews
   - Chroma: Vector DB
   - YC Track: Startup narrative

3. **Stretch Goals**:
   - MCP Automation Prize
   - Best Beginner Hack (if team qualifies)

## 🔑 API Keys and Endpoints

```env
# Add to .env
CREAO_INVITATION_CODE=<from-registration>
JANITOR_API_ENDPOINT=https://janitorai.com/hackathon/completions
JANITOR_API_KEY=<from-slack>
FETCHAI_CODE_CALHACK2025=<for-ASI:One-Pro>
FETCHAI_CODE_CALHACK2025AV=<for-Agentverse-Premium>
```

## 📅 Workshop Schedule

### Friday, October 24
- 20:00 PDT - Fetch.ai Workshop
- 20:00 PDT - Creao Workshop

### Saturday, October 25
- 10:00 PDT - Creao API/Agent Workshop
- 13:00 PDT - Fetch.ai Networking
- 15:00 PDT - Creao Networking & 'Yoga'

## 🚀 Quick Start Commands

```bash
# Register with Creao
make creao-register

# Deploy to Agentverse
make deploy-agents

# Test Janitor integration
make test-multiplayer

# Export Postman flow
make export-flow
```

## 📝 Submission Requirements

### Creao
- [ ] Submit via official Creao Challenge Form
- [ ] Include custom MCP documentation
- [ ] Clear problem statement

### Fetch.ai
- [ ] All agents under "Innovation Lab" category
- [ ] Include badges in README:
  ```markdown
  ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
  ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
  ```
- [ ] 3-5 minute demo video

### General
- [ ] Public GitHub repository
- [ ] Comprehensive README
- [ ] Working demo
- [ ] Prize category selection
