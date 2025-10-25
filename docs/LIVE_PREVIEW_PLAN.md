# Live Preview Implementation Plan

## Goal
Show users a live preview of their app as it's being built, with streaming updates and skeleton UI.

## Architecture Options

### Option 1: V0 + Gemini Hybrid (RECOMMENDED)
**Best for:** Beautiful UI + Fast preview

**Flow:**
1. User submits prompt
2. Frontend calls V0 API to generate UI components
3. Show V0 preview in iframe (instant!)
4. Backend uses Gemini to generate backend logic
5. Combine V0 frontend + Gemini backend
6. Push to GitHub

**Pros:**
- V0 generates beautiful, production-ready UI
- Instant preview in seconds
- shadcn/ui components built-in
- Specialized for React/Next.js

**Cons:**
- V0 limited free tier (10 gens/month)
- Need to combine two AI outputs

**V0 API:**
```typescript
// V0 has an SDK coming, but for now can use their web interface
// Or use their prompt engineering with Gemini
const v0Style = `
Generate a modern Next.js component using:
- shadcn/ui components
- Tailwind CSS
- TypeScript
- Lucide icons
Style: Modern, clean, with smooth animations
`;
```

### Option 2: Gemini Streaming Only
**Best for:** Simple, all-in-one solution

**Flow:**
1. User submits prompt
2. Backend streams Gemini responses
3. Frontend shows code being generated in real-time
4. Parse and preview components as they complete
5. Show in iframe with skeleton loader

**Pros:**
- Single AI provider
- True streaming experience
- Free (with Gemini API)

**Cons:**
- UI quality not as good as V0
- Slower to preview

### Option 3: StackBlitz WebContainer (ADVANCED)
**Best for:** Full live development environment in browser

**Flow:**
1. Generate code with Gemini/V0
2. Stream to StackBlitz WebContainer
3. Run full Next.js dev server in browser
4. Show live preview with hot reload

**Pros:**
- Full dev environment
- Real Next.js running
- No backend server needed

**Cons:**
- Complex integration
- Higher resource usage

## Recommended Implementation

### Phase 1: Skeleton + Streaming (Week 1)
```typescript
// frontend/src/components/LiveBuildPreview.tsx
export function LiveBuildPreview() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Left: Build Status */}
      <div>
        <BuildStatusStream />
      </div>
      
      {/* Right: Live Preview */}
      <div className="relative">
        <iframe 
          src="/preview" 
          className="w-full h-full"
          style={{ filter: isBuilding ? 'blur(4px)' : 'none' }}
        />
        {isBuilding && <SkeletonOverlay />}
      </div>
    </div>
  );
}
```

### Phase 2: Add V0 Integration (Week 2)
1. Get V0 API access (or use their SDK when available)
2. Generate UI with V0 first
3. Show V0 preview immediately
4. Enhance with Gemini backend

### Phase 3: StackBlitz Embed (Optional)
Add full WebContainer for live editing

## Streaming Implementation

### Backend Changes Needed:

```python
# backend/mcp/app_build.py

from fastapi.responses import StreamingResponse

@router.post("/app/build/stream")
async def build_app_stream(request: AppBuildRequest):
    """Stream the build process"""
    
    async def generate():
        # Step 1: Planning
        yield json.dumps({
            "type": "status",
            "message": "Planning your app...",
            "progress": 10
        }) + "\n"
        
        # Step 2: Generate with streaming
        async for chunk in gemini_generator.generate_app_stream(prompt):
            yield json.dumps({
                "type": "code",
                "file": chunk["file"],
                "content": chunk["content"],
                "progress": chunk["progress"]
            }) + "\n"
        
        # Step 3: Preview ready
        yield json.dumps({
            "type": "preview",
            "html": generate_preview_html(files),
            "progress": 70
        }) + "\n"
        
        # Step 4: GitHub push
        yield json.dumps({
            "type": "status",
            "message": "Pushing to GitHub...",
            "progress": 90
        }) + "\n"
        
        # Step 5: Complete
        yield json.dumps({
            "type": "complete",
            "repo_url": repo_url,
            "preview_url": preview_url,
            "progress": 100
        }) + "\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Frontend Changes Needed:

```typescript
// frontend/src/hooks/useStreamingBuild.ts

export function useStreamingBuild() {
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [previewHtml, setPreviewHtml] = useState("");
  
  async function startBuild(request: AppBuildRequest) {
    const response = await fetch("/mcp/app/build/stream", {
      method: "POST",
      body: JSON.stringify(request),
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const data = JSON.parse(chunk);
      
      switch (data.type) {
        case "status":
          setStatus(data.message);
          setProgress(data.progress);
          break;
        case "code":
          // Show code being written
          break;
        case "preview":
          setPreviewHtml(data.html);
          break;
        case "complete":
          // Done!
          break;
      }
    }
  }
  
  return { startBuild, status, progress, previewHtml };
}
```

## Preview Rendering Options

### Option A: Static HTML Preview (FASTEST)
Generate static HTML from React components and show in iframe:

```typescript
// No deployment needed!
<iframe 
  srcDoc={generateStaticPreview(components)}
  sandbox="allow-scripts"
/>
```

### Option B: StackBlitz Embed (ADVANCED)
Run full Next.js in browser:

```typescript
import sdk from '@stackblitz/sdk';

sdk.embedProjectId('preview-container', 'nextjs-template', {
  files: generatedFiles,
  template: 'node',
});
```

### Option C: CodeSandbox Embed
Similar to StackBlitz but different API

## What To Tell Your Frontend Engineer

### Immediate Tasks (Can Start Now):
1. **Create split-screen layout**
   - Left: Build status + logs
   - Right: Preview panel with skeleton

2. **Add skeleton UI**
   - Use shadcn/ui Skeleton component
   - Blur effect during build
   - Smooth reveal animation

3. **Implement streaming hook**
   - EventSource or fetch with streaming
   - Parse SSE messages
   - Update UI in real-time

### For Live Preview (Choose One):

**Option 1: Simple Static Preview** (No Vercel needed)
```typescript
// Just render HTML in iframe
<iframe srcDoc={generatedHtml} />
```

**Option 2: V0 Integration** (Best UI quality)
- Need V0 API access
- Show V0 preview first
- Enhance with backend

**Option 3: StackBlitz WebContainer** (Full environment)
- Complex but powerful
- Run real Next.js in browser

## Recommended Stack for Your Hackathon

### Backend:
- Gemini API for code generation (FREE)
- Streaming responses
- GitHub for version control

### Frontend:
- Split-screen with live preview
- Skeleton UI with blur effect
- Static HTML preview in iframe (no deployment needed!)
- Optional: Add V0 for better UI quality

### No Vercel Needed for Preview!
Just render static HTML in iframe. Deploy to GitHub Pages if needed.

## Example User Experience

1. User types: "Build a todo app"
2. UI splits into two panels
3. Left panel shows:
   ```
   ⏳ Planning your app...
   📝 Generating HomePage component...
   📝 Generating TodoList component...
   🎨 Styling with Tailwind...
   📁 Creating GitHub repo...
    Done!
   ```
4. Right panel shows:
   - Blurred skeleton at start
   - Components appear one by one
   - Blur fades away
   - Full preview revealed
5. Click "Open in GitHub" or "Deploy"

## Next Steps

1. **Choose your preview strategy** (I recommend Static HTML for MVP)
2. **Implement streaming endpoint** (backend)
3. **Create split-screen UI** (frontend)
4. **Add skeleton + blur effects** (frontend)
5. **Test streaming** (both)
6. **Optional: Add V0 for better UI**

