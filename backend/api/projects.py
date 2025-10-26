"""
Projects API - REST endpoints for project management
Now using PostgreSQL with SQLAlchemy
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from database import get_db
from models import Project, User, Stakeholder, Branch
from integrations.chroma_client import chroma_search, generate_embedding
from integrations.github_api import github_client

router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str
    prompt: str
    user_email: Optional[str] = "demo@opsx.dev"  # For MVP, default user


class V0File(BaseModel):
    name: str
    content: str


class SaveToGitHubRequest(BaseModel):
    project_id: int
    project_name: str
    files: List[V0File]
    v0_chat_id: Optional[str] = None
    v0_preview_url: Optional[str] = None
    description: Optional[str] = "Generated with v0.dev"


class ProjectResponse(BaseModel):
    id: int
    name: str
    prompt: str
    status: str
    github_repo: Optional[str] = None
    app_url: Optional[str] = None
    v0_chat_id: Optional[str] = None
    v0_preview_url: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


@router.post("/projects")
async def create_project(request: CreateProjectRequest, db: Session = Depends(get_db)):
    """Create a new project"""
    
    # Get or create anonymous user (session-based)
    # For MVP: Users don't need accounts to generate apps!
    # They only sign up when they want to invite team members
    user = db.query(User).filter(User.email == request.user_email).first()
    if not user:
        # Create anonymous user with session_id
        import uuid
        session_id = f"anon_{uuid.uuid4().hex[:16]}"
        user = User(
            session_id=session_id,
            email=request.user_email  # Store email for potential signup later
        )
        db.add(user)
        db.flush()  # Get user ID
    
    # Create project
    project = Project(
        name=request.name,
        prompt=request.prompt,
        status="pending",
        owner_id=user.id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "success": True,
        "data": {
            "id": project.id,
            "name": project.name,
            "prompt": project.prompt,
            "status": project.status,
            "github_repo": project.github_repo,
            "app_url": project.app_url,
            "owner_id": project.owner_id,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        },
        "error": None
    }


@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "prompt": p.prompt,
                "status": p.status,
                "github_repo": p.github_repo,
                "app_url": p.app_url,
                "owner_id": p.owner_id,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            }
            for p in projects
        ],
        "error": None
    }


@router.get("/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    return {
        "success": True,
        "data": {
            "id": project.id,
            "name": project.name,
            "prompt": project.prompt,
            "status": project.status,
            "github_repo": project.github_repo,
            "app_url": project.app_url,
            "v0_chat_id": project.v0_chat_id,
            "v0_preview_url": project.v0_preview_url,
            "owner_id": project.owner_id,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        },
        "error": None
    }


@router.patch("/projects/{project_id}")
async def update_project(project_id: int, updates: dict, db: Session = Depends(get_db)):
    """Update project status/URLs"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    # Update allowed fields
    allowed_fields = ["status", "github_repo", "app_url", "name", "v0_chat_id", "v0_preview_url"]
    for field, value in updates.items():
        if field in allowed_fields and hasattr(project, field):
            setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return {
        "success": True,
        "data": {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "github_repo": project.github_repo,
            "app_url": project.app_url,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        },
        "error": None
    }


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    # Delete Chroma embeddings
    if chroma_search:
        chroma_search.delete_project_embeddings(str(project_id))
    
    # Delete project (cascades to stakeholders, branches, etc.)
    db.delete(project)
    db.commit()
    
    return {
        "success": True,
        "data": {"deleted": project_id},
        "error": None
    }


@router.get("/projects/{project_id}/branches")
async def get_project_branches(project_id: int, db: Session = Depends(get_db)):
    """Get branches for a project"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    return {
        "success": True,
        "data": [
            {
                "id": b.id,
                "branch_name": b.branch_name,
                "github_url": b.github_url,
                "status": b.status,
                "stakeholder_id": b.stakeholder_id,
                "created_at": b.created_at.isoformat()
            }
            for b in project.branches
        ],
        "error": None
    }


@router.get("/projects/{project_id}/agents")
async def get_project_agents(project_id: int, db: Session = Depends(get_db)):
    """Get agents for a project (stub for now)"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    # TODO: Implement agent tracking
    return {
        "success": True,
        "data": [],
        "error": None
    }


@router.post("/projects/save-to-github")
async def save_to_github(request: SaveToGitHubRequest, db: Session = Depends(get_db)):
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
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            return {
                "success": False,
                "error": "Project not found",
                "data": None
            }
        
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
        
        print(f"Repo created: {repo_url}")
        print(f"Pushing {len(request.files)} files to GitHub...")
        
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
        
        print(f"Pushed {len(files_dict)} files successfully")
        
        # 5. Update project in database with v0 metadata
        project.github_repo = repo_url
        project.status = "built"
        project.v0_chat_id = request.v0_chat_id  # Save v0 chat ID for refinements
        project.v0_preview_url = request.v0_preview_url  # Save v0 preview URL
        project.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(project)
        
        print(f"Project saved to GitHub successfully!")
        
        # 6. Return success with repo info
        return {
            "success": True,
            "data": {
                "repo_url": repo_url,
                "repo_full_name": repo_full_name,
                "default_branch": default_branch,
                "files_pushed": len(files_dict),
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "github_repo": project.github_repo,
                    "status": project.status
                }
            },
            "error": None
        }
        
    except Exception as e:
        print(f"Error saving to GitHub: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": f"Failed to save to GitHub: {str(e)}",
            "data": None
        }


