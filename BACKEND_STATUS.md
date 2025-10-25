# Backend Status - Ready for One-Prompt Build

## What's Working

### 1. Projects API (NEW)
- POST /api/projects - Create project
- GET /api/projects - List all projects
- GET /api/projects/{id} - Get single project
- PATCH /api/projects/{id} - Update project
- DELETE /api/projects/{id} - Delete project

### 2. MCP Build Endpoint (CORE)
- POST /mcp/app/build - One-prompt app generation
  - Takes: project_id, spec (name, requirements, pages, entities)
  - Returns: repo_url, app_url, status

### 3. Other MCP Endpoints (Stubs)
- POST /mcp/chat/send - Janitor AI multiplayer (WORKING)
- POST /mcp/repo/patch - GitHub operations (stub)
- POST /mcp/conflict/scan - Conflict detection (stub)
- POST /mcp/pitch/generate - Pitch generation (stub)
- POST /mcp/yc/pack - YC pack generator (stub)
- POST /mcp/postman/export - Postman flow export (stub)

## What Frontend Expects

### Flow:
1. User enters project name and prompt in `CreaoPromptInput`
2. Frontend calls `POST /api/projects` with {name, prompt}
3. Frontend gets back project {id, name, prompt, status: "pending"}
4. Frontend calls `POST /mcp/app/build` with project_id and spec
5. Backend:
   - Uses Gemini to generate code
   - Creates GitHub repo
   - Pushes code to GitHub
   - Deploys to Vercel
6. Frontend gets back {repo_url, app_url, status: "success"}

## What You Need to Test End-to-End

### Required API Keys in scripts/.env:
```bash
GEMINI_API_KEY=your_gemini_key_here
GITHUB_TOKEN=your_github_pat_here
VERCEL_TOKEN=your_vercel_token_here
```

### Get Keys From:
1. **Gemini**: https://aistudio.google.com/app/apikey
2. **GitHub**: https://github.com/settings/tokens/new
   - Permissions: repo (all), workflow
3. **Vercel**: https://vercel.com/account/tokens

## Testing Steps

### 1. Start Backend:
```bash
cd backend
python3 main.py
```

### 2. Test Projects API (Swagger):
Go to http://localhost:8000/docs

Try POST /api/projects:
```json
{
  "name": "Todo App",
  "prompt": "Build a simple todo app with Next.js"
}
```

### 3. Test App Build (Swagger):
Use the project_id from step 2

Try POST /mcp/app/build:
```json
{
  "project_id": "your-project-id-here",
  "spec": {
    "name": "Todo App",
    "entities": [],
    "pages": ["Home", "TodoList"],
    "requirements": [
      "Build a simple todo app",
      "Use Next.js and TypeScript",
      "Add task creation and deletion"
    ]
  }
}
```

### 4. Check Results:
- repo_url: Should point to new GitHub repo
- app_url: Should point to deployed Vercel app

## Next Steps

1. **Add API keys** to scripts/.env
2. **Test the flow** in Swagger UI
3. **Start frontend** to test UI
4. **Verify GitHub repo** is created
5. **Verify Vercel deployment** works

