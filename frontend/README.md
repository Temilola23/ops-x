# OPS-X Frontend

Next.js 14 frontend for the OPS-X One-Prompt Startup Platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: TanStack Query + Zustand
- **Real-time**: Socket.IO Client
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your backend URL
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
src/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Landing page with prompt input
│   ├── dashboard/           # Project dashboard
│   └── chat/                # Multiplayer chat room
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── CreaoPromptInput.tsx # Initial prompt interface
│   ├── ChatRoom.tsx         # Multiplayer chat UI
│   ├── AgentPanel.tsx       # Agent status display
│   ├── BranchVisualizer.tsx # Git branch visualization
│   ├── StakeholderDashboard.tsx # Team management
│   └── ConflictResolver.tsx # Merge conflict UI
├── hooks/                   # Custom React hooks
│   ├── useWebSocket.ts      # WebSocket management
│   ├── useAgentStatus.ts    # Agent status tracking
│   ├── useChatRoom.ts       # Chat room state
│   └── useProject.ts        # Project data
├── services/                # API clients
│   ├── api.ts              # REST API client
│   ├── websocket.ts        # WebSocket service
│   └── auth.ts             # Authentication
├── types/                   # TypeScript types
│   └── index.ts            # Shared type definitions
└── providers/               # React context providers
    └── query-provider.tsx  # TanStack Query setup
```

## Key Features

### 1. One-Prompt Build

- Input a single prompt describing your startup idea
- Connects to Creao API to generate working MVP
- Real-time build progress tracking

### 2. Multiplayer Chat

- Role-based chat (Founder, Frontend, Backend, Investor, Facilitator)
- Real-time messaging via WebSocket
- Janitor AI integration for context-aware facilitation

### 3. Branch Management

- Git-style branch visualization
- PR status tracking
- CodeRabbit review integration

### 4. Agent Dashboard

- Real-time agent status monitoring
- Task progress tracking
- Agentverse integration links

### 5. Conflict Resolution

- Automatic conflict detection
- Smart merge suggestions
- One-click conflict resolution

## API Integration

The frontend connects to the OPS-X backend (FastAPI) via:

### REST API

- Project CRUD operations
- Branch management
- Chat history
- Agent control

### WebSocket

- Real-time chat messages
- Agent status updates
- Build progress
- Conflict notifications

## Environment Variables

| Variable              | Description     | Default                 |
| --------------------- | --------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL`  | WebSocket URL   | `http://localhost:8000` |

## Component Usage

### CreaoPromptInput

```tsx
import { CreaoPromptInput } from "@/components/CreaoPromptInput";

<CreaoPromptInput
  onProjectCreated={(projectId, appUrl) => {
    router.push(`/dashboard/${projectId}`);
  }}
/>;
```

### ChatRoom

```tsx
import { ChatRoom } from "@/components/ChatRoom";

<ChatRoom chatId="room_123" userRole="Frontend" userName="Alice" />;
```

### AgentPanel

```tsx
import { AgentPanel } from "@/components/AgentPanel";

<AgentPanel projectId="proj_123" />;
```

## Customization

### Adding New Components

```bash
# Add shadcn/ui components
npx shadcn@latest add [component-name]
```

### Styling

All components use Tailwind CSS. Global styles are in `src/app/globals.css`.

Theme colors can be customized in `tailwind.config.ts`.

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t opsx-frontend .

# Run container
docker run -p 3000:3000 opsx-frontend
```

## Troubleshooting

### WebSocket Connection Issues

If WebSocket fails to connect:

1. Check backend is running
2. Verify `NEXT_PUBLIC_WS_URL` is correct
3. Check CORS settings in backend

### Build Errors

If build fails:

1. Clear `.next` directory: `rm -rf .next`
2. Delete `node_modules`: `rm -rf node_modules`
3. Reinstall: `npm install`
4. Rebuild: `npm run build`

## Contributing

This is a Cal Hacks 12.0 hackathon project. For questions or contributions, contact the team.

## License

MIT
