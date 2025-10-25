# OPS-X: One-Prompt Startup Platform

*A comprehensive plan for Cal Hacks 12.0*

> ### RAW IDEA FROM YOU (exact text)
>
> Okay, so this is the big idea!
>
> I was thinking, what if we did our OPS-X as a multi-user platform? So, this is the thing, right? I was thinking what if we started out as a single creao one prompt thing! Then after that, we kinda provision it and then make the demo that os made accessible on a sorta centralized platform. Then the one who made the demo can now add stakeholders to the project. Now, say for the sake of a scenario we had a frontend engineer and a backend engineer working on this vibe coded project, we want it so the same mvp is available to all the stakeholders and then they can make more specialized requests based on each one of their expert areas  So, for example, if it's a web app, the backend guy can focus on the backend and like probe for ultra specific implemwentations.  Like for example, he might want a particular database instead of another one for some CAP reason or might want to use a particular auth methodology instead of another for some other reason and then he can keep probing the agent to make changes to the codebase based on those! Now, there arises a question: if this is happening simultaneously across different stakeholders, how do we track who made what change, what if a change is a breaking change, and what if there is some conflict? Like some systems diesnt agree with some other system, etc.?? Now, to solve that to an extent, I am thinking we could have like a Version control system (VCS). Now this VCS would kinda mean that when a stakeholder wants to start improving on their part of the product, they would have to like branch off of the main prompt platform, iterate and do their shtuf, and then they can make and merge PRs. And that goes the same for every other stakeholder.
> Also, for each of the stakeholder parts of things, we can use fetch.ai's specialized agents (maybe even consider building our own agents for it so it's like we have specialized agents that will attend only to the backend or frontend, etc)
> Now, for the ideation piece of the puzzle and conflict corrections too, we can have a centralized agent that kinda has context across different branches of the VCS and one can just message that agent to ask questions, double check that the current trajectory of our implementation is non-conflicting, etc.
> And also, there can be a chat room where all the stakeholders can meet and ask questions and ideate and stuff but then in this part of the room our central agent (Janitor AI's) will be there, be able to answer the different questions and then we have to figure out when it will speak, what context it willk refer to, etc! So, we could store context across all chats smartly in our DB (chroma DB), to stay within the 25K context limit, we can use what cursor does that we summarize when we are close to the context window, etc!
>
> And then normally, we have to make it so the different specific agents is able to communicate with our janitor ai agent like their context and allat so janitor ai is up to dte  So it has to intelligently choose what to or not to share and all given the context limit.
> And then we should beb able to backpropagate the contents of the chat back to the specific ai agents based on what is relevant to them so that implementation would be faster going forward.
>
> Then from the main codebase, we can always use some other AI agent to get index the full codebase and then from the full codebase, we can get a transcript to pitch and then from the transcript, use deepgram to get TTS and then we can hook up sora or some video/image generation platform to get slides off of it.
>
> Now, im thinking of how we can even use MCPs to integrate something and allat.
>
> Then we can also use postman for workflows, etc.
>
> Then we also have to figure out how to like deploy our agents to the specific agentverse, and all the other track specific prizes, etc!
>
> I dont know, this just has to work and it has to be crazy and cool.
>
> ETC!

---

## 1) Event context and prize targets

**Event**: Cal Hacks 12.0, Oct 24–26, Palace of Fine Arts, San Francisco.
**Primary sponsors we will integrate**: Creao, Fetch.ai, Postman, Janitor AI, Chroma, Deepgram, CodeRabbit.
**Additional optional integrations**: Groq, Mastra, Toolhouse, Bright Data, LiveKit.

**Prize categories we can realistically hit with one coherent product**

* Creao: Best Real-World Productivity Tool or Smartest AI Agent Prize
* Fetch.ai: Best Use of Fetch.ai, Best Deployment of Agentverse, Most Viral ASI:One Personal AI
* Postman: Best Use of Postman
* Janitor AI: Build a Multiplayer AI Chat Experience
* Chroma: Best AI application using Chroma
* CodeRabbit: Best Use of CodeRabbit AI
* LiveKit, Groq, Bright Data are stretch add-ons if time allows
* YC: Build an Iconic YC Company fits our narrative strongly

---

## 2) OPS-X executive summary

OPS-X is a multi-user, agentic platform that turns a single Creao prompt into a real product with stakeholder collaboration, true Git VCS, multi-user chat refinement, automated code reviews, conflict detection, a replayable Flow, and a YC application pack. It is not a thin wrapper. It uses MCP to expose build, repo, conflict, chat memory, pitch, YC pack, and replay as callable tools for other agents.

---

## 3) Product goals and success metrics

**Goals**

* From one prompt, generate a working MVP in Creao
* Let stakeholders branch, edit with specialist agents, and merge via PRs
* Maintain coherent multi-user chat for ideation and decisions
* Provide provenance, replay, and a YC pack

**Success metrics for the demo**

* End-to-end run finishes in one click with no manual stitching
* At least one PR per stakeholder branch reviewed by CodeRabbit
* Multiplayer chat produces a decision that triggers a repo change
* Postman Action URL replays the pipeline
* YC pack emits a PDF and JSON, plus a 60 second pitch audio

---

## 4) System overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              OPS-X PLATFORM                               │
├──────────────────────────────────────────────────────────────────────────┤
│  Creao One-Prompt UI  →  Creao Build API  →  Deployed MVP URL            │
│             │                     │                   │                  │
│             ▼                     ▼                   ▼                  │
│        MCP.creao.build_app  ◄──────────────  Builder Agent (uAgents)     │
│             │                                                    │       │
│             ├────────► GitHub VCS (branches, PRs, commits) ◄─────┤       │
│             │          REST: blobs, trees, refs, PRs               │     │
│             ▼                                                    ▼       │
│  Stakeholder Portal (invite)        Multiplayer Room (Janitor JLLM)      │
│  FE branch  |  BE branch            Founder, FE, BE, Investor, Facilitator│
│   │           │                     Role-aware summaries in Chroma        │
│   ▼           ▼                     Backprop decisions to agents           │
│  FE Agent   BE Agent                via MCP.chat.summarize_and_index       │
│   │           │                                                            │
│   └─► MCP.repo.patch ──► PRs ──► CodeRabbit reviews ──► MCP.conflict.scan  │
│                                                                            │
│  Fetch.ai Agentverse + ASI:One discovery + MCP server registration         │
│            │                                                               │
│            ▼                                                               │
│         Planner Agent (Claude)   Pitch Agent  → Deepgram TTS               │
│                 │                        │                                  │
│                 ├── Chroma memory        ├── YC JSON+PDF pack               │
│                 ▼                        ▼                                  │
│           Postman Flows replay graph  (Actions URL for judges)             │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 5) Detailed modules

### 5.1 One-prompt build and provisioning

* Input: single natural language prompt in Creao
* Planner Agent (Claude on Fetch.ai) produces 3 scoped specs
* Owner selects one
* `MCP.creao.build_app` calls Creao to generate front end, back end, and DB
* Output: App URL, component and API schema, stored in Chroma
* Postman Flow records the exact order of operations

### 5.2 Stakeholder collaboration with true Git

* Owner invites FE and BE stakeholders
* System creates GitHub branches from default
* FE Agent and BE Agent apply changes via `MCP.repo.patch`
* Each patch creates commits and opens PRs
* CodeRabbit posts automatic reviews on each PR

### 5.3 Multiplayer refinement room

* Janitor AI JLLM powers the shared room
* Roles: Founder, FE, BE, Investor, Facilitator
* Role-tagged messages
* Summaries after each turn are written into Chroma via `MCP.chat.summarize_and_index`
* Facilitator decides when to speak based on rules and prompts Specialists or proposes merges

### 5.4 Conflict detection and merge advice

* `MCP.conflict.scan` compares branches across schema, API contracts, auth, and UI assets
* Returns typed conflicts, files involved, and suggested fix patches
* Central Facilitator proposes resolution and triggers `MCP.repo.patch` if approved

### 5.5 Pitch and YC application pack

* Pitch Agent indexes code summaries and spec
* Produces 60 second script and slides.md
* Deepgram TTS renders pitch.mp3
* `MCP.yc.generate_pack` fills YC field JSON and a single page PDF
* Postman Action URL included as provenance link

### 5.6 Replay and provenance

* `MCP.postman.export_flow` outputs a Flow JSON and deploys an Action URL
* Judges can replay plan → build → branch → chat summarize → repo.patch → conflict.scan → pitch.generate → yc.generate_pack

---

## 6) MCP surface and JSON contracts

**1) `mcp.creao.build_app`**

* Input

```json
{
  "project_id": "opsx_123",
  "spec": {
    "name": "Investor Q&A",
    "entities": [{"name": "Company", "fields": ["ticker","sector","risk"]}],
    "pages": ["Home","Ask","Admin"],
    "requirements": ["Auth: email link", "DB: Postgres"]
  }
}
```