@router.post("/projects/{project_id}/codebase")
async def store_codebase(project_id: int, files: Dict[str, str], db: Session = Depends(get_db)):
    """
    Store generated codebase files in Chroma for semantic search
    Note: Files now stored in Chroma, not in-memory
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    if not chroma_search:
        return {
            "success": False,
            "data": None,
            "error": "Chroma search not available"
        }
    
    # Store files in Chroma
    stored_files = []
    for file_path, content in files.items():
        try:
            # Generate embedding
            embedding = generate_embedding(content)
            
            # Store in Chroma
            chroma_id = chroma_search.add_code_file(
                project_id=str(project_id),
                file_path=file_path,
                content=content,
                embedding=embedding
            )
            
            stored_files.append(file_path)
            
        except Exception as e:
            print(f"Error storing {file_path}: {e}")
    
    return {
        "success": True,
        "data": {
            "project_id": project_id,
            "file_count": len(stored_files),
            "files": stored_files
        },
        "error": None
    }


@router.get("/projects/{project_id}/codebase")
async def get_codebase(project_id: int, db: Session = Depends(get_db)):
    """
    Get codebase files from GitHub (not from Chroma)
    Use GitHub API to fetch actual files
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    # TODO: Fetch from GitHub API
    return {
        "success": True,
        "data": {
            "github_repo": project.github_repo,
            "message": "Use GitHub API to fetch files"
        },
        "error": None
    }


@router.get("/projects/{project_id}/codebase/files")
async def list_codebase_files(project_id: int, db: Session = Depends(get_db)):
    """List file structure (from Chroma metadata)"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    if not chroma_search:
        return {
            "success": True,
            "data": [],
            "error": None
        }
    
    # Get file list from Chroma metadata
    try:
        results = chroma_search.collection.get(
            where={"project_id": str(project_id)}
        )
        
        files = [
            {
                "path": meta["file_path"],
                "language": meta.get("language", "unknown"),
                "size": meta.get("size", 0)
            }
            for meta in results["metadatas"]
        ]
        
        return {
            "success": True,
            "data": files,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


@router.post("/projects/{project_id}/search/semantic")
async def semantic_search(
    project_id: int,
    query: str,
    n_results: int = 5,
    db: Session = Depends(get_db)
):
    """
    Semantic code search powered by Chroma
    Find code by meaning, not just text match
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    if not chroma_search:
        return {
            "success": False,
            "data": None,
            "error": "Chroma search not available"
        }
    
    # Generate query embedding
    query_embedding = generate_embedding(query)
    
    # Search in Chroma
    results = chroma_search.search_code(
        query_embedding=query_embedding,
        project_id=str(project_id),
        n_results=n_results
    )
    
    return {
        "success": True,
        "data": {
            "query": query,
            "results": [
                {
                    "file_path": results["metadatas"][i]["file_path"],
                    "snippet": results["documents"][i],
                    "language": results["metadatas"][i].get("language"),
                    "relevance_score": 1 - results["distances"][i]  # Convert distance to similarity
                }
                for i in range(len(results["ids"]))
            ],
            "powered_by": "Chroma DB"
        },
        "error": None
    }


@router.get("/projects/{project_id}/code/latest")
async def get_latest_code(
    project_id: int,
    stakeholder_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch latest code from GitHub for refinement
    
    Returns:
        All files from the GitHub repo, filtered by role permissions if stakeholder_id provided
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "error": "Project not found",
                "data": None
            }
        
        if not project.github_repo:
            return {
                "success": False,
                "error": "Project not yet pushed to GitHub",
                "data": None
            }
        
        # Extract repo full name from GitHub URL
        repo_url = project.github_repo
        if "github.com/" in repo_url:
            repo_full_name = repo_url.split("github.com/")[1].replace(".git", "").strip("/")
        else:
            repo_full_name = repo_url
        
        print(f"Extracting repo: {repo_full_name} from {repo_url}")
        
        # Fetch all files from GitHub
        default_branch = getattr(project, 'default_branch', None) or "main"
        files = await github_client.fetch_repo_files(repo_full_name, default_branch)
        
        # If stakeholder_id provided, filter by permissions
        if stakeholder_id:
            from api.permissions import get_allowed_files
            
            stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
            if stakeholder:
                all_file_paths = list(files.keys())
                allowed_paths = get_allowed_files(stakeholder.role, all_file_paths)
                files = {path: content for path, content in files.items() if path in allowed_paths}
        
        return {
            "success": True,
            "data": {
                "files": files,
                "total_files": len(files),
                "github_repo": project.github_repo,
                "branch": default_branch
            },
            "error": None
        }
        
    except Exception as e:
        print(f"Get latest code error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Failed to fetch code from GitHub",
            "data": None
        }


