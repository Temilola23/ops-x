# Frontend Implementation Guide: Auth + Stakeholder Management

**For**: Frontend Engineer
**Task**: Implement authentication + team management UI
**Backend**: Already complete and tested

---

## 🎯 What You Need to Build

### 1. Authentication Modal (Sign Up / Login with OTP)
### 2. Team Management Dashboard
### 3. Updated Homepage with Auth Options

---

## 📋 Backend Endpoints (Already Built!)

All endpoints return JSON with this structure:
```typescript
{
  success: boolean
  data?: any
  error?: string
}
```

### Auth Endpoints

#### `POST /api/auth/signup`
```typescript
// Request
{
  email: string
  name: string
}

// Response
{
  success: true
  message: "OTP sent to email. Check console for demo OTP: 123456"
}
```

####  `POST /api/auth/verify-otp`
```typescript
// Request
{
  email: string
  otp: string
}

// Response
{
  success: true
  user_id: number
  email: string
  name: string
  session_token: string  // Store this in localStorage!
  message: "Authentication successful"
}
```

#### `GET /api/auth/me?session_token={token}`
```typescript
// Response
{
  success: true
  user: {
    id: number
    email: string
    name: string
    created_at: string
  }
}
```

#### `POST /api/auth/logout?session_token={token}`
```typescript
// Response
{
  success: true
  message: "Logged out successfully"
}
```

### Stakeholder Endpoints

#### `POST /api/projects/{project_id}/invite`
```typescript
// Request
{
  name: string
  email: string
  role: "Founder" | "Frontend" | "Backend" | "Investor" | "Facilitator"
}

// Response
{
  success: true
  data: {
    stakeholder_id: number
    email: string
    role: string
    otp: string  // Demo only! Show this to user
    message: "Invitation sent to user@email.com. Demo OTP: 123456"
  }
}
```

#### `GET /api/projects/{project_id}/stakeholders`
```typescript
// Response
{
  success: true
  data: [
    {
      id: number
      project_id: number
      name: string
      email: string
      role: string
      github_branch: string | null
      created_at: string
    }
  ]
}
```

---

## 🎨 UI Components to Build

### Component 1: AuthModal.tsx

**Location**: `frontend/src/components/AuthModal.tsx`

**Features**:
- Sign Up / Login tabs
- Email + Name input (sign up) or Email only (login)
- OTP input step
- Auto-display OTP in demo mode (from backend response)
- Store `session_token` in localStorage
- Close modal after successful auth

**Flow**:
```
Step 1: User enters email + name → POST /api/auth/signup
Step 2: Backend returns OTP (shown in console + response)
Step 3: User enters OTP → POST /api/auth/verify-otp
Step 4: Store session_token → Redirect to dashboard
```

**Example Code**:
```typescript
'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: (user: any) => void
}

export function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [step, setStep] = useState<'email' | 'otp'>('email')
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [otp, setOtp] = useState('')
  const [demoOtp, setDemoOtp] = useState('') // Show OTP from backend
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSignup = async () => {
    setLoading(true)
    setError('')
    
    try {
      const res = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name })
      })
      
      const data = await res.json()
      
      if (data.success) {
        // Extract OTP from message (for demo)
        const otpMatch = data.message.match(/OTP: (\d{6})/)
        if (otpMatch) {
          setDemoOtp(otpMatch[1])
        }
        setStep('otp')
      } else {
        setError(data.error || 'Failed to send OTP')
      }
    } catch (err) {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async () => {
    setLoading(true)
    setError('')
    
    try {
      const res = await fetch('http://localhost:8000/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp })
      })
      
      const data = await res.json()
      
      if (data.success) {
        // Store session token
        localStorage.setItem('ops_x_session', data.session_token)
        localStorage.setItem('ops_x_user', JSON.stringify({
          id: data.user_id,
          email: data.email,
          name: data.name
        }))
        
        onSuccess?.(data)
        onClose()
      } else {
        setError(data.error || 'Invalid OTP')
      }
    } catch (err) {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Sign Up / Login</DialogTitle>
        </DialogHeader>

        {step === 'email' ? (
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
              />
            </div>
            
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>

            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}

            <Button
              onClick={handleSignup}
              disabled={!email || !name || loading}
              className="w-full"
            >
              {loading ? 'Sending OTP...' : 'Continue'}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <Label htmlFor="otp">Enter OTP</Label>
              <Input
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="000000"
                maxLength={6}
              />
              {demoOtp && (
                <p className="text-xs text-muted-foreground mt-1">
                  Demo OTP: <strong>{demoOtp}</strong>
                </p>
              )}
            </div>

            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}

            <Button
              onClick={handleVerifyOtp}
              disabled={otp.length !== 6 || loading}
              className="w-full"
            >
              {loading ? 'Verifying...' : 'Verify & Login'}
            </Button>

            <Button
              variant="ghost"
              onClick={() => setStep('email')}
              className="w-full"
            >
              Back
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
```

