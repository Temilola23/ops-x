"""
Stakeholders API - Team member management for projects
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# In-memory storage (for MVP - replace with DB later)
stakeholders_db: Dict[str, dict] = {}  # stakeholder_id -> stakeholder
project_stakeholders: Dict[str, List[str]] = {}  # project_id -> [stakeholder_ids]


class CreateStakeholderRequest(BaseModel):
    name: str
    email: str
    role: str  # Founder, Frontend, Backend, Investor, Facilitator


class Stakeholder(BaseModel):
    id: str
    project_id: str
    name: str
    email: str
    role: str
    branch_name: Optional[str] = None
    created_at: str


@router.post("/projects/{project_id}/stakeholders")
async def add_stakeholder(project_id: str, request: CreateStakeholderRequest):
    """Add a team member to the project"""
    
    stakeholder_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    stakeholder = {
        "id": stakeholder_id,
        "project_id": project_id,
        "name": request.name,
        "email": request.email,
        "role": request.role,
        "branch_name": None,  # Will be set when they create a branch
        "created_at": now,
    }
    
    stakeholders_db[stakeholder_id] = stakeholder
    
    # Add to project's stakeholder list
    if project_id not in project_stakeholders:
        project_stakeholders[project_id] = []
    project_stakeholders[project_id].append(stakeholder_id)
    
    return {
        "success": True,
        "data": stakeholder,
        "error": None
    }


@router.get("/projects/{project_id}/stakeholders")
async def list_stakeholders(project_id: str):
    """List all stakeholders for a project"""
    
    if project_id not in project_stakeholders:
        return {
            "success": True,
            "data": [],
            "error": None
        }
    
    stakeholder_ids = project_stakeholders[project_id]
    stakeholders = [stakeholders_db[sid] for sid in stakeholder_ids if sid in stakeholders_db]
    
    return {
        "success": True,
        "data": stakeholders,
        "error": None
    }


@router.get("/projects/{project_id}/stakeholders/{stakeholder_id}")
async def get_stakeholder(project_id: str, stakeholder_id: str):
    """Get a specific stakeholder"""
    
    if stakeholder_id not in stakeholders_db:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    stakeholder = stakeholders_db[stakeholder_id]
    
    if stakeholder["project_id"] != project_id:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found in this project"
        }
    
    return {
        "success": True,
        "data": stakeholder,
        "error": None
    }


@router.patch("/projects/{project_id}/stakeholders/{stakeholder_id}")
async def update_stakeholder(project_id: str, stakeholder_id: str, updates: dict):
    """Update stakeholder (role, branch, etc.)"""
    
    if stakeholder_id not in stakeholders_db:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    stakeholder = stakeholders_db[stakeholder_id]
    
    if stakeholder["project_id"] != project_id:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found in this project"
        }
    
    stakeholder.update(updates)
    
    return {
        "success": True,
        "data": stakeholder,
        "error": None
    }


@router.delete("/projects/{project_id}/stakeholders/{stakeholder_id}")
async def remove_stakeholder(project_id: str, stakeholder_id: str):
    """Remove a stakeholder from the project"""
    
    if stakeholder_id not in stakeholders_db:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    stakeholder = stakeholders_db[stakeholder_id]
    
    if stakeholder["project_id"] != project_id:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found in this project"
        }
    
    # Remove from project's stakeholder list
    if project_id in project_stakeholders:
        project_stakeholders[project_id] = [
            sid for sid in project_stakeholders[project_id] if sid != stakeholder_id
        ]
    
    # Delete stakeholder
    del stakeholders_db[stakeholder_id]
    
    return {
        "success": True,
        "data": {"deleted": stakeholder_id},
        "error": None
    }

