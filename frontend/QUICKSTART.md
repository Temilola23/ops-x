# Frontend Quick Start 

## Get Running in 3 Steps

```bash
# 1. Setup environment
cp .env.local.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000

# 2. Start dev server
npm run dev

# 3. Open http://localhost:3000
```

## What You Have

### Pages

- `/` - Landing + prompt input
- `/dashboard/[projectId]` - Project dashboard
- `/chat/[chatId]` - Team chat room

### Components

-  CreaoPromptInput - One-prompt build interface
-  ChatRoom - Multiplayer chat with roles
-  AgentPanel - Real-time agent status
-  BranchVisualizer - Git-style branches
-  StakeholderDashboard - Team management
-  ConflictResolver - Merge conflict UI

### Services

-  API Client - All backend endpoints
-  WebSocket - Real-time events
-  Auth - Token management

### Hooks

-  useWebSocket - WS connection
-  useAgentStatus - Agent monitoring
-  useChatRoom - Chat state
-  useProject - Project data

## Backend Integration Points

Your backend needs these endpoints:

**REST:**

```
POST /mcp/creao/build        - Build with Creao
POST /mcp/repo/patch         - Git operations
POST /mcp/conflict/scan      - Detect conflicts
POST /api/projects           - Create project
GET  /api/projects/:id       - Get project
GET  /api/projects/:id/branches
GET  /api/projects/:id/agents
GET  /api/chats/:id/messages
POST /api/chats/:id/messages
```

**WebSocket Events:**

```
Server → Client:
- chat:message       - New message
- agent:status       - Agent update
- branch:update      - Branch changed
- conflict:detected  - Conflict found
```

## File Structure

```
src/
├── app/              # Pages (Next.js App Router)
├── components/       # React components
│   └── ui/          # shadcn/ui components
├── hooks/           # Custom hooks
├── services/        # API clients
├── types/           # TypeScript types
└── providers/       # React providers
```

## Common Tasks

### Add UI Component

```bash
npx shadcn@latest add [component-name]
```

### Add API Endpoint

```typescript
// src/services/api.ts
async myNewEndpoint() {
  const { data } = await this.client.get('/api/my-endpoint');
  return data;
}
```

### Create New Page

```typescript
// src/app/my-page/page.tsx
export default function MyPage() {
  return <div>My Page</div>;
}
```

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Socket.IO Client

## Need Help?

- Full guide: `/docs/frontend_guide.md`
- Architecture: `/docs/architecture.md`
- Main README: `/README.md`
