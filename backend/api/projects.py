"""
Projects API - REST endpoints for project management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.github_api import github_client

router = APIRouter()

# In-memory storage (for MVP - replace with DB later)
projects_db: Dict[str, dict] = {}


class CreateProjectRequest(BaseModel):
    name: str
    prompt: str


class V0File(BaseModel):
    name: str
    content: str


class SaveToGitHubRequest(BaseModel):
    project_id: str
    project_name: str
    files: List[V0File]
    v0_chat_id: Optional[str] = None
    v0_preview_url: Optional[str] = None
    description: Optional[str] = "Generated with v0.dev"


class Project(BaseModel):
    id: str
    name: str
    prompt: str
    status: str = "pending"  # pending, building, built, failed
    repo_url: Optional[str] = None
    app_url: Optional[str] = None
    v0_chat_id: Optional[str] = None
    v0_preview_url: Optional[str] = None
    created_at: str
    updated_at: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    project = {
        "id": project_id,
        "name": request.name,
        "prompt": request.prompt,
        "status": "pending",
        "repo_url": None,
        "app_url": None,
        "created_at": now,
        "updated_at": now,
    }
    
    projects_db[project_id] = project
    
    return {
        "success": True,
        "data": project,
        "error": None
    }


@router.get("/projects")
async def list_projects():
    """List all projects"""
    projects = list(projects_db.values())
    projects.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "success": True,
        "data": projects,
        "error": None
    }


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    if project_id not in projects_db:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    return {
        "success": True,
        "data": projects_db[project_id],
        "error": None
    }


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, updates: dict):
    """Update project status/URLs"""
    if project_id not in projects_db:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    project = projects_db[project_id]
    project.update(updates)
    project["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "data": project,
        "error": None
    }


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in projects_db:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    del projects_db[project_id]
    
    return {
        "success": True,
        "data": {"deleted": project_id},
        "error": None
    }


@router.get("/projects/{project_id}/branches")
async def get_project_branches(project_id: str):
    """Get branches for a project"""
    # For MVP, return empty branches
    return {
        "success": True,
        "data": [],
        "error": None
    }


@router.get("/projects/{project_id}/agents")
async def get_project_agents(project_id: str):
    """Get agents for a project"""
    # For MVP, return empty agents
    return {
        "success": True,
        "data": [],
        "error": None
    }


@router.post("/projects/save-to-github")
async def save_to_github(request: SaveToGitHubRequest):
    """
    Save v0-generated code to GitHub
    
    This endpoint:
    1. Creates a new GitHub repository
    2. Pushes all v0 files to the repo
    3. Updates project with repo URL and v0 metadata
    4. Returns repo URL for frontend to display
    """
    try:
        # Verify project exists
        if request.project_id not in projects_db:
            return {
                "success": False,
                "error": "Project not found",
                "data": None
            }
        
        project = projects_db[request.project_id]
        
        # Sanitize repo name (GitHub requirements)
        repo_name = request.project_name.lower().replace(" ", "-").replace("_", "-")
        # Remove special characters
        repo_name = ''.join(c for c in repo_name if c.isalnum() or c == '-')
        
        print(f"📁 Creating GitHub repo: {repo_name}")
        
        # 1. Create GitHub repository
        repo_result = await github_client.create_repo(
            name=repo_name,
            description=request.description or f"Generated with v0.dev - {request.project_name}",
            private=False  # Public for demo purposes
        )
        
        if not repo_result.get("success"):
            return {
                "success": False,
                "error": repo_result.get("error", "Failed to create GitHub repo"),
                "data": None
            }
        
        repo_url = repo_result["repo_url"]
        repo_full_name = repo_result["repo_name"]
        default_branch = repo_result.get("default_branch", "main")
        
        print(f"✅ Repo created: {repo_url}")
        print(f"⬆️  Pushing {len(request.files)} files to GitHub...")
        
        # 2. Convert v0 files to dict
        files_dict = {file.name: file.content for file in request.files}
        
        # 3. Add a README if not included
        if "README.md" not in files_dict:
            files_dict["README.md"] = f"""# {request.project_name}

Generated with [v0.dev](https://v0.dev) via OPS-X

## Preview

[View Live Preview]({request.v0_preview_url})

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your app.

## Built With

- v0.dev - AI-powered UI generation
- Next.js - React framework
- Tailwind CSS - Styling
- shadcn/ui - Component library

## Generated by OPS-X

This project was created using the One-Prompt Startup Platform.
"""
        
        # 4. Push all files to GitHub
        push_result = await github_client.push_multiple_files(
            repo_full_name=repo_full_name,
            files=files_dict,
            commit_message="Initial commit from v0.dev",
            branch=default_branch
        )
        
        if not push_result.get("success"):
            return {
                "success": False,
                "error": f"Repo created but failed to push files: {push_result.get('error')}",
                "data": {
                    "repo_url": repo_url,
                    "partial": True
                }
            }
        
        print(f"✅ Pushed {len(files_dict)} files successfully")
        
        # 5. Update project in database
        project["repo_url"] = repo_url
        project["v0_chat_id"] = request.v0_chat_id
        project["v0_preview_url"] = request.v0_preview_url
        project["status"] = "built"
        project["default_branch"] = default_branch
        project["updated_at"] = datetime.utcnow().isoformat()
        
        projects_db[request.project_id] = project
        
        print(f"🎉 Project saved to GitHub successfully!")
        
        # 6. Return success with repo info
        return {
            "success": True,
            "data": {
                "repo_url": repo_url,
                "repo_full_name": repo_full_name,
                "default_branch": default_branch,
                "files_pushed": len(files_dict),
                "project": project
            },
            "error": None
        }
        
    except Exception as e:
        print(f"❌ Error saving to GitHub: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": f"Failed to save to GitHub: {str(e)}",
            "data": None
        }

