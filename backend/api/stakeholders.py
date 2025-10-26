"""
Stakeholders API - Team member management for projects
Now using PostgreSQL with SQLAlchemy
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import Stakeholder, Project, User
from integrations.email_service import send_team_invite_email

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
    
    # Check if user exists with this email (auto-link)
    user = db.query(User).filter(User.email == request.email).first()
    user_id = user.id if user else None
    
    # Create stakeholder
    stakeholder = Stakeholder(
        project_id=project_id,
        user_id=user_id,  # Link to user if exists
        name=request.name,
        email=request.email,
        role=request.role,
        status="active" if user_id else "pending"  # Active if linked, pending if not
    )
    
    db.add(stakeholder)
    db.commit()
    db.refresh(stakeholder)
    
    print(f"✅ Created stakeholder for {request.email} (user_id: {user_id}, status: {stakeholder.status})")
    
    return {
        "success": True,
        "data": {
            "id": stakeholder.id,
            "project_id": stakeholder.project_id,
            "name": stakeholder.name,
            "email": stakeholder.email,
            "role": stakeholder.role,
            "status": stakeholder.status,
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


# ==================== TEAM INVITATION ====================

class InviteTeamMemberRequest(BaseModel):
    name: str
    email: str
    role: str


@router.post("/projects/{project_id}/invite")
async def invite_team_member(
    project_id: int,
    request: InviteTeamMemberRequest,
    db: Session = Depends(get_db)
):
    """
    Invite team member to project
    
    Flow:
    1. Create stakeholder record
    2. Generate invite OTP
    3. Send email (for production) or return OTP (for demo)
    4. When user signs up with email, link to stakeholder
    """
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "data": None,
                "error": "Project not found"
            }
        
        # Check if stakeholder already exists
        existing = db.query(Stakeholder).filter(
            Stakeholder.project_id == project_id,
            Stakeholder.email == request.email
        ).first()
        
        if existing:
            return {
                "success": False,
                "data": None,
                "error": "Team member already invited"
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
        
        # Generate invite OTP
        from datetime import timezone, timedelta
        import secrets
        
        otp = str(secrets.randbelow(999999)).zfill(6)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        # Store OTP in auth storage (shared with auth.py)
        from api.auth import otp_storage
        otp_storage[request.email] = {
            "otp": otp,
            "expires_at": expires_at,
            "name": request.name,
            "is_existing_user": False,
            "is_team_invite": True,
            "project_id": project_id,
            "stakeholder_id": stakeholder.id
        }
        
        # Get inviter name (project owner)
        inviter = db.query(User).filter(User.id == project.owner_id).first()
        if inviter:
            inviter_name = inviter.name or inviter.email or "Project Creator"
        else:
            inviter_name = "Team Lead"
        
        # Send team invite email
        email_sent = send_team_invite_email(
            to_email=request.email,
            inviter_name=inviter_name,
            project_name=project.name,
            otp=otp,
            role=request.role,
            project_id=project_id,
            stakeholder_id=stakeholder.id,
            invite_url=os.getenv("FRONTEND_URL", "http://localhost:3000")
        )
        
        if email_sent:
            return {
                "success": True,
                "data": {
                    "stakeholder_id": stakeholder.id,
                    "email": request.email,
                    "role": request.role,
                    "message": f"Invitation sent to {request.email}. They should check their inbox!"
                },
                "error": None
            }
        else:
            # Fallback if email fails
            return {
                "success": True,
                "data": {
                    "stakeholder_id": stakeholder.id,
                    "email": request.email,
                    "role": request.role,
                    "otp": otp,  # Show OTP if email failed
                    "message": f"Invitation created. Fallback OTP (check console): {otp}"
                },
                "error": None
            }
        
    except Exception as e:
        print(f"Invite team member error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }
