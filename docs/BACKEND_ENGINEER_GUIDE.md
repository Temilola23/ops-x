# Backend Engineer's Role & V0 Integration Guide

## V0 API Status - IMPORTANT

### V0 Has APIs! Two Options:

1. **Model API** - Direct AI access for generating React/Next.js components
   - Framework-aware code generation
   - Fast streaming responses
   - OpenAI-compatible format

2. **Platform API** - Full development infrastructure
   - Chat/conversation management
   - Code parsing and file generation
   - Browser app execution
   - Project and deployment tools

### Pricing:
- **Free Plan**: No API access (web UI only)
- **Premium/Team Plan**: Required for API access
  - Usage-based billing
  - Exact price: ~$20/month Premium (need to verify on v0.dev/pricing)
  - Team plan higher

### For Hackathon:
**RECOMMENDATION**: Skip V0 API, use Gemini only
- Gemini is FREE with API key
- V0 requires paid plan
- You can manually use V0 web UI for testing UI quality
- Save money, ship faster

---

## Architecture Decision: Gemini vs V0

### Option 1: Gemini Only (RECOMMENDED FOR HACKATHON)
```
User Prompt → Gemini → Full Next.js App → GitHub → Preview
              (FREE)    (Frontend + Backend)
```

**Your Backend Role:**
1. Generate full-stack code with Gemini
2. Stream responses to frontend
3. Push to GitHub
4. Return preview HTML

**Pros:**
- FREE
- Single AI provider (simpler)
- Full-stack generation
- Already implemented!

**Cons:**
- UI quality not as specialized

---

### Option 2: V0 + Gemini Hybrid (IF YOU HAVE BUDGET)
```
User Prompt → V0 (Frontend) → Gemini (Backend) → Combine → GitHub
              ($20/month)      (FREE)
```

**Your Backend Role:**
1. Call V0 API for UI components
2. Call Gemini API for backend logic
3. Merge the two outputs
4. Push to GitHub
5. Return preview HTML

**Pros:**
- Beautiful UI from V0
- Backend logic from Gemini
- Best of both worlds

**Cons:**
- Costs $20/month
- More complex integration
- Two AI providers to manage

---

### Option 3: Gemini with V0 Prompt Engineering (BEST COMPROMISE)
```
User Prompt → Enhanced Prompt → Gemini → Next.js App → GitHub
              (V0-style)         (FREE)
```

**Your Backend Role:**
1. Add V0-style instructions to Gemini prompt
2. Generate code with Gemini
3. Stream to frontend
4. Push to GitHub

**Example Enhanced Prompt:**
```python
v0_style_instructions = """
Generate a modern Next.js application following these guidelines:
- Use shadcn/ui components
- Tailwind CSS for styling
- TypeScript throughout
- Lucide React icons
- Clean, modern design with smooth animations
- Responsive mobile-first layout
- Dark mode support
"""

full_prompt = f"{v0_style_instructions}\n\n{user_prompt}"
```

**Pros:**
- FREE (just Gemini)
- Better UI quality than raw Gemini
- No additional APIs to integrate

**Cons:**
- Not as good as real V0
- Still a compromise

---

## Your Backend Engineer Responsibilities

### Phase 1: Streaming Endpoint (THIS IS YOUR JOB)

**Create `/mcp/app/build/stream` endpoint:**