@router.post("/projects/{project_id}/create-branch-and-pr")
async def create_branch_and_pr(
    project_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Create a new branch with changes and open a PR
    
    Request body:
    {
        "stakeholder_id": int,
        "branch_name": str (optional, auto-generated if not provided),
        "files": {"path": "content", ...},
        "pr_title": str,
        "pr_description": str
    }
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Project not found", "data": None}
        
        if not project.github_repo:
            return {"success": False, "error": "Project not on GitHub yet", "data": None}
        
        # Get stakeholder
        stakeholder_id = request.get("stakeholder_id")
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
        
        # Generate branch name if not provided
        branch_name = request.get("branch_name")
        if not branch_name:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            role_prefix = stakeholder.role.lower().replace(" ", "-") if stakeholder else "update"
            branch_name = f"{role_prefix}-refinement-{timestamp}"
        
        # Extract repo full name
        repo_full_name = project.github_repo.replace("https://github.com/", "").replace(".git", "").strip("/")
        
        # 1. Create branch
        print(f"Creating branch: {branch_name}")
        branch_result = await github_client.create_branch(
            repo_full_name=repo_full_name,
            branch_name=branch_name,
            base_branch=getattr(project, 'default_branch', None) or "main"
        )
        
        if not branch_result.get("success"):
            return {"success": False, "error": f"Failed to create branch: {branch_result.get('error')}", "data": None}
        
        # 2. Push files to new branch
        files_to_push = request.get("files", {})
        print(f"Pushing {len(files_to_push)} files to branch {branch_name}")
        
        push_result = await github_client.push_multiple_files(
            repo_full_name=repo_full_name,
            files=files_to_push,
            commit_message=f"Refinement: {request.get('pr_title', 'Update code')}",
            branch=branch_name
        )
        
        if not push_result.get("success"):
            return {"success": False, "error": "Failed to push files", "data": None}
        
        # 3. Create Pull Request
        pr_title = request.get("pr_title", f"Refinement by {stakeholder.name if stakeholder else 'Team Member'}")
        pr_body = request.get("pr_description", "Code refinement requested through OPS-X platform")
        
        pr_result = await github_client.create_pull_request(
            repo_full_name=repo_full_name,
            title=pr_title,
            body=pr_body,
            head_branch=branch_name,
            base_branch=getattr(project, 'default_branch', None) or "main"
        )
        
        if not pr_result.get("success"):
            return {"success": False, "error": f"Failed to create PR: {pr_result.get('error')}", "data": None}
        
        # 4. Store branch in database
        branch_record = Branch(
            project_id=project_id,
            stakeholder_id=stakeholder_id,
            branch_name=branch_name,
            github_url=pr_result.get("pr_url"),
            status="active"
        )
        db.add(branch_record)
        db.commit()
        db.refresh(branch_record)
        
        return {
            "success": True,
            "data": {
                "branch_name": branch_name,
                "pr_url": pr_result.get("pr_url"),
                "pr_number": pr_result.get("pr_number"),
                "message": "Branch created and PR opened successfully!"
            },
            "error": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"Create branch and PR error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": "Failed to create branch and PR", "data": None}


@router.post("/projects/{project_id}/push-to-main")
async def push_to_main(
    project_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Push changes directly to main branch (for anonymous users or quick updates)
    
    Request body:
    {
        "files": {"path": "content", ...},
        "commit_message": str
    }
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Project not found", "data": None}
        
        if not project.github_repo:
            return {"success": False, "error": "Project not on GitHub yet", "data": None}
        
        # Extract repo full name
        repo_full_name = project.github_repo.replace("https://github.com/", "").replace(".git", "").strip("/")
        
        # Push files to main branch
        files_to_push = request.get("files", {})
        commit_message = request.get("commit_message", "Update via OPS-X")
        
        print(f"Pushing {len(files_to_push)} files to main branch")
        
        push_result = await github_client.push_multiple_files(
            repo_full_name=repo_full_name,
            files=files_to_push,
            commit_message=commit_message,
            branch=getattr(project, 'default_branch', None) or "main"
        )
        
        if push_result.get("success"):
            return {
                "success": True,
                "data": {
                    "github_repo": project.github_repo,
                    "message": "Changes pushed to main branch successfully!"
                },
                "error": None
            }
        else:
            return {"success": False, "error": "Failed to push to main", "data": None}
            
    except Exception as e:
        print(f"Push to main error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": "Failed to push to main", "data": None}
