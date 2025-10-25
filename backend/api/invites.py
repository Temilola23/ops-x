"""
Invites API - Handle team invitation verification and activation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone

from database import get_db
from models import Stakeholder, Project, User

router = APIRouter()


class ActivateInviteRequest(BaseModel):
    code: str
    stakeholder_id: int
    clerk_user_id: str
    email: EmailStr


@router.get("/invites/verify")
async def verify_invite(
    code: str = Query(...),
    project: int = Query(...),
    stakeholder: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Verify invite code and return invitation details
    """
    try:
        # Import OTP storage from auth
        from api.auth import otp_storage
        
        # Find the stakeholder
        stakeholder_record = db.query(Stakeholder).filter(Stakeholder.id == stakeholder).first()
        if not stakeholder_record:
            return {
                "success": False,
                "error": "Invitation not found",
                "data": None
            }
        
        # Verify the code matches in OTP storage
        otp_data = otp_storage.get(stakeholder_record.email)
        if not otp_data:
            return {
                "success": False,
                "error": "Invitation code expired or invalid",
                "data": None
            }
        
        if otp_data.get("otp") != code:
            return {
                "success": False,
                "error": "Invalid invitation code",
                "data": None
            }
        
        # Check if expired
        if otp_data.get("expires_at") < datetime.now(timezone.utc):
            return {
                "success": False,
                "error": "Invitation code has expired",
                "data": None
            }
        
        # Verify it's a team invite
        if not otp_data.get("is_team_invite"):
            return {
                "success": False,
                "error": "Invalid invitation type",
                "data": None
            }
        
        # Get project details
        project_record = db.query(Project).filter(Project.id == project).first()
        if not project_record:
            return {
                "success": False,
                "error": "Project not found",
                "data": None
            }
        
        # Get inviter name
        inviter = db.query(User).filter(User.id == project_record.owner_id).first()
        inviter_name = "Team Lead"
        if inviter:
            inviter_name = inviter.name or inviter.email or "Project Creator"
        
        return {
            "success": True,
            "data": {
                "project_name": project_record.name,
                "role": stakeholder_record.role,
                "inviter_name": inviter_name,
                "project_id": project,
                "stakeholder_id": stakeholder
            },
            "error": None
        }
        
    except Exception as e:
        print(f"Verify invite error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Failed to verify invitation",
            "data": None
        }


@router.post("/invites/activate")
async def activate_invite(
    request: ActivateInviteRequest,
    db: Session = Depends(get_db)
):
    """
    Activate stakeholder account and link to Clerk user
    
    Flow:
    1. Verify OTP code
    2. Get or create User with clerk_user_id
    3. Link stakeholder to user
    4. Update stakeholder status to 'active'
    5. Clean up OTP
    """
    try:
        # Import OTP storage from auth
        from api.auth import otp_storage
        
        # Find the stakeholder
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == request.stakeholder_id).first()
        if not stakeholder:
            return {
                "success": False,
                "error": "Stakeholder not found",
                "data": None
            }
        
        # Verify the code
        otp_data = otp_storage.get(stakeholder.email)
        if not otp_data or otp_data.get("otp") != request.code:
            return {
                "success": False,
                "error": "Invalid invitation code",
                "data": None
            }
        
        # Check if expired
        if otp_data.get("expires_at") < datetime.now(timezone.utc):
            return {
                "success": False,
                "error": "Invitation code has expired",
                "data": None
            }
        
        # Get or create User with Clerk ID
        user = db.query(User).filter(User.clerk_user_id == request.clerk_user_id).first()
        if not user:
            # Check if user exists by email (might be anonymous)
            user = db.query(User).filter(User.email == request.email).first()
            if user:
                # Upgrade anonymous user to Clerk user
                user.clerk_user_id = request.clerk_user_id
                user.email = request.email
            else:
                # Create new user
                user = User(
                    clerk_user_id=request.clerk_user_id,
                    email=request.email
                )
                db.add(user)
                db.flush()  # Get user ID
        
        # Link stakeholder to user
        stakeholder.user_id = user.id
        stakeholder.status = "active"
        
        db.commit()
        db.refresh(stakeholder)
        
        # Clean up OTP
        otp_storage.pop(stakeholder.email, None)
        
        return {
            "success": True,
            "data": {
                "user_id": user.id,
                "stakeholder_id": stakeholder.id,
                "project_id": stakeholder.project_id,
                "status": stakeholder.status
            },
            "error": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"Activate invite error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Failed to activate invitation",
            "data": None
        }