```python
# backend/mcp/app_build.py

from fastapi.responses import StreamingResponse
import json
import asyncio

@router.post("/app/build/stream")
async def build_app_stream(request: AppBuildRequest):
    """
    Stream the build process to frontend in real-time
    Frontend can show progress and preview as it happens
    """
    
    async def event_generator():
        try:
            # 1. Planning phase
            yield create_sse_event({
                "type": "status",
                "message": "🤔 Planning your application...",
                "progress": 5
            })
            
            await asyncio.sleep(0.5)  # Give UI time to show
            
            # 2. Code generation phase
            yield create_sse_event({
                "type": "status",
                "message": "🤖 Generating code with AI...",
                "progress": 10
            })
            
            # Generate code (this is streaming from Gemini)
            files = {}
            async for chunk in gemini_generator.generate_app_streaming(
                prompt=build_full_prompt(request),
                project_name=request.spec.name
            ):
                files[chunk["filename"]] = chunk["content"]
                
                # Stream each file as it's created
                yield create_sse_event({
                    "type": "file",
                    "filename": chunk["filename"],
                    "content": chunk["content"],
                    "progress": 10 + (chunk["file_index"] / chunk["total_files"]) * 50
                })
            
            # 3. Generate preview HTML
            yield create_sse_event({
                "type": "status",
                "message": "🎨 Creating preview...",
                "progress": 65
            })
            
            preview_html = generate_preview_html(files)
            
            yield create_sse_event({
                "type": "preview",
                "html": preview_html,
                "progress": 70
            })
            
            # 4. Create GitHub repo
            yield create_sse_event({
                "type": "status",
                "message": "📁 Creating GitHub repository...",
                "progress": 75
            })
            
            repo_result = await github_client.create_repo(...)
            repo_url = repo_result["repo_url"]
            
            # 5. Push files
            yield create_sse_event({
                "type": "status",
                "message": "⬆️ Pushing code to GitHub...",
                "progress": 85
            })
            
            await github_client.push_multiple_files(...)
            
            # 6. Complete
            yield create_sse_event({
                "type": "complete",
                "repo_url": repo_url,
                "preview_url": preview_html,
                "progress": 100,
                "message": " Your app is ready!"
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
        }
    )

def create_sse_event(data: dict) -> str:
    """Format data as Server-Sent Event"""
    return f"data: {json.dumps(data)}\n\n"
```

### Phase 2: Preview HTML Generator (THIS IS YOUR JOB)

**Convert generated files to preview HTML:**

```python
# backend/integrations/preview_generator.py

def generate_preview_html(files: dict) -> str:
    """
    Take generated Next.js files and create a static HTML preview
    This runs in an iframe on the frontend
    """
    
    # Extract the main page component
    page_content = files.get("src/app/page.tsx", "")
    
    # Simple transformation (can be enhanced)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@latest/font/lucide.css">
        <style>
            body {{ margin: 0; padding: 20px; font-family: system-ui; }}
            .preview-badge {{
                position: fixed;
                top: 10px;
                right: 10px;
                background: #3b82f6;
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                z-index: 1000;
            }}
        </style>
    </head>
    <body>
        <div class="preview-badge">🔍 Preview Mode</div>
        <div id="root">
            <!-- Render simplified version of the component -->
            {simplify_react_to_html(page_content)}
        </div>
    </body>
    </html>
    """
    
    return html

def simplify_react_to_html(react_code: str) -> str:
    """
    Convert React JSX to static HTML for preview
    This is simplified - can use a proper parser
    """
    # Remove import statements
    html = re.sub(r'import .*?\n', '', react_code)
    
    # Remove export statements
    html = re.sub(r'export (default )?', '', html)
    
    # Remove function declarations
    html = re.sub(r'function \w+\(\) \{', '', html)
    html = re.sub(r'return \(', '', html)
    
    # Remove trailing braces
    html = html.rstrip(')}; \n')
    
    # Convert className to class
    html = html.replace('className=', 'class=')
    
    return html
```

### Phase 3: Gemini Streaming (THIS IS YOUR JOB)

**Add streaming support to Gemini generator:**

```python
# backend/integrations/gemini_api.py

class GeminiGenerator:
    async def generate_app_streaming(self, prompt: str, project_name: str):
        """
        Stream the code generation process
        Yield each file as it's created
        """
        
        # Configure streaming
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 8000,
        }
        
        # Generate with streaming
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=True  # Enable streaming!
        )
        
        current_file = None
        current_content = []
        file_index = 0
        
        for chunk in response:
            text = chunk.text
            
            # Parse file boundaries (simplified)
            if "// File:" in text or "```" in text:
                if current_file:
                    # Yield completed file
                    yield {
                        "filename": current_file,
                        "content": "".join(current_content),
                        "file_index": file_index,
                        "total_files": 10,  # Estimate
                    }
                    file_index += 1
                    current_content = []
                
                # Start new file
                current_file = extract_filename(text)
            else:
                current_content.append(text)
        
        # Yield last file
        if current_file:
            yield {
                "filename": current_file,
                "content": "".join(current_content),
                "file_index": file_index,
                "total_files": file_index + 1,
            }