* Output

```json
{
  "app_url": "https://creao.app/p/opsx_123",
  "components": [{"id":"home","type":"page"},{"id":"askForm","type":"component"}],
  "api_schema": [{"path":"/api/ask","method":"POST","input":"Question","output":"Answer"}]
}
```

**2) `mcp.repo.patch`**

* Input

```json
{
  "repo": "org/opsx",
  "branch": "feat-backend-auth-oauth",
  "files": [
    {"path":"api/auth.ts","content":"<diff or full file>","mode":"file"},
    {"path":"config/db.json","content":"{...}","mode":"file"}
  ],
  "commit_message": "Switch auth to OAuth; update DB pool"
}
```

* Output

```json
{
  "commit_sha": "abc123",
  "pr_url": "https://github.com/org/opsx/pull/42",
  "status": "created"
}
```

**3) `mcp.conflict.scan`**

* Input

```json
{
  "repo": "org/opsx",
  "branches": ["feat-backend-auth-oauth","feat-frontend-ui-kit"],
  "focus": ["schema","api","auth","ui"]
}
```

* Output

```json
{
  "conflicts": [
    {"type":"api","files":["api/ask.ts","types/answer.ts"],"suggestion":"Align types: Answer.v2"},
    {"type":"auth","files":["api/auth.ts","ui/Login.tsx"],"suggestion":"Expose OAuth token in FE env"}
  ]
}
```

**4) `mcp.chat.summarize_and_index`**

* Input

```json
{"chat_id":"room_7","role":"Investor","text":"How do we monetize Q&A?"}
```

* Output

```json
{"summary_id":"sum_991","tokens_saved":1350}
```

**5) `mcp.pitch.generate`**

* Input

```json
{"project_id":"opsx_123"}
```

* Output

```json
{"script":"<60s pitch>","slides_md":"# Slide 1\n..."}
```

**6) `mcp.yc.generate_pack`**

* Input

```json
{
  "project_id":"opsx_123",
  "founders":[{"name":"A","bio":"..."},{"name":"B","bio":"..."}],
  "demo_url":"https://creao.app/p/opsx_123",
  "media_url":"https://cdn.opsx/pitch.mp3"
}
```

* Output

```json
{"yc_json":{"company":"OPS-X", "...":"..."}, "yc_pdf_path":"/out/opsx_yc.pdf"}
```

**7) `mcp.postman.export_flow`**

* Input

```json
{"project_id":"opsx_123"}
```

* Output

```json
{"flow_json":{ "...": "postman-flow" }, "action_url":"https://www.postman.com/.../action/opsx-replay"}
```

Implementation choice: hand roll or accelerate with **Composio ToolRouter** to get MCP servers with auth and provider integrations quickly.

---

## 7) Data model

**Project**

* id, name, owner_id, creao_project_id, app_url, default_branch
* spec_doc_id, pitch_doc_id

**Branch**

* name, base_sha, status, author_id
* open PR url, mergeable flag

**Artifact**

* type: spec, flow_json, audio, pdf, transcript, slides
* sha256, created_at, source pointer

**Chroma**

* `project_mem`: specs, component maps, decisions
* `convo_mem`: per role rolling summaries and vector embeddings
* `artifact_mem`: captions and pointers for replay

---

## 8) Flow diagrams per sub-MVP

### Sub-MVP A: Prompt to reproducible MVP

```
┌──────────┐    plan    ┌──────────────┐   build   ┌─────────────┐
│  Creao   │──────────► │ PlannerAgent │ ────────► │ MCP.creao.. │
└────┬─────┘            └──────┬───────┘          └──────┬──────┘
     │                         Chroma write                │
     ▼                                                    ▼
  MVP URL                                     Postman Flow Action
```

### Sub-MVP B: Multiplayer refinement

```
[Founder][FE][BE][Investor] → Janitor JLLM ← Facilitator Agent
                   │                │
                   └─ summarize to Chroma via MCP.chat.summarize_and_index
```

### Sub-MVP C: Branches, PRs, reviews, conflict scan

```
FE Agent ──► MCP.repo.patch ──► GitHub PR ──► CodeRabbit review
BE Agent ──► MCP.repo.patch ──► GitHub PR ──► CodeRabbit review
                      │
               MCP.conflict.scan → suggestions → merge
```

### Sub-MVP D: Pitch and YC pack

