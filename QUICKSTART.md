#  OPS-X Quick Start Guide

## Step 1: Both Team Members (First 30 minutes)

### Environment Setup
```bash
# 1. Clone and setup
cd ops-x
cp .env.example .env

# 2. Add these keys to .env (get from Slack/registration):
CREAO_INVITATION_CODE=<get-from-creao-registration>
JANITOR_API_KEY=<get-from-slack-#spons-janitor>
JANITOR_API_ENDPOINT=https://janitorai.com/hackathon/completions
FETCHAI_CODE_CALHACK2025=<for-ASI:One-Pro>
GITHUB_TOKEN=<your-github-pat>

# 3. Install dependencies
make setup  # or manually:
# Backend: cd backend && pip install -r requirements.txt
# Frontend: cd frontend && npm install
```

### Register on Platforms
1. **Creao**: Go to challenge page, click "Register Challenge" for invitation code
2. **Fetch.ai**: Use codes CalHack2025 and CalHack2025AV
3. **Join Slack channels**: #spons-creao, #spons-janitor, #spons-fetchai

---

## Step 2: Quick Test Setup (Next 30 minutes)

### Person A: Test Backend
```bash
cd backend
python main.py
# Should see: " Starting OPS-X Backend Server..."
# API docs at: http://localhost:8000/docs
```

### Person B: Test Frontend
```bash
cd frontend
npm run dev
# Should see: "VITE ready at http://localhost:5173"
```

---

## Step 3: First Working Feature (Hours 1-2)

### BOTH: Implement Basic Creao Integration

**Person A** - In `backend/mcp/creao_build.py`:
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CreaoRequest(BaseModel):
    project_id: str
    prompt: str

@router.post("/creao/build")
async def build_app(request: CreaoRequest):
    # TODO: Call Creao API
    return {"status": "building", "project_id": request.project_id}
```

**Person B** - In `frontend/src/components/CreaoPromptInput.tsx`:
```tsx
export const CreaoPromptInput = () => {
  const [prompt, setPrompt] = useState('');
  
  const handleSubmit = async () => {
    const response = await fetch('http://localhost:8000/mcp/creao/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        project_id: `opsx_${Date.now()}`,
        prompt 
      })
    });
  };
  
  return (
    <div>
      <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <button onClick={handleSubmit}>Build with Creao</button>
    </div>
  );
};
```

---

## Step 4: Branch Strategy

```bash
# Person A
git checkout -b feat/backend-integrations
git push -u origin feat/backend-integrations

# Person B  
git checkout -b feat/frontend-agents
git push -u origin feat/frontend-agents

# Create PR when ready
gh pr create --title "Backend: Creao and Janitor integration" --body "Implements MCP endpoints"
```

---

## 🔥 Hot Tips

1. **API Keys**: Keep them in a shared secure note
2. **Test Early**: Get one feature working end-to-end before adding more
3. **Use the Workshops**: 
   - Friday 20:00 - Creao & Fetch.ai workshops
   - Saturday 10:00 - Creao API workshop
4. **Ask for Help**: Sponsors are there to help you win their prizes!

---

## 📞 Emergency Contacts

- **Teammate Phone**: _______________
- **Backup Plan**: If one integration fails, pivot to another sponsor
- **Demo Backup**: Record working features as you go

---

## Ready? Let's Go! 🎯

1.  Environment setup complete
2.  Both can see backend and frontend running
3.  First API call working
4.  Start building the future!

Remember: It's a hackathon - done is better than perfect!
