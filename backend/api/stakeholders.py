"""
Stakeholders API - Team member management for projects
Now using PostgreSQL with SQLAlchemy
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import Stakeholder, Project

router = APIRouter()


class CreateStakeholderRequest(BaseModel):
    name: str
    email: str
    role: str  # Founder, Frontend, Backend, Investor, Facilitator


class StakeholderResponse(BaseModel):
    id: int
    project_id: int
    name: str
    email: str
    role: str
    github_branch: Optional[str] = None
    created_at: datetime


@router.post("/projects/{project_id}/stakeholders")
async def add_stakeholder(
    project_id: int,
    request: CreateStakeholderRequest,
    db: Session = Depends(get_db)
):
    """Add a team member to the project"""
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    # Create stakeholder
    stakeholder = Stakeholder(
        project_id=project_id,
        name=request.name,
        email=request.email,
        role=request.role
    )
    
    db.add(stakeholder)
    db.commit()
    db.refresh(stakeholder)
    
    return {
        "success": True,
        "data": {
            "id": stakeholder.id,
            "project_id": stakeholder.project_id,
            "name": stakeholder.name,
            "email": stakeholder.email,
            "role": stakeholder.role,
            "github_branch": stakeholder.github_branch,
            "created_at": stakeholder.created_at.isoformat()
        },
        "error": None
    }


@router.get("/projects/{project_id}/stakeholders")
async def list_stakeholders(project_id: int, db: Session = Depends(get_db)):
    """List all stakeholders for a project"""
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {
            "success": False,
            "data": None,
            "error": "Project not found"
        }
    
    stakeholders = db.query(Stakeholder).filter(
        Stakeholder.project_id == project_id
    ).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "project_id": s.project_id,
                "name": s.name,
                "email": s.email,
                "role": s.role,
                "github_branch": s.github_branch,
                "created_at": s.created_at.isoformat()
            }
            for s in stakeholders
        ],
        "error": None
    }


@router.get("/projects/{project_id}/stakeholders/{stakeholder_id}")
async def get_stakeholder(
    project_id: int,
    stakeholder_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific stakeholder"""
    
    stakeholder = db.query(Stakeholder).filter(
        Stakeholder.id == stakeholder_id,
        Stakeholder.project_id == project_id
    ).first()
    
    if not stakeholder:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    return {
        "success": True,
        "data": {
            "id": stakeholder.id,
            "project_id": stakeholder.project_id,
            "name": stakeholder.name,
            "email": stakeholder.email,
            "role": stakeholder.role,
            "github_branch": stakeholder.github_branch,
            "created_at": stakeholder.created_at.isoformat()
        },
        "error": None
    }


@router.patch("/projects/{project_id}/stakeholders/{stakeholder_id}")
async def update_stakeholder(
    project_id: int,
    stakeholder_id: int,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update stakeholder (role, branch, etc.)"""
    
    stakeholder = db.query(Stakeholder).filter(
        Stakeholder.id == stakeholder_id,
        Stakeholder.project_id == project_id
    ).first()
    
    if not stakeholder:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    # Update allowed fields
    allowed_fields = ["name", "email", "role", "github_branch"]
    for field, value in updates.items():
        if field in allowed_fields and hasattr(stakeholder, field):
            setattr(stakeholder, field, value)
    
    db.commit()
    db.refresh(stakeholder)
    
    return {
        "success": True,
        "data": {
            "id": stakeholder.id,
            "project_id": stakeholder.project_id,
            "name": stakeholder.name,
            "email": stakeholder.email,
            "role": stakeholder.role,
            "github_branch": stakeholder.github_branch
        },
        "error": None
    }


@router.delete("/projects/{project_id}/stakeholders/{stakeholder_id}")
async def remove_stakeholder(
    project_id: int,
    stakeholder_id: int,
    db: Session = Depends(get_db)
):
    """Remove a stakeholder from the project"""
    
    stakeholder = db.query(Stakeholder).filter(
        Stakeholder.id == stakeholder_id,
        Stakeholder.project_id == project_id
    ).first()
    
    if not stakeholder:
        return {
            "success": False,
            "data": None,
            "error": "Stakeholder not found"
        }
    
    # Delete stakeholder
    db.delete(stakeholder)
    db.commit()
    
    return {
        "success": True,
        "data": {"deleted": stakeholder_id},
        "error": None
    }