```
Pitch Agent → script.md → Deepgram TTS → pitch.mp3
          └→ slides.md → YC.json + YC.pdf
                   + Postman Flow Action URL
```

---

## 9) Tooling and platforms to use

**Core**

* Creao: one prompt build plus custom MCP integration
* Fetch.ai uAgents: Planner, FE Specialist, BE Specialist, Pitch Agent. Publish at least two on Agentverse with chat protocol
* Postman Flows: visual orchestration and Action URL
* Janitor AI JLLM: multiplayer chat with role context
* Chroma: memory for summaries and artifacts
* GitHub REST: branches, blobs, trees, commits, PRs
* CodeRabbit: PR review and comments
* Deepgram: TTS for 60 second pitch

**Optional accelerants**

* Composio: MCP servers and integrations
* Mastra: UI front end agent in TypeScript
* Toolhouse: agent BaaS if we need hosted agent HTTP endpoints
* Groq: low latency summarization during demo
* LiveKit: voice room, if we want an audio first demo

**Team dev environment**

* Cursor Teams or Windsurf Teams for shared AI coding in the repo
* One teammate with Claude Pro or Max to run planning prompts
* GitHub Copilot if your team prefers it for inline completions

---

## 10) Build plan for ~20 hours

**T0–T2**

* Repos, env vars, Postman workspace, Chroma collections

**T2–T6**

* Planner Agent with Claude
* `MCP.creao.build_app` and first end to end build to MVP URL
* Postman Flow skeleton with plan → build → publish

**T6–T9**

* GitHub branch and PR wiring
* `MCP.repo.patch` for file writes and commits
* CodeRabbit review on a test PR

**T9–T12**

* Janitor room wrapper, role tags, summarization into Chroma
* `MCP.chat.summarize_and_index` endpoint

**T12–T15**

* `MCP.conflict.scan` across two feature branches
* Facilitator prompts Specialists to resolve and merge

**T15–T17**

* Pitch Agent, Deepgram TTS, `MCP.yc.generate_pack`
* `MCP.postman.export_flow` updates Action URL with the real run

**T17–T20**

* Polish demo path, record a 45 second fallback clip
* Publish two agents to Agentverse with short READMEs
* Submission docs: links, short README, prize callouts

**Cut lines if needed**

* Skip LiveKit and Groq first
* Keep video simple or use audio only
* Keep conflict scan to API and auth only

---

## 11) Risk controls

* Cache Creao responses and schema for offline fallback
* Limit multiplayer chat to Founder, Facilitator, and one Specialist if load spikes
* Keep repo changes to config files and one API endpoint to reduce merge pain
* Always keep the Postman Flow and YC pack generating even if some branches fail

---

## 12) Deliverables checklist for submission

* Creao project link and app URL
* Public Postman Flow workspace and Action URL
* GitHub repo link with PRs and CodeRabbit review screenshots
* Agentverse links for at least two agents
* Janitor room demo link or recorded snippet
* Pitch audio file and YC pack PDF + JSON
* README that maps features to prize categories

---

## 13) Why this is not a dupe

* Creao covers one prompt to app. OPS-X adds multi-user collaboration with real Git VCS, role-aware multiplayer chat, MCP programmable endpoints, automated reviews, conflict scans, replayable Flows, and a YC pack.
* The MCP surface turns OPS-X into composable infrastructure that other agents can call, not just a single project.

---

## 14) Final recommendation for the dev environment

* **Cursor Teams** for shared coding, repo wide edits, and prompt templates
* **Claude Pro or Max** on at least one seat for planning prompts
* Keep Postman, Chroma, and GitHub tokens ready
* Use a single project .env template for quick teammate onboarding

---

## 15) Project Structure

