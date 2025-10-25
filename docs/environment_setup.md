# Environment Setup Guide

## Backend Environment Variables

The backend looks for environment variables in this order:

1. `scripts/.env` (recommended)
2. `backend/.env`
3. System environment variables

### Required Variables

Create `scripts/.env` with these values:

```bash
# ============================================
# GitHub Integration (REQUIRED)
# ============================================
# Get your token from: https://github.com/settings/tokens
# Required scopes: repo
GITHUB_TOKEN=ghp_your_github_personal_access_token_here

# ============================================
# Server Configuration
# ============================================
BACKEND_PORT=8000

# ============================================
# CORS Configuration
# ============================================
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Optional API Keys

These are used for advanced features:

```bash
# CodeRabbit - AI Code Review
CODERABBIT_API_KEY=your_coderabbit_api_key

# Janitor AI - Conflict Resolution
JANITOR_API_KEY=your_janitor_api_key

# Fetch.ai - Agent Deployment
FETCHAI_API_KEY=your_fetchai_api_key

# Google Gemini - AI Assistant
GEMINI_API_KEY=your_gemini_api_key

# Deepgram - Voice/Audio Processing
DEEPGRAM_API_KEY=your_deepgram_api_key

# Postman - API Testing
POSTMAN_API_KEY=your_postman_api_key
```

## Frontend Environment Variables

Create `frontend/.env.local`:

```bash
# ============================================
# v0.dev Integration (REQUIRED)
# ============================================
# Get your key from: https://v0.dev/settings/api
V0_API_KEY=v0_your_api_key_here

# ============================================
# Backend API URL
# ============================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============================================
# WebSocket URL (Future)
# ============================================
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## How to Get API Keys

### GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "OPS-X Development"
4. Scopes: Select **`repo`**
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)

### v0.dev API Key

1. Go to https://v0.dev
2. Sign in with your account
3. Navigate to Settings > API Keys
4. Create a new API key
5. Copy the key

### Other API Keys

See [sponsors.md](./sponsors.md) for details on:

- CodeRabbit: https://coderabbit.ai
- Janitor AI: https://janitorai.com
- Fetch.ai: https://fetch.ai
- Deepgram: https://deepgram.com

## Verification

### Backend

```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv('../scripts/.env'); print('GITHUB_TOKEN:', 'SET' if os.getenv('GITHUB_TOKEN') else 'MISSING')"
```

### Frontend

```bash
cd frontend
node -e "require('dotenv').config({path: '.env.local'}); console.log('V0_API_KEY:', process.env.V0_API_KEY ? 'SET' : 'MISSING')"
```

## Security Best Practices

### ✅ DO

- Keep `.env` files local (never commit)
- Use different tokens for dev/prod
- Rotate tokens regularly
- Use minimum required scopes

### ❌ DON'T

- Commit `.env` files to git
- Share tokens in chat/email
- Use production tokens in development
- Give tokens unnecessary scopes

## Deployment

For production deployment, set environment variables in your hosting platform:

### Vercel (Frontend)

```bash
vercel env add V0_API_KEY
vercel env add NEXT_PUBLIC_API_URL
```

### Railway/Render (Backend)

Set in dashboard:

- `GITHUB_TOKEN`
- `BACKEND_PORT`
- `CORS_ORIGINS`

## Troubleshooting

### "GITHUB_TOKEN not found"

**Problem**: Backend can't find the token
**Solution**: Create `scripts/.env` with `GITHUB_TOKEN=...`

### "401 Unauthorized" from GitHub

**Problem**: Token invalid or expired
**Solution**: Regenerate token with `repo` scope

### "V0_API_KEY not found"

**Problem**: Frontend can't find v0 key
**Solution**: Create `frontend/.env.local` with `V0_API_KEY=...`

### CORS Errors

**Problem**: Frontend can't reach backend
**Solution**: Check `NEXT_PUBLIC_API_URL` matches backend URL
