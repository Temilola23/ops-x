# OPS-X System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Team    │  │ Projects │  │   Chat   │  │ Profile  │        │
│  │Dashboard │  │Dashboard │  │  Rooms   │  │  Page    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js + Clerk)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Project Refinement Interface                              │ │
│  │  • Load GitHub code → Preview                              │ │
│  │  • Role-based model selector (Fetch.ai powered)            │ │
│  │  • Document ingestion for context                          │ │
│  │  • V0 SDK for iterative refinements                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   API    │  │  GitHub  │  │ CodeRabbit│  │  Fetch.ai│        │
│  │ Endpoints│  │Integration│  │   Auto   │  │  Router  │        │
│  │          │  │          │  │  Review  │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENT LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   V0     │  │  Claude  │  │  Gemini  │  │   JLLM   │        │
│  │(Frontend)│  │(Backend) │  │(General) │  │  (Chat)  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │PostgreSQL│  │  Chroma  │  │  GitHub  │  │  Vercel  │        │
│  │ (Render) │  │   (Vec   │  │  (Code)  │  │ (Deploy) │        │
│  │          │  │  Search) │  │          │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 REFINEMENT FLOW (The Core Feature)

```
USER INITIATES REFINEMENT
         │
         ↓
┌────────────────────────────────────┐
│ 1. Fetch Latest Code from GitHub  │
│    • Get main branch OR            │
│    • Get user's personal branch    │
└────────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ 2. Render Live Preview            │
│    • Same as initial MVP           │
│    • Load in iframe                │
└────────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ 3. User Enters Refinement Request │
│    • Textbox for prompt            │
│    • Optional: Upload docs         │
│    • Select AI model (role-based)  │
└────────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ 4. Fetch.ai Analyzes Request      │
│    • Determines complexity         │
│    • Suggests best AI model        │
│    • Routes to appropriate agent   │
└────────────────────────────────────┘
         │
         ├─────────────┬─────────────┐
         ↓             ↓             ↓
    ┌────────┐   ┌────────┐   ┌────────┐
    │   V0   │   │ Claude │   │ Gemini │
    │Frontend│   │Backend │   │General │
    └────────┘   └────────┘   └────────┘
         │             │             │
         └─────────────┴─────────────┘
                       ↓
┌────────────────────────────────────┐
│ 5. AI Generates Code Changes      │
│    • V0 SDK maintains context      │
│    • Only edits role-allowed files │
└────────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ 6. Create Pull Request            │
│    • Push to user's branch         │
│    • Create PR to main             │
│    • Tag team members              │
└────────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ 7. CodeRabbit Auto-Review         │
│    • Check for breaking changes    │
│    • Analyze code quality          │
│    • Score severity (1-10)         │
└────────────────────────────────────┘
         │
         ├─── Score < 5 (Good) ─────────┐
         │                               ↓
         │                      ┌─────────────────┐
         │                      │ Auto-Merge PR   │
         │                      │ Notify Team     │
         │                      └─────────────────┘
         │
         ├─── Score 5-7 (Medium) ───────┐
         │                               ↓
         │                      ┌─────────────────┐
         │                      │ Flag for Review │
         │                      │ Notify Admin    │
         │                      └─────────────────┘
         │
         └─── Score > 7 (Breaking) ─────┐
                                        ↓
                               ┌─────────────────┐
                               │ Auto Re-Refine  │
                               │ with CodeRabbit │
                               │ feedback        │
                               └─────────────────┘
                                        │
                                        ↓
                               ┌─────────────────┐
                               │ If still broken │
                               │ Flag team +     │
                               │ Admin + Freeze  │
                               └─────────────────┘
```

---

## 📁 FILE-LEVEL ACCESS CONTROL

```
┌──────────────────────────────────────────────┐
│         ROLE-BASED FILE PERMISSIONS          │
└──────────────────────────────────────────────┘

FRONTEND ENGINEER:
  ✅ Can Edit:
    • app/**/*.tsx
    • components/**/*.tsx
    • public/**/*
    • *.css, *.scss
    • middleware.ts (UI-related)

  ❌ Cannot Edit:
    • app/api/**/* (API routes)
    • backend/**/*
    • server.ts, *.config.js

BACKEND ENGINEER:
  ✅ Can Edit:
    • app/api/**/*
    • backend/**/*
    • server.ts
    • *.config.js (backend)
    • database/**/*

  ❌ Cannot Edit:
    • components/**/*.tsx
    • app/**/page.tsx
    • *.css

FULL-STACK / FOUNDER:
  ✅ Can Edit:
    • Everything

INVESTOR / FACILITATOR:
  ✅ Can:
    • View all code
    • Comment on PRs
    • Request changes
  
  ❌ Cannot:
    • Edit code directly
    • Merge PRs
```

