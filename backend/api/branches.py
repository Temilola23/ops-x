"""
Branches API - GitHub branch management with AI suggestions
Now using PostgreSQL with SQLAlchemy
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import re

from database import get_db
from models import Branch, Project, Stakeholder
from integrations.github_api import github_client
from integrations.gemini_code_generator import GeminiCodeGenerator

router = APIRouter()

# Initialize Gemini for branch name suggestions
gemini_suggester = None
try:
    gemini_suggester = GeminiCodeGenerator()
except Exception as e:
    print(f"WARNING: Gemini not available for branch suggestions: {e}")


class SuggestBranchRequest(BaseModel):
    stakeholder_name: str
    stakeholder_role: str
    project_name: str
    project_description: Optional[str] = None


class CreateBranchRequest(BaseModel):
    stakeholder_id: int
    stakeholder_name: str
    branch_name: str
    github_repo: str  # e.g., "username/repo-name"


@router.post("/projects/{project_id}/branches/suggest")
async def suggest_branch_name(
    project_id: int,
    request: SuggestBranchRequest,
    db: Session = Depends(get_db)
):
    """
    AI-powered branch name suggestion based on stakeholder role
    """
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    if not gemini_suggester:
        # Fallback to simple naming if Gemini not available
        role_prefix = request.stakeholder_role.lower().replace(" ", "-")
        fallback_name = f"{role_prefix}/{request.stakeholder_name.lower().replace(' ', '-')}"
        
        return {
            "success": True,
            "data": {
                "suggested_name": fallback_name,
                "alternatives": [
                    f"feature/{role_prefix}-improvements",
                    f"{role_prefix}/new-features",
                    f"dev/{request.stakeholder_name.lower().replace(' ', '-')}"
                ]
            },
            "error": None
        }
    
    # Use Gemini to suggest branch names
    prompt = f"""Suggest a Git branch name for a team member working on a project.

Project: {request.project_name}
{f'Description: {request.project_description}' if request.project_description else ''}
Team Member: {request.stakeholder_name}
Role: {request.stakeholder_role}

Suggest 3 professional Git branch names following best practices:
- Use lowercase with hyphens
- Include role/type prefix (e.g., feature/, fix/, dev/)
- Be descriptive but concise
- Follow Git conventions

Return ONLY a JSON object like this (no markdown, no explanations):
{{"primary": "branch-name-1", "alternative1": "branch-name-2", "alternative2": "branch-name-3"}}"""

    try:
        response = gemini_suggester.generate_text(prompt)
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group())
            
            return {
                "success": True,
                "data": {
                    "suggested_name": suggestions.get("primary", "dev/feature-branch"),
                    "alternatives": [
                        suggestions.get("alternative1", "feature/improvements"),
                        suggestions.get("alternative2", "dev/new-features")
                    ]
                },
                "error": None
            }
    except Exception as e:
        print(f"Error suggesting branch name with AI: {e}")
    
    # Fallback to simple naming
    role_prefix = request.stakeholder_role.lower().replace(" ", "-")
    fallback_name = f"{role_prefix}/{request.stakeholder_name.lower().replace(' ', '-')}"
    
    return {
        "success": True,
        "data": {
            "suggested_name": fallback_name,
            "alternatives": [
                f"feature/{role_prefix}-improvements",
                f"dev/{request.stakeholder_name.lower().replace(' ', '-')}"
            ]
        },
        "error": None
    }


@router.post("/projects/{project_id}/branches")
async def create_branch(
    project_id: int,
    request: CreateBranchRequest,
    db: Session = Depends(get_db)
):
    """
    Create a GitHub branch for a stakeholder
    """
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    # Verify stakeholder exists
    stakeholder = db.query(Stakeholder).filter(
        Stakeholder.id == request.stakeholder_id,
        Stakeholder.project_id == project_id
    ).first()
    if not stakeholder:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    if not github_client or not github_client.token:
        return {
            "success": False,
            "data": None,
            "error": "GitHub integration not configured"
        }
    
    github_branch_url = None
    
    # Create branch on GitHub
    try:
        # Get the default branch SHA (main/master)
        default_sha = await github_client.get_default_branch_sha(request.github_repo)
        
        if not default_sha:
            return {
                "success": False,
                "data": None,
                "error": "Could not find default branch. Make sure the repo exists and has commits."
            }
        
        # Create new branch from default branch
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{github_client.base_url}/repos/{request.github_repo}/git/refs",
                headers=github_client.headers,
                json={
                    "ref": f"refs/heads/{request.branch_name}",
                    "sha": default_sha
                }
            )
            
            if response.status_code not in [200, 201]:
                error_msg = f"GitHub API error: {response.text}"
                print(f"ERROR creating branch: {error_msg}")
                return {
                    "success": False,
                    "data": None,
                    "error": error_msg
                }
            
            github_branch_url = f"https://github.com/{request.github_repo}/tree/{request.branch_name}"
            print(f"Created GitHub branch: {github_branch_url}")
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to create GitHub branch: {str(e)}"
        }
    
    # Store branch in database
    branch = Branch(
        project_id=project_id,
        stakeholder_id=request.stakeholder_id,
        branch_name=request.branch_name,
        github_url=github_branch_url,
        status="active"
    )
    
    db.add(branch)
    
    # Update stakeholder with branch name
    stakeholder.github_branch = request.branch_name
    
    db.commit()
    db.refresh(branch)
    
    return {
        "success": True,
        "data": {
            "id": branch.id,
            "project_id": branch.project_id,
            "stakeholder_id": branch.stakeholder_id,
            "stakeholder_name": request.stakeholder_name,
            "branch_name": branch.branch_name,
            "github_url": branch.github_url,
            "status": branch.status,
            "created_at": branch.created_at.isoformat()
        },
        "error": None
    }


@router.get("/projects/{project_id}/branches")
async def list_branches(project_id: int, db: Session = Depends(get_db)):
    """List all branches for a project"""
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    branches = db.query(Branch).filter(Branch.project_id == project_id).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": b.id,
                "project_id": b.project_id,
                "stakeholder_id": b.stakeholder_id,
                "branch_name": b.branch_name,
                "github_url": b.github_url,
                "status": b.status,
                "created_at": b.created_at.isoformat()
            }
            for b in branches
        ],
        "error": None
    }


@router.get("/projects/{project_id}/branches/{branch_id}")
async def get_branch(
    project_id: int,
    branch_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific branch"""
    
    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.project_id == project_id
    ).first()
    
    if not branch:
        return {
            "success": False,
            "data": None,
            "error": "Branch not found"
        }
    
    return {
        "success": True,
        "data": {
            "id": branch.id,
            "project_id": branch.project_id,
            "stakeholder_id": branch.stakeholder_id,
            "branch_name": branch.branch_name,
            "github_url": branch.github_url,
            "status": branch.status,
            "created_at": branch.created_at.isoformat()
        },
        "error": None
    }


@router.delete("/projects/{project_id}/branches/{branch_id}")
async def delete_branch(
    project_id: int,
    branch_id: int,
    db: Session = Depends(get_db)
):
    """Delete a branch (mark as closed, don't delete from GitHub)"""
    
    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.project_id == project_id
    ).first()
    
    if not branch:
        return {
            "success": False,
            "data": None,
            "error": "Branch not found"
        }
    
    # Mark as closed instead of deleting
    branch.status = "closed"
    db.commit()
    
    return {
        "success": True,
        "data": {"closed": branch_id},
        "error": None
    }
