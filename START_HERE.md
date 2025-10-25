# 🚀 Quick Start Guide - OPS-X

## ⚡ Get Running in 5 Minutes

### Prerequisites Check

```bash
# Check if you have the required tools
python3 --version  # Should be 3.9+
node --version     # Should be 18+
npm --version      # Should be 9+
```

## 📋 Setup Steps

### Step 1: Environment Variables

**Backend Environment:**

```bash
# Create backend environment file
cat > scripts/.env << 'EOF'
# GitHub Integration (REQUIRED)
GITHUB_TOKEN=ghp_your_github_token_here

# Server Config
BACKEND_PORT=8000
EOF
```

**Get GitHub Token:**

1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "OPS-X Development"
4. Scopes: Select **`repo`** ✅
5. Generate and copy token
6. Replace `ghp_your_github_token_here` in `scripts/.env`

**Frontend Environment:**

```bash
# Create frontend environment file
cat > frontend/.env.local << 'EOF'
# V0.dev Integration (REQUIRED)
V0_API_KEY=v0_your_api_key_here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

**Get V0 API Key:**

1. Visit: https://v0.dev
2. Sign in
3. Go to Settings → API Keys
4. Create new key
5. Replace `v0_your_api_key_here` in `frontend/.env.local`

### Step 2: Install Backend Dependencies

```bash
cd backend

# Option 1: Use virtual environment (RECOMMENDED)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR: venv\Scripts\activate  # On Windows

pip install --upgrade pip
pip install fastapi uvicorn python-dotenv httpx PyGithub pydantic

# Option 2: Install all dependencies (may take longer)
# pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend

# Install dependencies (if not done already)
npm install

# Should already have v0-sdk from previous setup
# If not: npm install v0-sdk
```

### Step 4: Start Backend

```bash
cd backend

# If using venv, activate it first
source venv/bin/activate  # (if you created one)

# Start the server
python3 main.py

# You should see:
# ✅ Loaded environment from /path/to/scripts/.env
# 🚀 Starting OPS-X Backend Server...
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this terminal running!**

### Step 5: Start Frontend (New Terminal)

```bash
cd frontend

# Start the dev server
npm run dev

# You should see:
# ✓ Ready in 2s
# ○ Local:   http://localhost:3000
```

**Leave this terminal running!**

### Step 6: Test It! 🎉

Open your browser: **http://localhost:3000**

## 🧪 Test the Complete Flow

### 1. Create Your First MVP

1. **Project Name**: "My Todo App"
2. **Prompt**: "Build a modern todo app with categories, priorities, and due dates. Use a clean, minimal design with shadcn/ui components."
3. Click **"Build MVP"**
4. Wait ~30 seconds for v0 to generate

### 2. Explore the Preview

- Switch between **Preview** and **Code** tabs
- See your app running in the iframe
- Browse through generated files

### 3. Push to GitHub

1. Click **"Push to GitHub"**
2. Wait ~5 seconds
3. See **"View on GitHub"** button appear
4. Click it to open your new repository!

### 4. Verify on GitHub

You should see:

- ✅ New repository: `my-todo-app`
- ✅ All v0-generated files committed
- ✅ README.md with v0 preview link
- ✅ Ready to deploy to Vercel!

## 🐛 Troubleshooting

### Backend won't start

**Error: `ModuleNotFoundError: No module named 'fastapi'`**

```bash
cd backend
pip install fastapi uvicorn python-dotenv httpx PyGithub pydantic
```

**Error: `GITHUB_TOKEN not found`**

```bash
# Check if .env file exists
cat scripts/.env

# If not, create it with your token
echo 'GITHUB_TOKEN=ghp_your_actual_token' > scripts/.env
```

**Error: Port 8000 already in use**

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
BACKEND_PORT=8001 python3 main.py
```

### Frontend won't start

**Error: `Cannot find module 'v0-sdk'`**

```bash
cd frontend
npm install v0-sdk
```

**Error: `V0_API_KEY is not defined`**

```bash
# Create .env.local
echo 'V0_API_KEY=v0_your_key' > frontend/.env.local
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' >> frontend/.env.local
```

### GitHub Push Fails

**Error: "401 Unauthorized"**

- Your GitHub token is invalid or expired
- Get a new token from https://github.com/settings/tokens
- Make sure it has `repo` scope

**Error: "Repository already exists"**

- Change your project name
- Or delete the existing repo on GitHub

### v0 Generation Fails

**Error: "Failed to create chat with v0"**

- Your v0 API key is invalid
- Get a new key from https://v0.dev/settings
- Make sure it's in `frontend/.env.local`

## 📊 Check Everything is Working

### Backend Health Check

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Backend API Docs

Open: http://localhost:8000/docs

- You should see interactive API documentation
- Try the endpoints!

### Frontend

Open: http://localhost:3000

- You should see the OPS-X landing page
- "Build Your MVP" section

## 🎯 What You Can Do Now

1. **Generate MVPs**: Describe any app idea, get working code
2. **Preview Live**: See your app running in real-time
3. **Iterate Fast**: Refine your app with follow-up prompts
4. **Version Control**: Push to GitHub with one click
5. **Deploy**: Take the GitHub repo and deploy to Vercel

## 📁 Project Structure

```
ops-x/
├── backend/               # FastAPI server
│   ├── api/              # REST endpoints
│   │   └── projects.py   # GitHub integration ✨
│   ├── integrations/     # External APIs
│   │   └── github_api.py # GitHub client
│   └── main.py          # Server entry point
├── frontend/             # Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   └── actions/
│   │   │       └── v0.ts # v0 Server Actions
│   │   ├── components/
│   │   │   └── BuildWithPreview.tsx # Main UI ✨
│   │   └── services/
│   │       └── api.ts   # Backend API client
│   └── .env.local       # Frontend env vars
└── scripts/
    └── .env             # Backend env vars
```

## 🚀 Next Steps

1. **Test the flow** - Build a simple app
2. **Read the docs**:

   - `/docs/github_versioning.md` - Architecture
   - `/IMPLEMENTATION_SUMMARY.md` - Full details
   - `/ARCHITECTURE_DECISION.md` - Design decisions

3. **Deploy to production**:

   - Backend: Railway, Render, or AWS
   - Frontend: Vercel (recommended)

4. **Extend the platform**:
   - Add user authentication
   - Implement multi-stakeholder branching
   - Add conflict resolution

## 💡 Tips

- **Use descriptive prompts**: The more specific you are, the better v0 generates
- **Iterate quickly**: Use the refine feature to tweak your app
- **Check the code**: Review generated files before pushing to GitHub
- **Deploy fast**: GitHub repos are ready for Vercel deployment

## 🆘 Need Help?

1. Check terminal output for error messages
2. Review the documentation in `/docs/`
3. Check backend logs: Look at the terminal running `python3 main.py`
4. Check frontend logs: Look at browser console (F12)

## 🎉 You're Ready!

Everything is set up. Time to build amazing MVPs! 🚀

---

**Status**: ✅ Ready to run
**Time to first MVP**: ~5 minutes
**Documentation**: Complete
**Architecture**: Production-ready
