"""
OPS-X Backend Server
Main FastAPI application with MCP endpoint registration
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# CRITICAL: Load environment variables BEFORE importing any modules
# that need API keys (gemini, github, etc.)
env_path = Path(__file__).parent.parent / "scripts" / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f" Loaded environment from {env_path}")
else:
    load_dotenv()
    print(" Loading .env from current directory")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# NOW import modules (after env is loaded)
# Import MCP endpoints
from mcp import (
    # V0 build endpoints DISABLED - using frontend V0 SDK instead
    # app_build,
    # app_build_hybrid,
    # app_build_v0,
    repo_patch,
    conflict_scan,
    chat_summarize,
    pitch_generate,
    yc_pack,
    postman_flow
)

# Import REST API endpoints
from api import projects, stakeholders, branches, auth, invites


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    print(" Starting OPS-X Backend Server...")
    
    # Initialize database
    try:
        from database import init_db, engine
        from integrations.chroma_client import chroma_search
        
        print("Initializing PostgreSQL database...")
        init_db()
        
        # Test connection
        with engine.connect() as conn:
            print("PostgreSQL connection successful!")
        
        if chroma_search:
            print(f"Chroma DB initialized: {chroma_search.get_stats()}")
        else:
            print("WARNING: Chroma DB not available")
        
    except Exception as e:
        print(f"WARNING: Database initialization failed: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct")
    
    yield
    
    # Cleanup on shutdown
    print(" Shutting down OPS-X Backend Server...")


# Create FastAPI app
app = FastAPI(
    title="OPS-X API",
    description="One-Prompt Startup Platform Backend",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register REST API endpoints
app.include_router(auth.router, prefix="/api", tags=["Authentication API"])
app.include_router(projects.router, prefix="/api", tags=["Projects API"])
app.include_router(stakeholders.router, prefix="/api", tags=["Stakeholders API"])
app.include_router(branches.router, prefix="/api", tags=["Branches API"])
app.include_router(invites.router, prefix="/api", tags=["Invites API"])

# Register MCP endpoints
# V0 build endpoints DISABLED - frontend handles V0 with TypeScript SDK
# app.include_router(app_build_v0.router, tags=["MCP - PURE V0 BUILD (RECOMMENDED)"])
# app.include_router(app_build.router, prefix="/mcp", tags=["MCP - App Build (Legacy Gemini)"])
# app.include_router(app_build_hybrid.router, prefix="/mcp", tags=["MCP - Hybrid Build (V0 + Gemini - BROKEN)"])
app.include_router(repo_patch.router, prefix="/mcp", tags=["MCP - Repository"])
app.include_router(conflict_scan.router, prefix="/mcp", tags=["MCP - Conflict"])
app.include_router(chat_summarize.router, prefix="/mcp", tags=["MCP - Chat"])
app.include_router(pitch_generate.router, prefix="/mcp", tags=["MCP - Pitch"])
app.include_router(yc_pack.router, prefix="/mcp", tags=["MCP - YC Pack"])
app.include_router(postman_flow.router, prefix="/mcp", tags=["MCP - Postman"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to OPS-X API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
