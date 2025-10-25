# OPS-X Frontend Developer Guide

## Overview

The frontend is now fully scaffolded with Next.js 14, shadcn/ui, and all necessary integrations ready to connect to your backend.

## What's Been Set Up

### ✅ Core Infrastructure

- **Next.js 14** with App Router
- **TypeScript** with strict mode
- **Tailwind CSS** for styling
- **shadcn/ui** component library (13 components installed)
- **TanStack Query** for server state management
- **Socket.IO Client** for real-time features
- **Zustand** for client state (installed but not yet used)

### ✅ Services Layer

- **API Client** (`src/services/api.ts`)

  - All MCP endpoints (Creao, GitHub, Janitor, etc.)
  - Project/Branch/Chat CRUD operations
  - Automatic auth token handling
  - Error interceptors

- **WebSocket Service** (`src/services/websocket.ts`)

  - Auto-reconnection
  - Room join/leave
  - Event pub/sub system
  - Real-time message handling

- **Auth Service** (`src/services/auth.ts`)
  - Login/signup placeholders
  - Token management
  - User session handling

### ✅ Custom Hooks

- `useWebSocket` - WebSocket connection management
- `useAgentStatus` - Real-time agent monitoring
- `useChatRoom` - Chat state with real-time updates
- `useProject` - Project data fetching

### ✅ Components Built

#### Main Feature Components

1. **CreaoPromptInput** - One-prompt build interface
2. **ChatRoom** - Multiplayer chat with role badges
3. **AgentPanel** - Real-time agent status display
4. **BranchVisualizer** - Git-style branch tree
5. **StakeholderDashboard** - Team management
6. **ConflictResolver** - Merge conflict UI with suggestions

#### UI Components (shadcn/ui)

- Button, Input, Textarea, Label, Select
- Card, Badge, Avatar, Separator
- Dialog, Tabs, ScrollArea
- Sonner (Toast notifications)

### ✅ Pages Created

- `/` - Landing page with hero and prompt input
- `/dashboard/[projectId]` - Project dashboard with tabs
- `/chat/[chatId]` - Multiplayer chat room

### ✅ Type Definitions

Complete TypeScript interfaces for:

- Project, Branch, Stakeholder
- ChatMessage, ChatRoom, Agent
- All MCP request/response types
- WebSocket events
- API responses

## Quick Start

```bash
cd frontend

# Install dependencies (already done)
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local with your backend URL
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=http://localhost:8000

# Start dev server
npm run dev

# Open http://localhost:3000
```

## Architecture Flow

```
User Input → Components → Hooks → Services → Backend API
                ↓           ↓
            TanStack    WebSocket
             Query      Events
```

### Example: Building with Creao

1. User fills `CreaoPromptInput`
2. Component calls `apiClient.createProject()`
3. Component calls `apiClient.buildWithCreao()`
4. Backend processes via MCP
5. Component receives response
6. Router navigates to `/dashboard/[projectId]`

### Example: Real-time Chat

1. User enters `/chat/[chatId]` page
2. `useChatRoom` hook auto-connects WebSocket
3. Hook joins room via `wsService.joinRoom(chatId)`
4. User types message
5. Hook calls `apiClient.sendChatMessage()`
6. Backend broadcasts via WebSocket
7. All clients receive via `chat:message` event
8. Hook updates local state
9. UI auto-updates

## Integration Points with Backend

### REST API Endpoints Expected

```typescript
// Projects
GET    /api/projects
GET    /api/projects/:id
POST   /api/projects

// Branches
GET    /api/projects/:id/branches
POST   /api/projects/:id/branches

// Chat
GET    /api/projects/:id/chats
GET    /api/chats/:id/messages
POST   /api/chats/:id/messages

// Agents
GET    /api/projects/:id/agents
POST   /api/agents/:id/trigger

// MCP Endpoints
POST   /mcp/creao/build
POST   /mcp/repo/patch
POST   /mcp/conflict/scan
POST   /mcp/chat/summarize
POST   /mcp/pitch/generate
POST   /mcp/yc/pack
POST   /mcp/postman/export
```

### WebSocket Events

**Client → Server:**

- `join_room` - Join a chat room
- `leave_room` - Leave a chat room
- `chat:message` - Send a message

**Server → Client:**

- `chat:message` - New message received
- `agent:status` - Agent status update
- `branch:update` - Branch changed
- `conflict:detected` - Conflict found
- `build:progress` - Build progress update
- `pr:review` - PR review posted

## Key Files to Know

### Entry Points

- `src/app/page.tsx` - Landing page
- `src/app/layout.tsx` - Root layout with providers

### Core Services