---

## 🤖 AI MODEL ROUTING LOGIC

```
┌────────────────────────────────────┐
│    Fetch.ai Model Router           │
└────────────────────────────────────┘
         │
         ↓
   Analyze Request
         │
    ┌────┴────┐
    │         │
    ↓         ↓
Keywords    Role
Detected    Check
    │         │
    └────┬────┘
         ↓
┌─────────────────────────────────────┐
│ Decision Tree:                      │
│                                     │
│ IF role == "Frontend":              │
│   DEFAULT: V0                       │
│   FALLBACK: Gemini                  │
│                                     │
│ IF role == "Backend":               │
│   DEFAULT: Claude                   │
│   FALLBACK: Gemini                  │
│                                     │
│ IF keywords include:                │
│   "UI", "design", "component" → V0  │
│   "API", "database", "auth" → Claude│
│   "general", "refactor" → Gemini    │
│                                     │
│ IF document uploaded:               │
│   Extract requirements → Claude     │
│   (Claude is best for doc analysis) │
└─────────────────────────────────────┘
```

---

## 💬 CHAT ROOM ARCHITECTURE

```
┌────────────────────────────────────┐
│         Chat Room Types            │
└────────────────────────────────────┘

1. PERSONAL CHATS (1-on-1)
   • Direct messages between team members
   • No AI involvement
   • Standard WebSocket or Polling

2. PROJECT ROOMS (Team + JLLM)
   • All stakeholders in a project
   • JLLM AI assistant present
   • Role-aware context
   • Can tag specific members

3. ADMIN ROOM
   • Project owner + Facilitator
   • High-level decisions
   • JLLM provides insights

┌────────────────────────────────────┐
│         JLLM Integration           │
└────────────────────────────────────┘

JLLM Capabilities:
  • Remembers all project context
  • Role-aware responses
  • Can suggest task assignments
  • Summarizes discussions
  • Alerts on blockers

Example:
  User: "@JLLM, who should handle the auth refactor?"
  JLLM: "Based on expertise, I recommend assigning
         this to @BackendEngineer. They handled the
         initial auth implementation and have context."
```

---

## 🗄️ DATABASE SCHEMA (Updated)

```sql
-- Users (Clerk managed)
users
  ├─ id
  ├─ clerk_user_id (unique)
  ├─ email
  ├─ name
  └─ created_at

-- Projects
projects
  ├─ id
  ├─ name
  ├─ owner_id (FK → users)
  ├─ github_repo
  ├─ v0_chat_id (for continuity)
  ├─ default_branch
  └─ created_at

-- Stakeholders (Team Members)
stakeholders
  ├─ id
  ├─ project_id (FK → projects)
  ├─ user_id (FK → users)
  ├─ role (Frontend/Backend/Investor/etc)
  ├─ permissions (JSON: file patterns)
  ├─ preferred_ai_model
  └─ status (active/pending/inactive)

-- Refinements (NEW)
refinements
  ├─ id
  ├─ project_id (FK → projects)
  ├─ stakeholder_id (FK → stakeholders)
  ├─ request_text
  ├─ ai_model_used (V0/Claude/Gemini)
  ├─ files_changed (JSON array)
  ├─ pr_url
  ├─ coderabbit_score (1-10)
  ├─ status (pending/approved/merged/rejected)
  ├─ created_at
  └─ merged_at

-- Chat Rooms (NEW)
chat_rooms
  ├─ id
  ├─ name
  ├─ type (personal/project/admin)
  ├─ project_id (FK → projects, nullable)
  ├─ has_jllm (boolean)
  └─ created_at

-- Chat Messages (NEW)
chat_messages
  ├─ id
  ├─ room_id (FK → chat_rooms)
  ├─ sender_id (FK → users, nullable for JLLM)
  ├─ message_text
  ├─ is_ai (boolean)
  ├─ ai_model (if is_ai)
  └─ created_at

-- Document Uploads (NEW)
documents
  ├─ id
  ├─ refinement_id (FK → refinements)
  ├─ filename
  ├─ file_url (S3 or similar)
  ├─ extracted_requirements (TEXT)
  └─ uploaded_at

-- CodeRabbit Reviews (NEW)
coderabbit_reviews
  ├─ id
  ├─ refinement_id (FK → refinements)
  ├─ pr_url
  ├─ severity_score (1-10)
  ├─ issues_found (JSON array)
  ├─ auto_fixed (boolean)
  ├─ review_summary
  └─ reviewed_at
```

