'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogFooter 
} from '@/components/ui/dialog'
import { Users, UserPlus, Mail, Calendar, RefreshCw, Trash2, Loader2 } from 'lucide-react'
import { useUser } from '@clerk/nextjs'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Stakeholder {
  id: number
  name: string
  email: string
  role: string
  status?: string
  github_branch: string | null
  created_at: string
}

export default function TeamDashboard() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.projectId as string
  const { user, isLoaded } = useUser()

  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([])
  const [showInvite, setShowInvite] = useState(false)
  const [loading, setLoading] = useState(false)
  const [inviteForm, setInviteForm] = useState({
    name: '',
    email: '',
    role: 'Frontend'
  })
  
  // Delete confirmation dialog
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean
    stakeholder: Stakeholder | null
  }>({ open: false, stakeholder: null })

  // Resend invite state
  const [resendingId, setResendingId] = useState<number | null>(null)

  useEffect(() => {
    loadStakeholders()
  }, [projectId])

  const loadStakeholders = async () => {
    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}/stakeholders`)
      const data = await res.json()
      if (data.success) {
        setStakeholders(data.data)
      }
    } catch (err) {
      console.error('Failed to load stakeholders:', err)
      toast.error('Failed to load team members')
    }
  }

  const handleInvite = async () => {
    if (!inviteForm.name || !inviteForm.email) {
      toast.error('Please fill in all fields')
      return
    }

    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}/invite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inviteForm)
      })

      const data = await res.json()
      
      if (data.success) {
        toast.success(data.data.message || 'Invitation sent successfully!')
        loadStakeholders()
        
        // Reset form
        setTimeout(() => {
          setShowInvite(false)
          setInviteForm({ name: '', email: '', role: 'Frontend' })
        }, 1500)
      } else {
        toast.error(data.error || 'Failed to send invitation')
      }
    } catch (err) {
      toast.error('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleResendInvite = async (stakeholder: Stakeholder) => {
    setResendingId(stakeholder.id)

    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}/invite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: stakeholder.name,
          email: stakeholder.email,
          role: stakeholder.role
        })
      })

      const data = await res.json()
      
      if (data.success) {
        toast.success(`Invitation resent to ${stakeholder.email}`)
      } else {
        toast.error(data.error || 'Failed to resend invitation')
      }
    } catch (err) {
      toast.error('Network error. Please try again.')
    } finally {
      setResendingId(null)
    }
  }

  const confirmDelete = (stakeholder: Stakeholder) => {
    setDeleteDialog({ open: true, stakeholder })
  }

  const handleDelete = async () => {
    if (!deleteDialog.stakeholder) return

    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}/stakeholders/${deleteDialog.stakeholder.id}`, {
        method: 'DELETE'
      })

      const data = await res.json()

      if (data.success) {
        toast.success(`${deleteDialog.stakeholder.name} removed from team`)
        loadStakeholders()
      } else {
        toast.error(data.error || 'Failed to remove team member')
      }
    } catch (err) {
      toast.error('Failed to remove team member')
    } finally {
      setDeleteDialog({ open: false, stakeholder: null })
    }
  }

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      'Founder': 'bg-purple-500 hover:bg-purple-600',
      'Frontend': 'bg-blue-500 hover:bg-blue-600',
      'Backend': 'bg-green-500 hover:bg-green-600',
      'Investor': 'bg-yellow-500 hover:bg-yellow-600',
      'Facilitator': 'bg-pink-500 hover:bg-pink-600'
    }
    return colors[role] || 'bg-gray-500 hover:bg-gray-600'
  }

  const getStatusBadgeColor = (status?: string) => {
    if (status === 'active') return 'bg-green-100 text-green-800'
    if (status === 'pending') return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  if (!isLoaded) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Users className="h-6 w-6 text-purple-600" />
            <h1 className="text-2xl font-bold">Team Management</h1>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => router.push('/workspace')}>
              Back to Workspace
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Members</p>
                  <p className="text-3xl font-bold">{stakeholders.length}</p>
                </div>
                <Users className="h-10 w-10 text-purple-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active</p>
                  <p className="text-3xl font-bold">
                    {stakeholders.filter(s => s.status === 'active').length}
                  </p>
                </div>
                <Calendar className="h-10 w-10 text-green-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending</p>
                  <p className="text-3xl font-bold">
                    {stakeholders.filter(s => s.status !== 'active').length}
                  </p>
                </div>
                <Mail className="h-10 w-10 text-yellow-600 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Invite Form */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Team Members</h2>
          <Button
            onClick={() => setShowInvite(!showInvite)}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            {showInvite ? 'Cancel' : 'Invite Member'}
          </Button>
        </div>

        {showInvite && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Invite Team Member</CardTitle>
              <CardDescription>
                Send an invitation email with OTP to join the project
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={inviteForm.name}
                    onChange={(e) => setInviteForm({ ...inviteForm, name: e.target.value })}
                    placeholder="John Doe"
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                    placeholder="john.doe@example.com"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Select
                  value={inviteForm.role}
                  onValueChange={(value) => setInviteForm({ ...inviteForm, role: value })}
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
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

              <Button
                onClick={handleInvite}
                disabled={!inviteForm.name || !inviteForm.email || loading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Sending Invitation...
                  </>
                ) : (
                  'Send Invitation'
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Team Members List */}
        <div className="grid gap-4">
          {stakeholders.map((member) => (
            <Card key={member.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="flex items-center justify-between p-6">
                <div className="flex items-center gap-4">
                  <div className="h-14 w-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xl">
                    {member.name.charAt(0).toUpperCase()}
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg">{member.name}</h3>
                      {member.status && (
                        <Badge className={getStatusBadgeColor(member.status)}>
                          {member.status}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{member.email}</p>
                    {member.github_branch && (
                      <p className="text-xs text-blue-600 mt-1 font-mono">
                        Branch: {member.github_branch}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Badge className={`${getRoleBadgeColor(member.role)} text-white`}>
                    {member.role}
                  </Badge>
                  
                  {/* Resend invite button for pending members */}
                  {member.status !== 'active' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleResendInvite(member)}
                      disabled={resendingId === member.id}
                      className="h-8"
                    >
                      {resendingId === member.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <RefreshCw className="h-4 w-4 mr-1" />
                          Resend
                        </>
                      )}
                    </Button>
                  )}
                  
                  {/* Delete button (only for admins/owner) */}
                  {user && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => confirmDelete(member)}
                      className="h-8"
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      Remove
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}

          {stakeholders.length === 0 && !showInvite && (
            <Card>
              <CardContent className="p-6 text-center text-muted-foreground">
                No team members yet. Invite the first one!
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, stakeholder: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove Team Member</DialogTitle>
            <DialogDescription>
              Are you sure you want to remove <strong>{deleteDialog.stakeholder?.name}</strong> from the team?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialog({ open: false, stakeholder: null })}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Remove Member
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
