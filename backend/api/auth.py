"""
Authentication API Endpoints

Uses simple email + OTP for hackathon speed.
For production, integrate Clerk or Firebase Auth.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets
import hashlib

from database import get_db
from models import User, Session as DBSession
from integrations.email_service import send_otp_email

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class SignUpRequest(BaseModel):
    email: EmailStr
    name: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class AuthResponse(BaseModel):
    success: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    name: Optional[str] = None
    session_token: Optional[str] = None
    message: Optional[str] = None


# ==================== OTP STORAGE (In-memory for MVP) ====================
# For production: Use Redis or database with TTL

otp_storage = {}  # email -> {"otp": str, "expires_at": datetime, "name": str}


def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return str(secrets.randbelow(999999)).zfill(6)


def hash_token(token: str) -> str:
    """Hash session token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


# ==================== AUTH ENDPOINTS ====================

@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """
    Step 1: Sign up with email
    
    Flow:
    1. User enters email + name
    2. Check if email exists (if yes, treat as login)
    3. Generate OTP
    4. Store OTP in memory (expires in 10 min)
    5. Return success (in production: send OTP via email)
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        
        # Generate OTP
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        # Store OTP
        otp_storage[request.email] = {
            "otp": otp,
            "expires_at": expires_at,
            "name": request.name,
            "is_existing_user": existing_user is not None
        }
        
        # Send OTP email
        email_sent = send_otp_email(request.email, otp, request.name)
        
        if email_sent:
            return AuthResponse(
                success=True,
                message=f"OTP sent to {request.email}. Check your inbox!"
            )
        else:
            # Fallback if email fails
            return AuthResponse(
                success=True,
                message=f"OTP sent to {request.email}. Fallback OTP (check console): {otp}"
            )
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Step 2: Verify OTP and create session
    
    Flow:
    1. User enters OTP
    2. Verify OTP is correct and not expired
    3. Create or get user
    4. Generate session token
    5. Return user info + token
    """
    try:
        # Check if OTP exists
        if request.email not in otp_storage:
            raise HTTPException(status_code=400, detail="No OTP found. Please sign up first.")
        
        otp_data = otp_storage[request.email]
        
        # Check if OTP is expired
        if datetime.now(timezone.utc) > otp_data["expires_at"]:
            del otp_storage[request.email]
            raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")
        
        # Verify OTP
        if request.otp != otp_data["otp"]:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        # OTP is valid! Clear it
        name = otp_data["name"]
        is_existing = otp_data["is_existing_user"]
        del otp_storage[request.email]
        
        # Get or upgrade user from anonymous to authenticated
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Create new authenticated user
            user = User(
                email=request.email,
                hashed_password="otp_auth",  # No password for OTP auth
                name=name,
                session_id=None  # Authenticated users don't need session_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created new authenticated user: {user.email}")
        elif user.hashed_password is None:
            # Upgrade anonymous user to authenticated
            user.hashed_password = "otp_auth"
            user.name = name
            print(f"✅ Upgraded anonymous user to authenticated: {user.email}")
            db.commit()
            db.refresh(user)
        else:
            print(f"✅ Existing user logged in: {user.email}")
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        hashed_token = hash_token(session_token)
        
        # Create session
        session = DBSession(
            user_id=user.id,
            token=hashed_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(session)
        db.commit()
        
        return AuthResponse(
            success=True,
            user_id=user.id,
            email=user.email,
            name=user.name,
            session_token=session_token,
            message="Authentication successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verify OTP error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/clerk-user")
async def ensure_clerk_user(
    clerk_user_id: str,
    email: str,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Ensure a User record exists for a Clerk user
    This is called by frontend to ensure database sync
    
    Flow:
    1. Check if user exists with clerk_user_id
    2. If not, check by email
    3. If not, create new user
    4. Return user info
    """
    try:
        # Check by Clerk ID
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        
        if user:
            # User exists, update email/name if provided
            if email and user.email != email:
                user.email = email
            if name and user.name != name:
                user.name = name
            db.commit()
            db.refresh(user)
            print(f"✅ Found existing Clerk user: {user.email}")
        else:
            # Check by email (might be anonymous user)
            user = db.query(User).filter(User.email == email).first()
            if user:
                # Link anonymous user to Clerk
                user.clerk_user_id = clerk_user_id
                if name:
                    user.name = name
                db.commit()
                db.refresh(user)
                print(f"✅ Linked Clerk ID to existing user: {user.email}")
            else:
                # Create new user
                user = User(
                    clerk_user_id=clerk_user_id,
                    email=email,
                    name=name
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Created new Clerk user: {user.email}")
        
        return {
            "success": True,
            "data": {
                "user_id": user.id,
                "clerk_user_id": user.clerk_user_id,
                "email": user.email,
                "name": user.name
            },
            "error": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ensure Clerk user error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@router.get("/auth/me")
async def get_current_user(session_token: str, db: Session = Depends(get_db)):
    """
    Get current user from session token
    
    Used by frontend to check if user is logged in
    """
    try:
        hashed_token = hash_token(session_token)
        
        # Find session
        session = db.query(DBSession).filter(
            DBSession.token == hashed_token,
            DBSession.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/logout")
async def logout(session_token: str, db: Session = Depends(get_db)):
    """
    Logout user by invalidating session
    """
    try:
        hashed_token = hash_token(session_token)
        
        # Delete session
        session = db.query(DBSession).filter(DBSession.token == hashed_token).first()
        
        if session:
            db.delete(session)
            db.commit()
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        print(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== OAUTH PLACEHOLDER ====================
# For production: Add Google/GitHub OAuth

@router.get("/auth/oauth/google")
async def oauth_google():
    """Placeholder for Google OAuth"""
    raise HTTPException(status_code=501, detail="Google OAuth not implemented yet")


@router.get("/auth/oauth/github")
async def oauth_github():
    """Placeholder for GitHub OAuth"""
    raise HTTPException(status_code=501, detail="GitHub OAuth not implemented yet")