---

### Component 2: TeamManagementDashboard.tsx

**Location**: `frontend/src/app/dashboard/[projectId]/team/page.tsx`

**Features**:
- List all team members
- Add new team member (name, email, role)
- Show invite OTP in demo mode
- Delete team member
- Show GitHub branch for each member

**Example Code**:
```typescript
'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

interface Stakeholder {
  id: number
  name: string
  email: string
  role: string
  github_branch: string | null
  created_at: string
}

export default function TeamDashboard() {
  const params = useParams()
  const projectId = params.projectId

  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([])
  const [showInvite, setShowInvite] = useState(false)
  const [inviteForm, setInviteForm] = useState({
    name: '',
    email: '',
    role: 'Frontend'
  })
  const [inviteOtp, setInviteOtp] = useState('')

  useEffect(() => {
    loadStakeholders()
  }, [projectId])

  const loadStakeholders = async () => {
    const res = await fetch(`http://localhost:8000/api/projects/${projectId}/stakeholders`)
    const data = await res.json()
    if (data.success) {
      setStakeholders(data.data)
    }
  }

  const handleInvite = async () => {
    const res = await fetch(`http://localhost:8000/api/projects/${projectId}/invite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inviteForm)
    })

    const data = await res.json()
    
    if (data.success) {
      setInviteOtp(data.data.otp)
      loadStakeholders()
      // Reset form after 5 seconds
      setTimeout(() => {
        setShowInvite(false)
        setInviteOtp('')
        setInviteForm({ name: '', email: '', role: 'Frontend' })
      }, 5000)
    }
  }

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      'Founder': 'bg-purple-500',
      'Frontend': 'bg-blue-500',
      'Backend': 'bg-green-500',
      'Investor': 'bg-yellow-500',
      'Facilitator': 'bg-pink-500'
    }
    return colors[role] || 'bg-gray-500'
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Team Management</h1>
        <Button onClick={() => setShowInvite(!showInvite)}>
          {showInvite ? 'Cancel' : 'Invite Team Member'}
        </Button>
      </div>

      {showInvite && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Invite Team Member</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={inviteForm.name}
                onChange={(e) => setInviteForm({ ...inviteForm, name: e.target.value })}
                placeholder="John Doe"
              />
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={inviteForm.email}
                onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                placeholder="john@example.com"
              />
            </div>

            <div>
              <Label htmlFor="role">Role</Label>
              <Select
                value={inviteForm.role}
                onValueChange={(value) => setInviteForm({ ...inviteForm, role: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Founder">Founder</SelectItem>
                  <SelectItem value="Frontend">Frontend Engineer</SelectItem>
                  <SelectItem value="Backend">Backend Engineer</SelectItem>
                  <SelectItem value="Investor">Investor</SelectItem>
                  <SelectItem value="Facilitator">Facilitator</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {inviteOtp && (
              <div className="bg-green-50 border border-green-200 p-4 rounded">
                <p className="text-sm font-semibold text-green-800">Invitation Sent!</p>
                <p className="text-xs text-green-600 mt-1">
                  Demo OTP: <strong className="text-lg">{inviteOtp}</strong>
                </p>
                <p className="text-xs text-gray-600 mt-2">
                  Share this OTP with {inviteForm.email} to sign up.
                </p>
              </div>
            )}

            <Button
              onClick={handleInvite}
              disabled={!inviteForm.name || !inviteForm.email}
              className="w-full"
            >
              Send Invitation
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {stakeholders.map((member) => (
          <Card key={member.id}>
            <CardContent className="flex items-center justify-between p-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg">
                  {member.name.charAt(0).toUpperCase()}
                </div>
                
                <div>
                  <h3 className="font-semibold text-lg">{member.name}</h3>
                  <p className="text-sm text-muted-foreground">{member.email}</p>
                  {member.github_branch && (
                    <p className="text-xs text-blue-600 mt-1">
                      Branch: {member.github_branch}
                    </p>
                  )}
                </div>
              </div>

              <Badge className={getRoleBadgeColor(member.role)}>
                {member.role}
              </Badge>
            </CardContent>
          </Card>
        ))}

        {stakeholders.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <p className="text-muted-foreground">No team members yet. Invite your first team member!</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
```

---

### Component 3: Updated Homepage with Auth

**Location**: `frontend/src/app/page.tsx`

**Changes Needed**:
1. Add "Sign In" button in navbar
2. After project creation, show prompt: "Invite your team?"
3. If yes → Show AuthModal
4. After auth → Redirect to team dashboard

**Example Code** (additions):
```typescript
'use client'

import { useState } from 'react'
import { AuthModal } from '@/components/AuthModal'

export default function Home() {
  const [showAuth, setShowAuth] = useState(false)
  const [projectId, setProjectId] = useState<number | null>(null)

  const handleProjectCreated = (project: any) => {
    setProjectId(project.id)
    
    // Ask if they want to invite team
    const inviteTeam = confirm('Project created! Do you want to invite your team?')
    
    if (inviteTeam) {
      setShowAuth(true)
    } else {
      // Go to project view
      window.open(`/dashboard/${project.id}`, '_blank')
    }
  }

  const handleAuthSuccess = (user: any) => {
    // Redirect to team dashboard
    if (projectId) {
      window.location.href = `/dashboard/${projectId}/team`
    }
  }

  return (
    <>
      <div className="min-h-screen">
        {/* Add to navbar */}
        <header className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold">OPS-X</h1>
            <button
              onClick={() => setShowAuth(true)}
              className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
            >
              Sign In
            </button>
          </div>
        </header>

        {/* Existing content */}
        {/* ... */}
      </div>

      <AuthModal
        isOpen={showAuth}
        onClose={() => setShowAuth(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  )
}
```

---

## 🔧 Helper Functions

### `lib/auth.ts`
```typescript
export interface User {
  id: number
  email: string
  name: string
}

export function getSessionToken(): string | null {
  return localStorage.getItem('ops_x_session')
}

export function getCurrentUser(): User | null {
  const userStr = localStorage.getItem('ops_x_user')
  return userStr ? JSON.parse(userStr) : null
}

export function isAuthenticated(): boolean {
  return !!getSessionToken()
}

export async function logout() {
  const token = getSessionToken()
  if (token) {
    await fetch(`http://localhost:8000/api/auth/logout?session_token=${token}`, {
      method: 'POST'
    })
  }
  localStorage.removeItem('ops_x_session')
  localStorage.removeItem('ops_x_user')
  window.location.href = '/'
}

