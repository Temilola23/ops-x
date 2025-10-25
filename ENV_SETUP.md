# Environment Variables Setup

Create a file at `scripts/.env` with these values:

## Required API Keys

### 1. Google AI Studio API Key (REQUIRED)
```
GEMINI_API_KEY=your_key_here
```
**How to get it:**
- Go to: https://aistudio.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy the key (starts with `AIza...`)
- Free with good rate limits

### 2. GitHub Personal Access Token (REQUIRED)
```
GITHUB_TOKEN=your_token_here
```
**How to get it:**
- Go to: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scopes: `repo`, `workflow`
- Copy the token

### 3. Vercel Token (OPTIONAL)
```
VERCEL_TOKEN=your_token_here
```
**How to get it:**
- Go to: https://vercel.com/account/tokens
- Create new token
- Copy it

**Note:** Without Vercel token, apps will be pushed to GitHub but not deployed. You'll get the GitHub repo URL instead.

## Already Configured (No Action Needed)

```
# Janitor AI
JANITOR_API_ENDPOINT=https://janitorai.com/hackathon/completions
JANITOR_API_KEY=calhacks2047

# Fetch.ai
FETCHAI_API_KEY=sk_f1565b8c1c934a7ab641446e5b1f4159fb14f45afe964224b90e7f6cfedd55a5
FETCHAI_ENDPOINT=https://agentverse.ai

# Creao
CREAO_INVITATION_CODE=CALHAC
```

## Optional Keys

```
# Deepgram (for TTS)
DEEPGRAM_API_KEY=your_key_here
```

## Server Configuration

```
BACKEND_PORT=8000
FRONTEND_PORT=3000
MCP_SERVER_PORT=8080
NODE_ENV=development
DEBUG=true
```

## Database

```
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

## Complete Template

Copy this to `scripts/.env`:

```bash
# Google AI Studio API Key (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub Token (REQUIRED)
GITHUB_TOKEN=your_github_token_here

# Vercel Token (OPTIONAL)
VERCEL_TOKEN=your_vercel_token_here

# Already configured
JANITOR_API_ENDPOINT=https://janitorai.com/hackathon/completions
JANITOR_API_KEY=calhacks2047
FETCHAI_API_KEY=sk_f1565b8c1c934a7ab641446e5b1f4159fb14f45afe964224b90e7f6cfedd55a5
FETCHAI_ENDPOINT=https://agentverse.ai
CREAO_INVITATION_CODE=CALHAC

# Optional
DEEPGRAM_API_KEY=your_deepgram_key_here

# Server config
BACKEND_PORT=8000
FRONTEND_PORT=3000
CHROMA_HOST=localhost
CHROMA_PORT=8000
NODE_ENV=development
DEBUG=true
```
