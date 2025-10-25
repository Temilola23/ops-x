# GitHub Versioning Architecture

## Overview

The OPS-X platform integrates GitHub for version control, allowing users to save v0-generated applications directly to GitHub repositories. This document explains the complete architecture and flow.

## Architecture Decision

### ✅ Backend Handles GitHub Integration

**Why Backend?**

1. **Security**: GitHub API tokens never exposed to client
2. **Centralized Control**: Project metadata managed in one place
3. **Future Scalability**: Easy to add webhooks, CI/CD, advanced Git operations
4. **Consistency**: Single source of truth for project state
5. **Multi-Stakeholder**: Backend can coordinate multiple users pushing to same repo

### Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. BuildWithPreview Component                                       │
│     • User enters project name + prompt                              │
│     • Calls: apiClient.createProject()                               │
│     • Gets back: project_id                                          │
│                                                                       │
│  2. Server Action (v0.ts)                                           │
│     • Calls v0 SDK securely (server-side)                           │
│     • Returns: chatId, previewUrl, files[]                          │
│                                                                       │
│  3. User clicks "Push to GitHub"                                     │
│     • Calls: apiClient.saveToGitHub()                               │
│     • Sends: project_id, files[], v0_chat_id, preview_url          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  API Endpoint: POST /api/projects/save-to-github                    │
│                                                                       │
│  Step 1: Validate project_id exists                                 │
│  Step 2: Sanitize repo name (GitHub requirements)                   │
│  Step 3: Create GitHub repo via github_client.create_repo()         │
│  Step 4: Convert files to dict {path: content}                      │
│  Step 5: Add auto-generated README.md                               │
│  Step 6: Push all files via github_client.push_multiple_files()     │
│  Step 7: Update project in database with repo_url                   │
│  Step 8: Return repo_url to frontend                                │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   GITHUB API (via github_api.py)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  • create_repo(): Creates new public/private repo                   │
│  • push_multiple_files(): Commits all files in one batch           │
│  • create_branch(): For stakeholder refinements (future)           │
│  • create_pull_request(): For conflict resolution (future)         │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Backend API Endpoint

**File**: `backend/api/projects.py`

```python
@router.post("/projects/save-to-github")
async def save_to_github(request: SaveToGitHubRequest):
    """
    Save v0-generated code to GitHub

    Request Body:
    {
        "project_id": "uuid",
        "project_name": "My Startup",
        "files": [
            {"name": "app/page.tsx", "content": "..."},
            {"name": "components/ui/button.tsx", "content": "..."}
        ],
        "v0_chat_id": "v0_chat_xyz",
        "v0_preview_url": "https://v0.dev/chat/xyz/preview",
        "description": "Generated with v0.dev"
    }

    Response:
    {
        "success": true,
        "data": {
            "repo_url": "https://github.com/user/my-startup",
            "repo_full_name": "user/my-startup",
            "default_branch": "main",
            "files_pushed": 12
        }
    }
    """
```

**Key Operations:**

- Validates project exists
- Sanitizes repo name (lowercase, hyphens, no special chars)
- Creates GitHub repo with description
- Auto-generates README.md if not present
- Pushes all files via GitHub API
- Updates project database with repo metadata

### 2. Frontend Integration

**File**: `frontend/src/components/BuildWithPreview.tsx`

**State Management:**

```typescript
const [backendProjectId, setBackendProjectId] = useState<string | null>(null);
const [repoUrl, setRepoUrl] = useState("");
const [isPushingToGitHub, setIsPushingToGitHub] = useState(false);
```

**Build Flow:**

```typescript
// Step 1: Create project in backend
const projectResponse = await apiClient.createProject(projectName, prompt);
setBackendProjectId(projectResponse.data.id);

// Step 2: Generate UI with v0
const result = await createV0Chat(fullPrompt);
setChatId(result.data.chatId);
setFiles(result.data.files);
```

**GitHub Push:**

