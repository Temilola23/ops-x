"""
Projects API - REST endpoints for project management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

router = APIRouter()

# In-memory storage (for MVP - replace with DB later)
projects_db: Dict[str, dict] = {}


class CreateProjectRequest(BaseModel):
    name: str
    prompt: str


class Project(BaseModel):
    id: str
    name: str
    prompt: str
    status: str = "pending"  # pending, building, built, failed
    repo_url: Optional[str] = None
    app_url: Optional[str] = None
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

