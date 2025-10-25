# V0 Integration Setup Guide

## What V0 Does for You

V0 generates **beautiful, production-ready UI components** using:
- React/Next.js 14
- shadcn/ui components
- Tailwind CSS
- TypeScript
- Lucide icons
- Modern, responsive design

Combined with Gemini for backend logic, you get the best of both worlds!

---

## Step 1: Sign Up for V0

### Get Free Trial Access:

1. **Go to V0**: https://v0.dev

2. **Sign up with GitHub/Google**
   - Free plan available
   - Premium plan needed for API access (~$20/month)
   - **For Hackathon**: Sign up for free trial!

3. **Navigate to Settings**
   - Click your profile
   - Go to "API Keys"

---

## Step 2: Get Your API Key

1. In V0 settings, click **"Generate API Key"**

2. Copy the key immediately (you won't see it again!)

3. Add to `scripts/.env`:
   ```bash
   V0_API_KEY=v0_xxxxxxxxxxxxxxxxxxxxx
   ```

---

## Step 3: Choose Your Build Mode

You now have **3 build endpoints**:

### Option 1: Gemini Only (Original)
**Endpoint**: `POST /mcp/app/build`

**Use When**:
- No V0 API key
- Want faster builds
- Backend-heavy apps

**Example**:
```json
{
  "project_id": "proj123",
  "spec": {
    "name": "Todo App",
    "pages": ["Home"],
    "requirements": ["Build a todo app"]
  }
}
```

### Option 2: V0 + Gemini Hybrid (NEW!)
**Endpoint**: `POST /mcp/app/build/hybrid`

**Use When**:
- Have V0 API key
- Want beautiful UI
- Best for demos!

**Example**:
```json
{
  "project_id": "proj123",
  "spec": {
    "name": "Todo App",
    "pages": ["Home", "Dashboard"],
    "requirements": [
      "Build a modern todo app",
      "Beautiful UI with animations"
    ]
  },
  "use_v0": true
}
```

### Option 3: Streaming Mode (For Live Preview)
**Endpoint**: `POST /mcp/app/build/hybrid` (same, but uses SSE)

**Frontend Receives**:
- Real-time progress updates
- File-by-file generation
- Preview HTML
- GitHub repo URL
- Deployment status

---

## Step 4: Test the Integration

### Quick Test in Swagger UI:

1. **Start backend**:
   ```bash
   cd backend
   python3 main.py
   ```

2. **Go to**: http://localhost:8000/docs

3. **Find**: `POST /mcp/app/build/hybrid`

4. **Try this request**:
   ```json
   {
     "project_id": "test-001",
     "spec": {
       "name": "Landing Page",
       "pages": ["Home"],
       "requirements": [
         "Create a modern landing page",
         "Hero section with gradient",
         "Feature cards",
         "Call-to-action button"
       ]
     },
     "use_v0": true
   }
   ```

5. **Watch the magic**:
   - V0 generates beautiful UI
   - Gemini adds backend logic
   - Code pushed to GitHub
   - Preview HTML returned

---

## Step 5: Frontend Integration

### Update Your Frontend to Use Streaming:

```typescript
// frontend/src/hooks/useStreamingBuild.ts

export function useStreamingBuild() {
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [previewHtml, setPreviewHtml] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  
  async function startBuild(request: AppBuildRequest) {
    const response = await fetch(
      "http://localhost:8000/mcp/app/build/hybrid",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      }
    );
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");
      
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = JSON.parse(line.substring(6));
          
          switch (data.type) {
            case "status":
              setStatus(data.message);
              setProgress(data.progress);
              break;
              
            case "file_created":
              setFiles(prev => [...prev, data.filename]);
              break;
              
            case "preview_ready":
              setPreviewHtml(data.html);
              break;
              
            case "complete":
              // Done!
              return {
                repo_url: data.repo_url,
                app_url: data.app_url,
              };
              
            case "error":
              throw new Error(data.message);
          }
        }
      }
    }
  }
  
  return { startBuild, status, progress, previewHtml, files };
}
```

### Display Live Preview:

```typescript
// frontend/src/components/LiveBuildView.tsx

export function LiveBuildView() {
  const { startBuild, status, progress, previewHtml } = useStreamingBuild();
  
  return (
    <div className="grid grid-cols-2 gap-4 h-screen">
      {/* Left: Build Status */}
      <div className="p-6 bg-gray-50">
        <h2 className="text-xl font-bold mb-4">Build Progress</h2>
        <Progress value={progress} className="mb-4" />
        <p className="text-sm text-gray-600">{status}</p>
      </div>
      
      {/* Right: Live Preview */}
      <div className="relative">
        <iframe
          srcDoc={previewHtml}
          className={cn(
            "w-full h-full border-0",
            progress < 75 && "blur-sm opacity-50"
          )}
        />
        {progress < 75 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Architecture: How V0 + Gemini Work Together

### Flow Diagram:

```
User Prompt
    ↓
┌─────────────────────────────┐
│  Backend orchestrates:      │
├─────────────────────────────┤
│  1. V0 generates UI         │ ← Beautiful components
│     - page.tsx              │
│     - components/*.tsx      │
│     - Tailwind styles       │
│                             │
│  2. Gemini generates logic  │ ← Backend functionality
│     - API routes            │
│     - Server actions        │
│     - Utilities             │
│                             │
│  3. Combine both outputs    │
│  4. Push to GitHub          │
│  5. Deploy to Vercel        │
└─────────────────────────────┘
    ↓
Preview HTML + GitHub URL
```

### What Each AI Handles:

| Task | V0 | Gemini |
|------|-----|--------|
| UI Components |  |  |
| Tailwind Styling |  |  |
| shadcn/ui |  |  |
| Responsive Design |  |  |
| API Routes |  |  |
| Server Actions |  |  |
| Database Schema |  |  |
| Business Logic |  |  |

---

## Pricing & Free Trial Info

### V0 Pricing:

- **Free Tier**: Web UI only (no API access)
- **Premium**: ~$20/month with API access
- **Team**: Higher tier for teams

### For Hackathon:

1. **Sign up for free trial** (usually 7-14 days)
2. **Get API access during trial**
3. **Build your demo**
4. **Cancel before billing** (if needed)

### Alternative (If No V0):

You can still use the Gemini-only endpoint (`/mcp/app/build`) which works great and is **100% FREE**!

---

## Troubleshooting

### Issue: "V0_API_KEY not found"

**Solution**:
```bash
# Add to scripts/.env
V0_API_KEY=your_actual_key_here

# Restart backend
cd backend
python3 main.py
```

### Issue: V0 API returns 401

**Causes**:
- Invalid API key
- Free trial expired
- Need to upgrade to Premium

**Solution**:
- Check your V0 account status
- Regenerate API key
- Or set `"use_v0": false` in request

### Issue: Frontend not showing preview

**Solution**:
- Check browser console for errors
- Verify iframe srcDoc is set
- Test with simple HTML first

### Issue: Streaming not working

**Solution**:
- Use EventSource or fetch with streaming
- Check CORS settings
- Verify SSE headers in response

---

## Backend Engineer's Checklist

Your implementation is ready! Here's what you have:

- [x] V0 API client (`backend/integrations/v0_api.py`)
- [x] Gemini integration (already done)
- [x] Hybrid build endpoint (`/mcp/app/build/hybrid`)
- [x] Streaming support (SSE)
- [x] Preview HTML generator
- [x] GitHub integration
- [x] Environment variable setup

### Next Steps:

1. **Get V0 API key** from https://v0.dev
2. **Add to scripts/.env**
3. **Test in Swagger UI**
4. **Tell your frontend engineer** to use streaming endpoint
5. **Build amazing UIs** for your hackathon!

---

## Example: Full Request/Response

### Request to `/mcp/app/build/hybrid`:

```json
{
  "project_id": "hackathon-demo",
  "spec": {
    "name": "AI Startup Builder",
    "pages": ["Home", "Dashboard", "Projects"],
    "requirements": [
      "Modern landing page with hero section",
      "Dashboard with project cards",
      "Real-time project status updates",
      "Beautiful animations and transitions",
      "Dark mode support"
    ]
  },
  "use_v0": true
}
```

### Streaming Response (SSE):

```
data: {"type":"status","message":"🤔 Planning...","progress":5}

data: {"type":"status","message":"🎨 V0 generating UI...","progress":10}

data: {"type":"file_created","filename":"src/app/page.tsx","progress":20}

data: {"type":"file_created","filename":"src/components/Hero.tsx","progress":25}

data: {"type":"status","message":"🤖 Gemini adding backend...","progress":45}

data: {"type":"file_created","filename":"src/app/api/projects/route.ts","progress":55}

data: {"type":"preview_ready","html":"<!DOCTYPE html>...","progress":75}

data: {"type":"status","message":"📁 Pushing to GitHub...","progress":85}

data: {"type":"complete","repo_url":"https://github.com/...","progress":100}
```

---

## Summary

- **V0 API Key**: Get from https://v0.dev (free trial available)
- **Add to .env**: `V0_API_KEY=your_key_here`
- **Use hybrid endpoint**: `/mcp/app/build/hybrid`
- **Frontend**: Implement streaming with EventSource
- **Preview**: Show in iframe with blur effect
- **Fallback**: Gemini-only mode if V0 unavailable

**You're ready to build beautiful apps with V0 + Gemini!**

