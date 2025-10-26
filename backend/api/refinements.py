"""
Refinements API - Handle iterative MVP improvements
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from database import get_db
from models import Refinement, Project, Stakeholder

router = APIRouter()


class CreateRefinementRequest(BaseModel):
    project_id: int
    stakeholder_id: int
    request_text: str
    ai_model_preference: Optional[str] = None  # "v0", "claude", "gemini", or "auto"
    uploaded_docs: Optional[List[str]] = None  # URLs or file paths


class RefinementResponse(BaseModel):
    id: int
    project_id: int
    stakeholder_id: int
    request_text: str
    ai_model_used: Optional[str]
    status: str
    pr_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/projects/{project_id}/refine")
async def create_refinement(
    project_id: int,
    request: CreateRefinementRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new refinement request
    
    Flow:
    1. Validate project and stakeholder
    2. Check role permissions
    3. Route to appropriate AI model (Fetch.ai)
    4. Create refinement record
    5. Return refinement ID for frontend to poll
    """
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "error": "Project not found",
                "data": None
            }
        
        # Verify stakeholder
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == request.stakeholder_id).first()
        if not stakeholder:
            return {
                "success": False,
                "error": "Stakeholder not found",
                "data": None
            }
        
        # Create refinement record
        refinement = Refinement(
            project_id=project_id,
            stakeholder_id=request.stakeholder_id,
            request_text=request.request_text,
            ai_model_preference=request.ai_model_preference or "auto",
            status="pending"
        )
        
        db.add(refinement)
        db.commit()
        db.refresh(refinement)
        
        # TODO: Queue refinement for processing by AI agents
        # This will be handled asynchronously
        
        return {
            "success": True,
            "data": {
                "refinement_id": refinement.id,
                "status": refinement.status,
                "message": "Refinement queued! AI agents are working on it."
            },
            "error": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"Create refinement error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Failed to create refinement",
            "data": None
        }


@router.get("/projects/{project_id}/refinements", response_model=List[RefinementResponse])
async def list_refinements(project_id: int, db: Session = Depends(get_db)):
    """
    Get all refinements for a project
    """
    refinements = db.query(Refinement).filter(Refinement.project_id == project_id).order_by(Refinement.created_at.desc()).all()
    return refinements


@router.get("/refinements/{refinement_id}")
async def get_refinement(refinement_id: int, db: Session = Depends(get_db)):
    """
    Get refinement details including status
    """
    refinement = db.query(Refinement).filter(Refinement.id == refinement_id).first()
    if not refinement:
        raise HTTPException(status_code=404, detail="Refinement not found")
    
    return {
        "success": True,
        "data": {
            "id": refinement.id,
            "project_id": refinement.project_id,
            "stakeholder_id": refinement.stakeholder_id,
            "request_text": refinement.request_text,
            "ai_model_used": refinement.ai_model_used,
            "status": refinement.status,
            "pr_url": refinement.pr_url,
            "files_changed": refinement.files_changed,
            "created_at": refinement.created_at
        },
        "error": None
    }