```
ops-x/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml        # For local development
├── Makefile                  # Common commands
│
├── backend/
│   ├── requirements.txt      # Python dependencies
│   ├── requirements-dev.txt  # Dev dependencies
│   ├── main.py              # FastAPI + MCP endpoint registration
│   ├── config.py            # Configuration management
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── creao_build.py
│   │   ├── repo_patch.py
│   │   ├── conflict_scan.py
│   │   ├── chat_summarize.py
│   │   ├── pitch_generate.py
│   │   ├── yc_pack.py
│   │   └── postman_flow.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── chroma_handler.py
│   │   ├── models.py        # SQLAlchemy/Pydantic models
│   │   └── schemas.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Base class for agents
│   │   ├── planner_agent.py
│   │   ├── frontend_agent.py
│   │   ├── backend_agent.py
│   │   ├── facilitator_agent.py
│   │   └── pitch_agent.py
│   ├── integrations/        # External service integrations
│   │   ├── __init__.py
│   │   ├── creao_api.py
│   │   ├── github_api.py
│   │   ├── coderabbit_api.py
│   │   ├── janitor_api.py
│   │   └── fetchai_api.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── git_api.py
│   │   ├── postman_api.py
│   │   ├── deepgram_api.py
│   │   ├── auth.py          # Authentication utilities
│   │   └── helpers.py
│   └── tests/               # Backend tests
│       ├── __init__.py
│       ├── test_mcp.py
│       ├── test_agents.py
│       ├── test_integrations.py
│       └── test_utils.py
│
├── frontend/
│   ├── package.json         # Frontend dependencies
│   ├── tsconfig.json        # TypeScript config
│   ├── vite.config.ts       # Vite configuration
│   ├── .eslintrc.json       # Linting rules
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx         # Entry point
│   │   ├── components/
│   │   │   ├── ChatRoom.tsx
│   │   │   ├── StakeholderDashboard.tsx
│   │   │   ├── AgentPanel.tsx
│   │   │   ├── BranchVisualizer.tsx
│   │   │   ├── ConflictResolver.tsx
│   │   │   └── CreaoPromptInput.tsx
│   │   ├── hooks/           # Custom React hooks
│   │   │   ├── useWebSocket.ts
│   │   │   └── useAgentStatus.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── auth.ts
│   │   ├── types/           # TypeScript types
│   │   │   └── index.ts
│   │   └── styles/          # CSS/styling
│   │       └── globals.css
│   └── public/
│       ├── index.html
│       └── favicon.ico
│
├── opsx_agents/             # Fetch.ai agents
│   ├── requirements.txt     # uAgents dependencies
│   ├── uagent_config.yaml   # For Fetch.ai deployment
│   ├── base_uagent.py       # Base class
│   ├── planner_uagent.py
│   ├── facilitator_uagent.py
│   ├── frontend_uagent.py
│   ├── backend_uagent.py
│   └── deploy.py            # Deployment script
│
├── mcp_server/              # MCP server implementation
│   ├── server.py            # MCP server setup
│   └── handlers.py          # MCP request handlers
│
├── scripts/                 # Automation scripts
│   ├── setup.sh            # Initial setup
│   ├── deploy.sh           # Deployment script
│   ├── test_e2e.py         # End-to-end tests
│   └── demo_flow.py        # Demo automation
│
├── postman_flows/
│   ├── opsx_flow.json      # Main flow export
│   ├── demo_flow.json      # Demo-specific flow
│   └── templates/          # Flow templates
│       └── base_flow.json
│
├── data/
│   ├── samples/
│   │   ├── demo_prompt.json
│   │   ├── test_branches.json
│   │   └── yc_template.json
│   └── cache/              # For caching API responses
│       └── .gitkeep
│
├── docs/
│   ├── OPS-X_README.md
│   ├── architecture.md
│   ├── api_reference.md    # API documentation
│   ├── deployment.md       # Deployment guide
│   └── demo_script.md      # Demo walkthrough
│
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI pipeline
│       └── deploy.yml      # CD pipeline
│
└── deployment/
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    ├── kubernetes/         # K8s configs if needed
    │   └── manifests.yaml
    └── nginx.conf         # For production

```

### Key Additions:

1. **Testing Infrastructure**
   - `backend/tests/` for comprehensive testing
   - `scripts/test_e2e.py` for end-to-end testing

2. **Configuration Files**
   - `docker-compose.yml` for local development
   - `Makefile` for common commands
   - TypeScript/Vite configs for frontend
   - Python requirements files

3. **Better Organization**
   - `integrations/` separate from `utils/` for cleaner API client code
   - `base_agent.py` and `base_uagent.py` for DRY principles
   - `types/` directory in frontend for TypeScript interfaces

4. **MCP Server**
   - Dedicated `mcp_server/` directory since MCP is core to your architecture

5. **Deployment & CI/CD**
   - GitHub Actions workflows
   - Docker configurations
   - Deployment scripts

6. **Documentation**
   - API reference documentation
   - Deployment guide
   - Demo script for hackathon presentation

7. **Development Tools**
   - `scripts/` directory for automation
   - Cache directory for API response caching (important for demos)
   - `.gitignore` for proper version control

This structure supports both rapid hackathon development and potential post-hackathon scaling. The modular design allows team members to work independently while maintaining clear interfaces between components.