```typescript
// User clicks "Push to GitHub" button
const handlePushToGitHub = async () => {
  const response = await apiClient.saveToGitHub({
    project_id: backendProjectId,
    project_name: projectName,
    files: files,
    v0_chat_id: chatId,
    v0_preview_url: previewUrl,
  });

  setRepoUrl(response.data.repo_url);
};
```

**UI Features:**

- "Push to GitHub" button appears after v0 generates code
- Button shows loading state during push
- After successful push, button changes to "View on GitHub"
- Clicking "View on GitHub" opens repo in new tab

### 3. GitHub API Client

**File**: `backend/integrations/github_api.py`

**Methods Used:**

- `create_repo()`: Creates new repository
- `push_multiple_files()`: Commits all files in batch
- `create_or_update_file()`: Individual file operations

**Authentication:**

- Uses `GITHUB_TOKEN` from environment variables
- Token should have `repo` scope
- Supports personal access tokens and GitHub Apps

## Environment Setup

### Backend Environment Variables

**File**: `backend/.env` or `scripts/.env`

```bash
GITHUB_TOKEN=ghp_your_github_personal_access_token
```

**How to Get GitHub Token:**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Copy token and add to `.env`

### Frontend Environment Variables

**File**: `frontend/.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
V0_API_KEY=your_v0_api_key
```

## Data Flow

### Project Creation

```json
POST /api/projects
{
  "name": "My Startup",
  "prompt": "Build a todo app with categories"
}

Response:
{
  "success": true,
  "data": {
    "id": "abc-123",
    "name": "My Startup",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GitHub Save

```json
POST /api/projects/save-to-github
{
  "project_id": "abc-123",
  "project_name": "My Startup",
  "files": [
    {
      "name": "app/page.tsx",
      "content": "export default function Page() { ... }"
    },
    {
      "name": "components/ui/button.tsx",
      "content": "export function Button() { ... }"
    }
  ],
  "v0_chat_id": "v0_xyz",
  "v0_preview_url": "https://v0.dev/chat/xyz",
  "description": "Generated with v0.dev"
}

Response:
{
  "success": true,
  "data": {
    "repo_url": "https://github.com/user/my-startup",
    "repo_full_name": "user/my-startup",
    "default_branch": "main",
    "files_pushed": 12,
    "project": {
      "id": "abc-123",
      "name": "My Startup",
      "status": "built",
      "repo_url": "https://github.com/user/my-startup",
      "v0_chat_id": "v0_xyz",
      "v0_preview_url": "https://v0.dev/chat/xyz"
    }
  }
}
```

## Future Enhancements

### Multi-Stakeholder Collaboration

When stakeholders refine the app:

1. **Frontend**: User clicks "Refine" with new prompt
2. **v0**: Generates updated code
3. **Backend**:
   - Create new branch: `stakeholder-1-refinement`
   - Push updated files to branch
   - Create Pull Request to `main`
4. **Frontend**: Show PR link for review/merge

**API Endpoints (Future):**

```python
POST /api/projects/{project_id}/refinements
POST /api/projects/{project_id}/branches
POST /api/projects/{project_id}/pull-requests
```

### Conflict Resolution

When multiple stakeholders make changes:

1. **Backend**: Detect file conflicts via `mcp.conflict.scan`
2. **AI Resolution**: Janitor AI suggests merge strategies
3. **GitHub**: Create conflict resolution branch
4. **PR**: Open PR with resolved conflicts

### Continuous Deployment

**Future Integration:**

- Push to GitHub triggers Vercel deployment
- Store `app_url` from Vercel in project
- Display live app link to users

## Testing

### Manual Test Flow

1. **Start Backend**:

   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow**:
   - Open http://localhost:3000
   - Enter project name: "Test App"
   - Enter prompt: "Build a simple todo app"
   - Click "Build MVP"
   - Wait for v0 to generate code
   - Click "Push to GitHub"
   - Verify repo created on GitHub
   - Click "View on GitHub"

### API Testing (curl)

```bash
# 1. Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "prompt": "Build a todo app"
  }'