```

---

## What V0 Would Handle (If You Use It)

### V0's Job:
- Generate beautiful React/Next.js UI components
- Use shadcn/ui automatically
- Modern, responsive design
- Tailwind styling
- Component composition

### Gemini's Job:
- API routes and backend logic
- Database schemas
- Business logic
- Integration code
- Server actions

### When to Use V0 in the Flow:

**Scenario 1: Initial Build (User's first prompt)**
```
Use: Gemini only (full-stack)
Why: Need complete app, not just UI
```

**Scenario 2: Frontend Stakeholder Iteration**
```
Use: V0 for UI changes
Why: Specialized UI improvements
```

**Scenario 3: UI Agent (Specialized)**
```
Use: V0 API through your agent
Why: Best UI quality for UI-specific tasks
```

---

## Deployment: Static vs Real-Time

### You Said: "I need non-static deployment in real time"

**Here's the confusion:**

1. **Preview** = Static HTML in iframe (INSTANT)
   - Just for visualization
   - Not a real deployment
   - No server running
   - Perfect for showing progress

2. **Real Deployment** = Live Next.js app
   - Requires actual deployment (Vercel/Netlify)
   - Takes 2-3 minutes
   - Full functionality
   - Happens AFTER preview

### The Flow:
```
1. Generate code (10s) → Show PREVIEW (instant)
2. Push to GitHub (5s)
3. Deploy to Vercel (2min) → Show LIVE APP
```

**V0 Cannot Handle Deployment**
- V0 generates code only
- You still need GitHub + Vercel for deployment
- V0's "Platform API" has deployment tools but they're for V0's own platform

---

## Your Complete Backend Checklist

### Must Implement:
- [ ] Streaming endpoint (`/mcp/app/build/stream`)
- [ ] SSE (Server-Sent Events) formatting
- [ ] Preview HTML generator
- [ ] Gemini streaming support
- [ ] Progress tracking
- [ ] Error handling in streams

### Optional (If Using V0):
- [ ] V0 API integration
- [ ] V0 + Gemini merge logic
- [ ] V0 API key management

### Already Done:
- [x] Non-streaming build endpoint
- [x] Gemini integration
- [x] GitHub integration
- [x] Projects API

---

## Recommended Plan for Hackathon

### For Backend (You):
1. **Implement streaming endpoint** (2-3 hours)
2. **Add preview HTML generator** (1 hour)
3. **Test with Gemini only** (30 mins)
4. **Enhance Gemini prompts with V0-style instructions** (30 mins)

### For Frontend (Your teammate):
1. **Split-screen layout** (2 hours)
2. **EventSource client for streaming** (1 hour)
3. **Skeleton UI + blur effects** (1 hour)
4. **Preview iframe renderer** (30 mins)

### Total Time: ~8 hours for both

### Skip V0 API Because:
- Costs money ($20/month minimum)
- Adds complexity
- Gemini is good enough for hackathon
- Can manually use V0 web UI to test designs

---

## Decision Matrix

| Feature | Gemini Only | Gemini + V0 |
|---------|-------------|-------------|
| Cost | FREE | $20/month |
| Setup Time | 1 hour | 3 hours |
| UI Quality | Good | Excellent |
| Backend Quality | Excellent | Excellent |
| Complexity | Simple | Complex |
| **Hackathon?** |  YES |  Too much |

---

## Summary for You (Backend Engineer)

### Your Job:
1. Build streaming endpoint
2. Generate preview HTML
3. Stream progress to frontend
4. Push to GitHub when done
5. Return preview + repo URL

### What Your Frontend Guy Does:
1. Show your stream in UI
2. Display preview in iframe
3. Add blur/skeleton effects
4. Handle loading states

### Use V0?
**NO** - Too expensive and complex for hackathon
**Instead**: Use Gemini with V0-style prompt engineering

### Questions Answered:
- **V0 APIs?** YES, but requires $20/month Premium
- **V0 for deployment?** NO, still need Vercel/GitHub
- **V0 vs Gemini?** Use Gemini only for hackathon
- **Non-static deployment?** That's Vercel, not preview
- **V0 for scaffolding?** Can work, but costs money

**Bottom line: Implement streaming, skip V0 API, use Gemini only.**

