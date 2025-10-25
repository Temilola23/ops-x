"""
Branches API - GitHub branch management with AI suggestions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import os

# Import integrations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.github_api import github_client
from integrations.gemini_code_generator import GeminiCodeGenerator

router = APIRouter()

# In-memory storage
branches_db: Dict[str, dict] = {}  # branch_id -> branch
project_branches: Dict[str, List[str]] = {}  # project_id -> [branch_ids]

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
    stakeholder_id: str
    stakeholder_name: str
    branch_name: str
    github_repo: str  # e.g., "username/repo-name"


class Branch(BaseModel):
    id: str
    project_id: str
    stakeholder_id: str
    stakeholder_name: str
    branch_name: str
    github_repo: str
    github_branch_url: Optional[str] = None
    status: str  # active, merged, closed
    created_at: str


@router.post("/projects/{project_id}/branches/suggest")
async def suggest_branch_name(project_id: str, request: SuggestBranchRequest):
    """
    AI-powered branch name suggestion based on stakeholder role
    """
    
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
        
        # Try to parse JSON from response
        import json
        import re
        
        # Extract JSON from response (might have markdown or extra text)
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
async def create_branch(project_id: str, request: CreateBranchRequest):
    """
    Create a GitHub branch for a stakeholder
    """
    
    if not github_client or not github_client.token:
        return {
            "success": False,
            "data": None,
            "error": "GitHub integration not configured"
        }
    
    branch_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
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
            
            branch_data = response.json()
            github_branch_url = f"https://github.com/{request.github_repo}/tree/{request.branch_name}"
            
            print(f"Created GitHub branch: {github_branch_url}")
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to create GitHub branch: {str(e)}"
        }
    
    # Store branch in our DB
    branch = {
        "id": branch_id,
        "project_id": project_id,
        "stakeholder_id": request.stakeholder_id,
        "stakeholder_name": request.stakeholder_name,
        "branch_name": request.branch_name,
        "github_repo": request.github_repo,
        "github_branch_url": github_branch_url,
        "status": "active",
        "created_at": now,
    }
    
    branches_db[branch_id] = branch
    
    # Add to project's branch list
    if project_id not in project_branches:
        project_branches[project_id] = []
    project_branches[project_id].append(branch_id)
    
    # Update stakeholder with branch info (if stakeholders API is loaded)
    try:
        from api.stakeholders import stakeholders_db
        if request.stakeholder_id in stakeholders_db:
            stakeholders_db[request.stakeholder_id]["branch_name"] = request.branch_name
    except Exception:
        pass  # Stakeholders API might not be loaded yet
    
    return {
        "success": True,
        "data": branch,
        "error": None
    }


@router.get("/projects/{project_id}/branches")
async def list_branches(project_id: str):
    """List all branches for a project"""
    
    if project_id not in project_branches:
        return {
            "success": True,
            "data": [],
            "error": None
        }
    
    branch_ids = project_branches[project_id]
    branches = [branches_db[bid] for bid in branch_ids if bid in branches_db]
    
    return {
        "success": True,
        "data": branches,
        "error": None
    }


@router.get("/projects/{project_id}/branches/{branch_id}")
async def get_branch(project_id: str, branch_id: str):
    """Get a specific branch"""
    
    if branch_id not in branches_db:
        return {
            "success": False,
            "data": None,
            "error": "Branch not found"
        }
    
    branch = branches_db[branch_id]
    
    if branch["project_id"] != project_id:
        return {
            "success": False,
            "data": None,
            "error": "Branch not found in this project"
        }
    
    return {
        "success": True,
        "data": branch,
        "error": None
    }


@router.delete("/projects/{project_id}/branches/{branch_id}")
async def delete_branch(project_id: str, branch_id: str):
    """Delete a branch (mark as closed, don't delete from GitHub)"""
    
    if branch_id not in branches_db:
        return {
            "success": False,
            "data": None,
            "error": "Branch not found"
        }
    
    branch = branches_db[branch_id]
    
    if branch["project_id"] != project_id:
        return {
            "success": False,
            "data": None,
            "error": "Branch not found in this project"
        }
    
    # Mark as closed instead of deleting
    branch["status"] = "closed"
    
    return {
        "success": True,
        "data": {"closed": branch_id},
        "error": None
    }

