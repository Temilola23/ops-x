"""
Hybrid App Build - V0 for UI + Gemini for Backend Logic
Combines the best of both worlds for hackathon demo
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime

from integrations.v0_api import v0_generator
from integrations.gemini_code_generator import gemini_code_generator
from integrations.github_api import github_client
from integrations.vercel_api import vercel_client

router = APIRouter()


class AppSpec(BaseModel):
    name: str
    entities: List[str] = []
    pages: List[str] = []
    requirements: List[str] = []


class AppBuildRequest(BaseModel):
    project_id: str
    spec: AppSpec
    use_v0: bool = True  # Toggle V0 usage


def create_sse_event(data: dict) -> str:
    """Format data as Server-Sent Event"""
    return f"data: {json.dumps(data)}\n\n"


@router.post("/app/build/hybrid")
async def build_app_hybrid_stream(request: AppBuildRequest):
    """
    Hybrid app builder with streaming:
    - V0 generates beautiful UI components
    - Gemini generates backend logic and API routes
    - Real-time progress updates via SSE
    """
    
    async def event_generator():
        try:
            project_id = request.project_id
            project_name = request.spec.name
            pages = request.spec.pages or ["Home", "Dashboard"]
            requirements = " ".join(request.spec.requirements)
            
            # Phase 1: Planning
            yield create_sse_event({
                "type": "status",
                "phase": "planning",
                "message": "🤔 Planning your application architecture...",
                "progress": 5
            })
            
            await asyncio.sleep(0.5)
            
            all_files = {}
            
            # Phase 2: Generate UI with V0 (if enabled)
            if request.use_v0 and v0_generator:
                yield create_sse_event({
                    "type": "status",
                    "phase": "ui_generation",
                    "message": "🎨 Generating beautiful UI with V0...",
                    "progress": 10
                })
                
                try:
                    # Generate UI components with V0 (no streaming for now - simpler)
                    v0_files = await v0_generator.generate_full_app(
                        prompt=requirements,
                        project_name=project_name,
                        pages=pages
                    )
                    
                    all_files.update(v0_files)
                    
                    # Stream each generated file
                    for idx, (filename, content) in enumerate(v0_files.items()):
                        progress = 10 + (idx / len(v0_files)) * 30
                        yield create_sse_event({
                            "type": "file_created",
                            "filename": filename,
                            "content": content[:200] + "...",  # Preview
                            "phase": "ui",
                            "progress": progress
                        })
                        await asyncio.sleep(0.1)
                    
                    yield create_sse_event({
                        "type": "status",
                        "phase": "ui_complete",
                        "message": " UI components generated with V0!",
                        "progress": 40
                    })
                    
                except Exception as e:
                    print(f"  V0 generation failed, falling back to Gemini: {e}")
                    # Fallback to Gemini if V0 fails
                    request.use_v0 = False
            
            # Phase 3: Generate backend logic with Gemini
            yield create_sse_event({
                "type": "status",
                "phase": "backend_generation",
                "message": "🤖 Generating backend logic with Gemini...",
                "progress": 45
            })
            
            # Build Gemini prompt
            if request.use_v0 and all_files:
                # V0 already generated UI, just need backend
                gemini_prompt = f"""
                Generate API routes and backend logic for a Next.js app called "{project_name}".
                
                Requirements: {requirements}
                
                The UI components are already created. Generate:
                1. API routes in src/app/api/
                2. Server actions if needed
                3. Database schema (prisma or similar)
                4. Utility functions in src/lib/
                
                Use TypeScript. Return only the backend files.
                """
            else:
                # No V0, generate full app with Gemini
                gemini_prompt = f"""
                Generate a complete Next.js 14 application called "{project_name}".
                
                Requirements: {requirements}
                Pages: {", ".join(pages)}
                
                Use:
                - Next.js 14 with App Router
                - TypeScript
                - Tailwind CSS
                - shadcn/ui components
                - Modern, clean design
                
                Generate all necessary files including:
                - Pages (src/app/)
                - Components (src/components/)
                - API routes (src/app/api/)
                - Utilities (src/lib/)
                - Configuration files
                """
            
            # Initialize Gemini generator if needed
            if gemini_code_generator is None:
                from integrations.gemini_code_generator import GeminiCodeGenerator
                generator = GeminiCodeGenerator()
            else:
                generator = gemini_code_generator
            
            # Generate with Gemini
            gemini_files = generator.generate_nextjs_app(
                project_name=project_name,
                user_requirements=gemini_prompt
            )
            
            # Merge Gemini files (don't overwrite V0 UI files)
            for filename, content in gemini_files.items():
                # Only add if not a page file (V0 already generated those)
                if "/app/api/" in filename or "/lib/" in filename or "config" in filename.lower():
                    all_files[filename] = content
                elif filename not in all_files:
                    # Add if V0 didn't generate it
                    all_files[filename] = content
            
            # Stream backend files
            backend_files = [f for f in gemini_files.keys() if "/api/" in f or "/lib/" in f]
            for idx, filename in enumerate(backend_files):
                progress = 45 + (idx / max(len(backend_files), 1)) * 20
                yield create_sse_event({
                    "type": "file_created",
                    "filename": filename,
                    "content": all_files[filename][:200] + "...",
                    "phase": "backend",
                    "progress": progress
                })
                await asyncio.sleep(0.1)
            
            yield create_sse_event({
                "type": "status",
                "phase": "code_complete",
                "message": " Code generation complete!",
                "progress": 65
            })
            
            # Phase 4: Generate preview HTML
            yield create_sse_event({
                "type": "status",
                "phase": "preview",
                "message": "🔍 Creating live preview...",
                "progress": 70
            })
            
            preview_html = generate_preview_html(all_files, project_name)
            
            yield create_sse_event({
                "type": "preview_ready",
                "html": preview_html,
                "progress": 75
            })
            
            # Phase 5: Push to GitHub
            yield create_sse_event({
                "type": "status",
                "phase": "github",
                "message": "📁 Creating GitHub repository...",
                "progress": 80
            })
            
            repo_name = project_name.lower().replace(' ', '-').replace('_', '-')
            repo_result = await github_client.create_repo(
                name=repo_name,
                description=f"Generated by OPS-X: {requirements[:100]}",
                private=False
            )
            
            if not repo_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create GitHub repo: {repo_result.get('error')}"
                )
            
            repo_url = repo_result["repo_url"]
            repo_full_name = repo_result["repo_name"]
            
            yield create_sse_event({
                "type": "status",
                "phase": "github_push",
                "message": "⬆️  Pushing code to GitHub...",
                "progress": 85
            })
            
            await asyncio.sleep(2)  # Give GitHub time to initialize
            
            push_result = await github_client.push_multiple_files(
                repo_full_name=repo_full_name,
                files=all_files,
                commit_message=f"Initial commit: Generated by OPS-X\n\n{requirements}",
                branch="main"
            )
            
            if not push_result["success"]:
                print(f"  Some files failed to push: {push_result}")
            
            # Phase 6: Deploy (optional)
            app_url = repo_url
            
            if vercel_client.token:
                yield create_sse_event({
                    "type": "status",
                    "phase": "deploy",
                    "message": "🚀 Deploying to Vercel...",
                    "progress": 90
                })
                
                try:
                    deploy_result = await vercel_client.create_project(
                        repo_url=repo_url,
                        project_name=repo_name
                    )
                    
                    if deploy_result.get("success"):
                        app_url = deploy_result.get("url", repo_url)
                except Exception as e:
                    print(f"  Vercel deployment failed: {e}")
            
            # Phase 7: Complete!
            yield create_sse_event({
                "type": "complete",
                "repo_url": repo_url,
                "app_url": app_url,
                "preview_html": preview_html,
                "files_generated": len(all_files),
                "used_v0": request.use_v0 and v0_generator is not None,
                "message": "🎉 Your app is ready!",
                "progress": 100
            })
            
        except Exception as e:
            yield create_sse_event({
                "type": "error",
                "message": str(e),
                "progress": 0
            })
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


def generate_preview_html(files: Dict[str, str], project_name: str) -> str:
    """
    Generate static HTML preview from Next.js files
    This shows in iframe while the real app is being deployed
    """
    
    # Try to find the main page component (check both with and without src/)
    page_file = files.get("app/page.tsx", "") or files.get("src/app/page.tsx", "")
    
    if not page_file:
        # Try to find any component file
        for filename, content in files.items():
            if filename.endswith("page.tsx") or filename.endswith("Page.tsx"):
                page_file = content
                break
        
        if not page_file:
            page_file = "<div>Loading preview...</div>"
    
    # Simple JSX to HTML conversion (can be enhanced)
    html_content = simplify_jsx_to_html(page_file)
    
    preview_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Preview</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@latest/font/lucide.min.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        .preview-banner {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.5s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateY(100px);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}
        
        .preview-content {{
            animation: fadeIn 1s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="preview-banner">
        🔍 Live Preview
    </div>
    
    <div class="preview-content">
        {html_content}
    </div>
</body>
</html>
"""
    
    return preview_html


def simplify_jsx_to_html(jsx_code: str) -> str:
    """
    Convert React JSX to static HTML for preview
    This is a simplified version - can be enhanced with a proper parser
    """
    import re
    
    # Remove imports
    html = re.sub(r'import .*?;?\n', '', jsx_code)
    
    # Remove exports
    html = re.sub(r'export (default )?', '', html)
    
    # Remove function declarations
    html = re.sub(r'(function|const) \w+\s*=?\s*\([^)]*\)\s*(?:=>)?\s*\{', '', html)
    
    # Remove return statement
    html = re.sub(r'return\s*\(', '', html)
    
    # Remove trailing braces and semicolons
    html = html.rstrip(')};\n ')
    
    # Convert className to class
    html = html.replace('className=', 'class=')
    
    # Remove React hooks and state
    html = re.sub(r'const \[.*?\] = useState\(.*?\);?', '', html)
    html = re.sub(r'const \[.*?\] = use.*?\(.*?\);?', '', html)
    
    # Clean up excess whitespace
    html = re.sub(r'\n\s*\n', '\n', html)
    
    return html.strip()