# Response: {"success": true, "data": {"id": "abc-123", ...}}

# 2. Save to GitHub
curl -X POST http://localhost:8000/api/projects/save-to-github \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "abc-123",
    "project_name": "Test Project",
    "files": [
      {
        "name": "README.md",
        "content": "# Test Project"
      }
    ],
    "description": "Test project"
  }'

# Response: {"success": true, "data": {"repo_url": "...", ...}}
```

## Error Handling

### Common Errors

**1. Missing GitHub Token**

```json
{
  "success": false,
  "error": "Failed to create GitHub repo: 401 Unauthorized"
}
```

**Solution**: Add `GITHUB_TOKEN` to backend `.env`

**2. Repository Already Exists**

```json
{
  "success": false,
  "error": "Failed to create repo: repository already exists"
}
```

**Solution**: Choose different project name or delete existing repo

**3. Rate Limit Exceeded**

```json
{
  "success": false,
  "error": "Failed to create repo: 403 Forbidden (rate limit)"
}
```

**Solution**: Wait or use authenticated requests (already done)

**4. Invalid Token Permissions**

```json
{
  "success": false,
  "error": "Failed to create repo: insufficient permissions"
}
```

**Solution**: Regenerate token with `repo` scope

## Security Considerations

### ✅ Best Practices Implemented

1. **Token Security**:

   - GitHub token stored server-side only
   - Never exposed to client
   - Loaded from environment variables

2. **API Authentication**:

   - Future: Add JWT auth to `/api/projects/*` endpoints
   - Verify users can only push to their own repos

3. **Input Validation**:

   - Sanitize repo names (remove special chars)
   - Validate project_id exists
   - Check file content length limits

4. **Error Messages**:
   - Don't expose sensitive info in errors
   - Log full errors server-side
   - Return generic messages to client

### 🔒 Future Security Enhancements

1. **User Authentication**: Add login system
2. **Rate Limiting**: Prevent abuse of GitHub API
3. **Webhook Verification**: Validate GitHub webhooks
4. **OAuth**: Let users connect their own GitHub accounts

## Deployment

### Production Checklist

- [ ] Set `GITHUB_TOKEN` in production environment
- [ ] Configure CORS for production frontend URL
- [ ] Add rate limiting middleware
- [ ] Set up error monitoring (Sentry)
- [ ] Enable HTTPS for API
- [ ] Add health check endpoint
- [ ] Configure log aggregation

### Environment Variables

**Backend (production)**:

```bash
GITHUB_TOKEN=ghp_production_token
BACKEND_PORT=8000
CORS_ORIGINS=https://opsx.app
```

**Frontend (production)**:

```bash
NEXT_PUBLIC_API_URL=https://api.opsx.app
V0_API_KEY=v0_production_key
```

## Summary

### Key Points

✅ **Backend handles GitHub integration** for security and control
✅ **v0 generates code** in Next.js Server Actions (frontend)
✅ **Frontend sends files to backend** for GitHub push
✅ **Backend creates repo and commits files** atomically
✅ **Users see "View on GitHub" button** after successful push
✅ **All credentials stay server-side** (secure)

### API Endpoints Created

- `POST /api/projects` - Create project
- `POST /api/projects/save-to-github` - Save to GitHub
- `GET /api/projects/{project_id}` - Get project details

### Files Modified/Created

**Backend**:

- `backend/api/projects.py` - Added GitHub save endpoint
- `backend/integrations/github_api.py` - Already had all methods

**Frontend**:

- `frontend/src/components/BuildWithPreview.tsx` - Added GitHub push UI
- `frontend/src/services/api.ts` - Added saveToGitHub method

### Next Steps

1. **Test the flow end-to-end**
2. **Add user authentication**
3. **Implement multi-stakeholder branching**
4. **Add Vercel deployment integration**
5. **Create conflict resolution UI**
