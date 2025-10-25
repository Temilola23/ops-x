# PHASE 1: STAKEHOLDER & BRANCHING SYSTEM

**Status:** Backend Complete, Frontend Pending

---

## WHAT WAS BUILT

### Backend APIs (All Working)

#### **1. Stakeholder Management** (`/api/stakeholders.py`)
Manage team members for each project:

- `POST /api/projects/{project_id}/stakeholders` - Add team member
- `GET /api/projects/{project_id}/stakeholders` - List all stakeholders
- `GET /api/projects/{project_id}/stakeholders/{stakeholder_id}` - Get one
- `PATCH /api/projects/{project_id}/stakeholders/{stakeholder_id}` - Update role/branch
- `DELETE /api/projects/{project_id}/stakeholders/{stakeholder_id}` - Remove

**Roles Supported:**
- Founder
- Frontend
- Backend
- Investor
- Facilitator

#### **2. AI-Powered Branching** (`/api/branches.py`)
Create GitHub branches with AI suggestions:

- `POST /api/projects/{project_id}/branches/suggest` - AI suggests branch names
  - Uses Gemini to suggest 3 professional Git branch names
  - Falls back to simple naming if Gemini unavailable
  
- `POST /api/projects/{project_id}/branches` - Create actual GitHub branch
  - Creates branch on GitHub from main/master
  - Links branch to stakeholder
  - Tracks branch in backend
  
- `GET /api/projects/{project_id}/branches` - List all branches
- `GET /api/projects/{project_id}/branches/{branch_id}` - Get one branch
- `DELETE /api/projects/{project_id}/branches/{branch_id}` - Mark branch as closed

#### **3. Codebase Storage** (`/api/projects.py`)
Store and retrieve generated code:

- `POST /api/projects/{project_id}/codebase` - Store files (auto-called by V0 builder)
- `GET /api/projects/{project_id}/codebase` - Get all files
- `GET /api/projects/{project_id}/codebase/files` - List file structure

**Storage:**
- In-memory (for MVP)
- Will be migrated to Chroma DB later for vector search
- Files stored as `{filename: content}` dict

#### **4. V0 Builder Enhanced** (`/mcp/app_build_v0.py`)
Updated to store generated code:
- Now accepts `project_id` in request
- Automatically stores all generated files in codebase storage
- Returns `project_id` in complete event

---

## HOW TO USE (Backend Testing)

### 1. Start Backend Server
```bash
cd backend
python3 main.py
```

### 2. Create a Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Startup",
    "prompt": "Build a todo app"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "abc-123-xyz",
    "name": "My Startup",
    "status": "pending"
  }
}
```

### 3. Build with V0 (with project_id)
```bash
curl -X POST http://localhost:8000/mcp/app/build/v0/stream \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My Startup",
    "requirements": "Todo app with dark theme",
    "deploy_vercel": true,
    "project_id": "abc-123-xyz"
  }'
```

### 4. Add Stakeholders
```bash
curl -X POST http://localhost:8000/api/projects/abc-123-xyz/stakeholders \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Chen",
    "email": "alice@startup.com",
    "role": "Frontend"
  }'
```

### 5. Get AI Branch Name Suggestion
```bash
curl -X POST http://localhost:8000/api/projects/abc-123-xyz/branches/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "stakeholder_name": "Alice Chen",
    "stakeholder_role": "Frontend",
    "project_name": "My Startup",
    "project_description": "Todo app"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "suggested_name": "frontend/alice-chen",
    "alternatives": [
      "feature/frontend-improvements",
      "dev/alice-chen"
    ]
  }
}
```

### 6. Create GitHub Branch
```bash
curl -X POST http://localhost:8000/api/projects/abc-123-xyz/branches \
  -H "Content-Type: application/json" \
  -d '{
    "stakeholder_id": "stakeholder-id-here",
    "stakeholder_name": "Alice Chen",
    "branch_name": "frontend/alice-chen",
    "github_repo": "Temilola23/my-startup-20250125-123456"
  }'
```

**Note:** Use the actual `repo_name` returned from the V0 build (includes timestamp).

### 7. View Stored Codebase
```bash
# List files
curl http://localhost:8000/api/projects/abc-123-xyz/codebase/files

