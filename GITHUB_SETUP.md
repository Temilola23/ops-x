# GitHub Integration - Quick Setup Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Get Your GitHub Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: `OPS-X Development`
4. Select scope: **`repo`** (Full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### Step 2: Configure Backend

Create or edit `backend/.env`:

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here

# Backend Config
BACKEND_PORT=8000
```

Or add to `scripts/.env` if that's where your env file is.

### Step 3: Test It!

```bash
# Terminal 1 - Start Backend
cd backend
python main.py

# Terminal 2 - Start Frontend
cd frontend
npm run dev

# Terminal 3 - Open Browser
open http://localhost:3000
```

## 🎯 How to Use

1. **Enter Project Name**: e.g., "My Todo App"
2. **Describe Your App**: e.g., "Build a todo app with categories and due dates"
3. **Click "Build MVP"** - Wait for v0 to generate code
4. **Click "Push to GitHub"** - Your code is now on GitHub!
5. **Click "View on GitHub"** - Opens your new repo

## 🧪 Quick Test (API Only)

```bash
# Test GitHub integration
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "prompt": "A simple test app"
  }'

# You'll get back a project_id, use it below:
curl -X POST http://localhost:8000/api/projects/save-to-github \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_ID",
    "project_name": "Test Project",
    "files": [
      {
        "name": "README.md",
        "content": "# Test Project\n\nThis is a test."
      },
      {
        "name": "index.html",
        "content": "<!DOCTYPE html><html><body>Hello World</body></html>"
      }
    ],
    "description": "Test project from OPS-X"
  }'

# Check GitHub - you should see a new repo!
```

## ⚠️ Troubleshooting

### "401 Unauthorized"

❌ GitHub token missing or invalid
✅ **Fix**: Regenerate token with `repo` scope

### "Repository already exists"

❌ Repo name already taken in your account
✅ **Fix**: Use a different project name or delete the existing repo

### "403 Forbidden (rate limit)"

❌ Too many requests to GitHub API
✅ **Fix**: Wait 1 hour or use authenticated token (already done)

### CORS Error in Frontend

❌ Backend not running or wrong URL
✅ **Fix**: Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`

## 📋 Environment Variables Checklist

**Backend** (`backend/.env`):

- [x] `GITHUB_TOKEN` - Your personal access token
- [x] `BACKEND_PORT` - Usually 8000

**Frontend** (`frontend/.env.local`):

- [x] `NEXT_PUBLIC_API_URL` - Usually http://localhost:8000
- [x] `V0_API_KEY` - Your v0.dev API key

## 🎉 What You Get

After pushing to GitHub:

- ✅ New public repository
- ✅ All v0-generated files committed
- ✅ Auto-generated README with preview link
- ✅ Ready to deploy to Vercel
- ✅ Version control for your MVP

## 🔗 Useful Links

- [GitHub Token Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [v0.dev API Docs](https://v0.app/docs/api/platform/quickstart)
- [Full Architecture Docs](./docs/github_versioning.md)

## 🚀 Next Steps

After GitHub integration works:

1. Add user authentication
2. Implement stakeholder branching
3. Set up Vercel auto-deploy
4. Add conflict resolution