- `src/services/api.ts` - Main API client
- `src/services/websocket.ts` - WebSocket manager

### Main Components

- `src/components/CreaoPromptInput.tsx` - Start here for demo
- `src/components/ChatRoom.tsx` - Multiplayer chat
- `src/components/AgentPanel.tsx` - Agent monitoring

### Type Definitions

- `src/types/index.ts` - All TypeScript interfaces

## Development Workflow

### Adding a New Feature

1. **Define Types** (if needed)

   ```typescript
   // src/types/index.ts
   export interface MyNewFeature {
     id: string;
     name: string;
   }
   ```

2. **Add API Method**

   ```typescript
   // src/services/api.ts
   async getMyFeature(id: string): Promise<ApiResponse<MyNewFeature>> {
     const { data } = await this.client.get(`/api/features/${id}`);
     return data;
   }
   ```

3. **Create Hook** (optional)

   ```typescript
   // src/hooks/useMyFeature.ts
   export function useMyFeature(id: string) {
     return useQuery({
       queryKey: ["feature", id],
       queryFn: () => apiClient.getMyFeature(id),
     });
   }
   ```

4. **Build Component**
   ```tsx
   // src/components/MyFeature.tsx
   export function MyFeature({ id }: { id: string }) {
     const { data } = useMyFeature(id);
     return <div>{data?.name}</div>;
   }
   ```

### Adding shadcn/ui Components

```bash
# See available components
npx shadcn@latest add

# Add specific component
npx shadcn@latest add dropdown-menu
```

## Testing the Frontend

### Manual Testing Checklist

1. **Landing Page**

   - [ ] Page loads without errors
   - [ ] "Start Building" button shows prompt input
   - [ ] Form validates empty inputs

2. **Prompt Submission**

   - [ ] Creates project in backend
   - [ ] Shows loading state
   - [ ] Redirects to dashboard on success
   - [ ] Shows error toast on failure

3. **Dashboard**

   - [ ] Loads project data
   - [ ] Shows agent panel
   - [ ] Branch visualizer displays branches
   - [ ] Team tab shows stakeholders

4. **Chat Room**
   - [ ] WebSocket connects
   - [ ] Messages send/receive in real-time
   - [ ] Role badges display correctly
   - [ ] Auto-scrolls to new messages

### Common Issues & Fixes

#### CORS Errors

```python
# In your backend main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### WebSocket Not Connecting

1. Check backend WebSocket server is running
2. Verify `NEXT_PUBLIC_WS_URL` in `.env.local`
3. Check browser console for connection errors

#### 404 on API Calls

1. Verify backend is running on correct port
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure API endpoints match frontend expectations

## Next Steps

### Immediate (for Hackathon)

1. **Start Backend** - Make sure FastAPI server runs
2. **Test Integration** - Try creating a project end-to-end
3. **Connect Creao** - Implement actual Creao API calls
4. **Add Auth** - Implement real authentication
5. **WebSocket Events** - Connect all real-time features

### Polish

1. Add loading skeletons
2. Better error handling/messages
3. Responsive design tweaks
4. Dark mode refinements
5. Animation improvements

### Optional Enhancements

1. **Project List Page** - Show all user projects
2. **Settings Page** - User preferences
3. **Onboarding Flow** - Tutorial for new users
4. **Keyboard Shortcuts** - Power user features
5. **Export Features** - Download pitch deck, YC pack

## Sponsor Integration Notes

### Creao

- `CreaoPromptInput` component handles this
- Calls `/mcp/creao/build` endpoint
- Displays app URL on completion

### Janitor AI

- `ChatRoom` component ready for JLLM integration
- Backend should call Janitor API when facilitator speaks
- 25K context window management in backend

### Fetch.ai

- `AgentPanel` shows agents deployed on Agentverse
- Links to Agentverse URLs when available
- Real-time status updates via WebSocket

### Postman

- Export flow feature in backend
- Could add UI button to trigger export
- Display replay Action URL

### CodeRabbit

- PR reviews show in `BranchVisualizer`
- External links to GitHub PRs
- Review status badges

## Tips for Demo

1. **Pre-populate Data** - Have sample projects ready
2. **Mock Slow Operations** - Add fake delays for dramatic effect
3. **Show Multiple Roles** - Open chat in multiple browser windows
4. **Prepare Fallback** - Record video if live demo fails
5. **Highlight Integrations** - Point out each sponsor's tech

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query/latest)
- [Socket.IO Client](https://socket.io/docs/v4/client-api/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## Need Help?

Check the main README at `/docs/OPS-X_README.md` for architecture overview.

Good luck at Cal Hacks! 🚀