# Get all files with content
curl http://localhost:8000/api/projects/abc-123-xyz/codebase
```

---

## FRONTEND TASKS (For Your Teammate)

### 1. Update `StakeholderDashboard.tsx`
Replace mock data with real API calls:

```typescript
// In StakeholderDashboard.tsx
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';

export function StakeholderDashboard({ projectId }: { projectId: string }) {
  const [stakeholders, setStakeholders] = useState([]);
  
  useEffect(() => {
    const fetchStakeholders = async () => {
      const response = await apiClient.get(`/api/projects/${projectId}/stakeholders`);
      if (response.data.success) {
        setStakeholders(response.data.data);
      }
    };
    fetchStakeholders();
  }, [projectId]);
  
  // ... rest of component
}
```

### 2. Add "Invite Team Member" Modal
- Button to open modal
- Form with fields: name, email, role (dropdown)
- Call `POST /api/projects/{projectId}/stakeholders`

### 3. Add "Create Branch" Button (per stakeholder)
- Show suggested branch names (call `/branches/suggest`)
- Let user pick or edit branch name
- Call `/branches` to create on GitHub
- Show branch status and GitHub URL

### 4. Build File Structure Viewer (Next Phase)
- Call `/api/projects/{projectId}/codebase/files`
- Display as tree structure
- Click to view file content
- Show who's editing what (later)

### 5. Update `BuildWithPreview.tsx`
Pass `project_id` to V0 streaming request:

```typescript
const buildRequest: V0BuildRequest = {
  project_name: projectName,
  requirements: prompt.trim(),
  deploy_vercel: true,
  project_id: projectId,  // ADD THIS
  spec: {
    pages: ["Home", "Dashboard"],
  }
};
```

---

## TESTING THE FLOW

### End-to-End Test:

1. **User creates project** on landing page
2. **V0 generates code** and pushes to GitHub
3. **Dashboard opens** showing project
4. **User adds stakeholders** (Frontend, Backend devs)
5. **Each stakeholder gets AI-suggested branch name**
6. **Stakeholder clicks "Create Branch"**
7. **GitHub branch created** and linked to stakeholder
8. **User can see file structure** in dashboard
9. **(Next Phase)** Stakeholder can edit files in their branch

---

## GITHUB PUSH STATUS

**Current Status:** Working with timestamps

The GitHub integration:
- Creates unique repo names with timestamps (e.g., `my-app-20250125-123456`)
- Initializes repo with README
- Pushes all V0-generated files
- Returns GitHub URL

**Known Issues:**
- Repo names must be unique (hence timestamps)
- Need valid `GITHUB_TOKEN` in environment

**To Test GitHub Push:**
1. Make sure `GITHUB_TOKEN` is in `scripts/.env`
2. Run V0 build with `deploy_vercel: true`
3. Check terminal logs for "Pushed X files to GitHub!"
4. Visit the `github_url` in response

---

## NEXT PHASE: VCS & CONFLICT DETECTION

Once stakeholders and branching work:

1. **File Ownership Tracking**
   - Track who's editing which files
   - Real-time presence system (WebSockets)

2. **Visual Branch Tree**
   - Show all branches
   - Display commit history
   - Highlight divergences

3. **PR Creation**
   - Implement `/mcp/repo/patch` for commits
   - Create PR via GitHub API
   - Trigger CodeRabbit auto-review

4. **Conflict Detection**
   - Implement `/mcp/conflict/scan`
   - Detect schema conflicts
   - Suggest resolutions

5. **Merge UI**
   - Review changes
   - Resolve conflicts
   - Merge branches

---

## CHROMA DB INTEGRATION (Later)

For now, codebase stored in-memory. Later:

1. Store file embeddings in Chroma
2. Enable semantic search ("find auth logic")
3. Track file changes over time
4. Detect similar code patterns
5. Suggest refactoring opportunities

---

## API DOCUMENTATION

Full API docs at: `http://localhost:8000/docs`

**New Sections:**
- Stakeholders API
- Branches API
- Projects API (enhanced with codebase storage)

---

## SUMMARY

**Backend:** Ready for integration
**Frontend:** Needs UI work
**GitHub:** Working with unique naming
**Next:** VCS workflow + conflict detection

Your frontend engineer can start building the stakeholder UI immediately!