export async function checkAuth(): Promise<User | null> {
  const token = getSessionToken()
  if (!token) return null

  try {
    const res = await fetch(`http://localhost:8000/api/auth/me?session_token=${token}`)
    const data = await res.json()
    
    if (data.success) {
      return data.user
    }
    return null
  } catch {
    return null
  }
}
```

---

## 🎯 Implementation Checklist

### Phase 1: Auth Modal (1-2 hours)
- [ ] Create `AuthModal.tsx` component
- [ ] Implement email + name input
- [ ] Implement OTP verification
- [ ] Store session token in localStorage
- [ ] Add to homepage navbar

### Phase 2: Team Dashboard (1-2 hours)
- [ ] Create team dashboard page
- [ ] List stakeholders with roles
- [ ] Add team invitation form
- [ ] Display demo OTP after invitation
- [ ] Show GitHub branches

### Phase 3: Integration (30 min)
- [ ] Update homepage to show auth prompt after project creation
- [ ] Redirect to team dashboard after auth
- [ ] Add logout button
- [ ] Test full flow

---

## 🎬 Demo Flow (For Judges)

1. **Anonymous Project Creation**
   - User creates project without signing in
   - Project saved in database

2. **Team Invitation Prompt**
   - After project creation: "Invite your team?"
   - User clicks "Yes" → Auth modal opens

3. **Sign Up**
   - User enters email + name
   - Backend returns OTP (shown in UI for demo)
   - User enters OTP → Logged in

4. **Claim Project Ownership**
   - User now owns the project
   - Redirect to team dashboard

5. **Invite Team Member**
   - Click "Invite Team Member"
   - Enter name, email, role
   - Backend returns demo OTP
   - Show OTP to user (they share with team member)

6. **Team Member Signs Up**
   - Team member uses same OTP flow
   - Linked to stakeholder record
   - Can see their assigned branch

---

## 🔥 Tips

1. **Use shadcn/ui** - Already installed, consistent design
2. **localStorage for session** - Simple for MVP
3. **Show OTPs in UI** - For demo, don't hide them
4. **Error handling** - Show user-friendly messages
5. **Loading states** - Add spinners for API calls

---

## 🐛 Testing

### Test Auth Flow
```bash
# 1. Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User"}'

# Response: {"success":true,"message":"OTP sent... Demo OTP: 123456"}

# 2. Verify OTP
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","otp":"123456"}'

# Response: {"success":true,"session_token":"abc...","user_id":1}
```

### Test Team Invitation
```bash
# 1. Invite team member
curl -X POST http://localhost:8000/api/projects/1/invite \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","role":"Frontend"}'

# Response: {"success":true,"data":{"otp":"654321"}}

# 2. List team
curl http://localhost:8000/api/projects/1/stakeholders

# Response: {"success":true,"data":[...]}
```

---

## 📝 Notes

- **OTP Storage**: In-memory for demo (30min expiry)
- **Production**: Replace with email service (SendGrid, Postmark)
- **OAuth**: Placeholder endpoints for Google/GitHub (not implemented)
- **Sessions**: 7-day expiry
- **Project Ownership**: First user to auth after creation claims ownership

---

**Questions?** Ask the backend engineer (me)! All endpoints are tested and working.

**Next Steps**: After you finish Auth + Team UI, backend engineer will handle refinement logic and V0 chat continuation.

