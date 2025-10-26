"""
SQLAlchemy Models for OPS-X
PostgreSQL database schema
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """User/Admin accounts - supports both anonymous (session_id only) and authenticated users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # For anonymous users (MVP flow)
    session_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # For authenticated users (after sign up with Clerk)
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Legacy, not used with Clerk
    name = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    chat_messages = relationship("ChatMessage", back_populates="user")
    auth_sessions = relationship("Session", back_populates="user")


class Session(Base):
    """User sessions for authentication"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="auth_sessions")


class Project(Base):
    """Projects created by users"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt = Column(Text)  # Original user prompt
    github_repo = Column(String(255), index=True)  # e.g., "username/repo-name"
    app_url = Column(String(512))  # Deployed app URL (Vercel, etc.)
    status = Column(String(50), default="pending")  # pending, building, built, failed
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    stakeholders = relationship("Stakeholder", back_populates="project", cascade="all, delete-orphan")
    branches = relationship("Branch", back_populates="project", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="project", cascade="all, delete-orphan")
    code_embeddings = relationship("CodeEmbedding", back_populates="project", cascade="all, delete-orphan")


class Stakeholder(Base):
    """Team members/stakeholders for projects"""
    __tablename__ = "stakeholders"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Linked after signup
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # Founder, Frontend, Backend, Investor, Facilitator
    status = Column(String(20), default="pending")  # pending, active, inactive
    github_branch = Column(String(255))  # Linked branch name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="stakeholders")
    user = relationship("User")
    branches = relationship("Branch", back_populates="stakeholder")


class Branch(Base):
    """GitHub branches for stakeholders"""
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"), nullable=False)
    branch_name = Column(String(255), nullable=False)
    github_url = Column(String(512))  # Full GitHub branch URL
    status = Column(String(50), default="active")  # active, merged, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="branches")
    stakeholder = relationship("Stakeholder", back_populates="branches")


class ChatMessage(Base):
    """Chat messages for multiplayer collaboration"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String(50))  # User role at time of message
    is_ai = Column(Boolean, default=False)  # Is this from an AI agent?
    extra_data = Column(JSON)  # Extra data (agent type, etc.) - renamed from metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")


class CodeEmbedding(Base):
    """Code embeddings for semantic search (stored reference to Chroma)"""
    __tablename__ = "code_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(512), nullable=False)
    chroma_id = Column(String(255), unique=True, index=True)  # ID in Chroma collection
    language = Column(String(50))  # Language detected
    chunk_index = Column(Integer, default=0)  # For splitting large files
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="code_embeddings")
    
    # Note: Actual embeddings stored in Chroma, this is just metadata


class Refinement(Base):
    """MVP refinements requested by team members"""
    __tablename__ = "refinements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"), nullable=False)
    request_text = Column(Text, nullable=False)
    ai_model_preference = Column(String(50))  # "v0", "claude", "gemini", "auto"
    ai_model_used = Column(String(50))  # Actual model that processed it
    files_changed = Column(JSON)  # List of files modified
    pr_url = Column(String(500))  # GitHub PR URL
    coderabbit_score = Column(Integer)  # 1-10 severity score
    status = Column(String(20), default="pending")  # pending, processing, completed, failed, re-refining
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    project = relationship("Project")
    stakeholder = relationship("Stakeholder")


# Index for faster queries
from sqlalchemy import Index

Index('idx_project_stakeholders', Stakeholder.project_id)
Index('idx_project_branches', Branch.project_id)
Index('idx_project_chat', ChatMessage.project_id)
Index('idx_code_embeddings_project', CodeEmbedding.project_id)
Index('idx_github_repo', Project.github_repo)

