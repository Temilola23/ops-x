"""
OPS-X Backend Server
Main FastAPI application with MCP endpoint registration
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import MCP endpoints
from mcp import (
    creao_build,
    repo_patch,
    conflict_scan,
    chat_summarize,
    pitch_generate,
    yc_pack,
    postman_flow
)

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    print("🚀 Starting OPS-X Backend Server...")
    # Initialize any resources here (DB connections, etc.)
    yield
    # Cleanup on shutdown
    print("👋 Shutting down OPS-X Backend Server...")


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


# Register MCP endpoints
app.include_router(creao_build.router, prefix="/mcp", tags=["MCP - Creao"])
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
