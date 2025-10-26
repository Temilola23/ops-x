'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Sparkles, 
  Loader2, 
  Users,
  ExternalLink,
  GitBranch,
  ArrowLeft,
  Send,
  Code2,
  Eye,
  Home
} from 'lucide-react'
import { useUser } from '@clerk/nextjs'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function RefinePage() {
  const params = useParams()
  const router = useRouter()
  const { user, isLoaded } = useUser()
  const projectId = params.projectId as string

  const [project, setProject] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [refinementText, setRefinementText] = useState('')
  const [refining, setRefining] = useState(false)
  const [stakeholders, setStakeholders] = useState<any[]>([])
  const [view, setView] = useState<'preview' | 'code'>('preview')
  const [showPushDialog, setShowPushDialog] = useState(false)
  const [pushTarget, setPushTarget] = useState<'main' | 'branch'>('main')
  const [files, setFiles] = useState<any>({})
  const [loadingCode, setLoadingCode] = useState(false)
  const [pushing, setPushing] = useState(false)

  useEffect(() => {
    loadProject()
  }, [projectId])

  const loadProject = async () => {
    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}`)
      const data = await res.json()
      
      if (data.success) {
        setProject(data.data)
      }
      
      // Load stakeholders
      const stakeholdersRes = await fetch(`${API_URL}/api/projects/${projectId}/stakeholders`)
      const stakeholdersData = await stakeholdersRes.json()
      if (stakeholdersData.success) {
        setStakeholders(stakeholdersData.data)
      }
      
      // Load code files from GitHub
      if (data.success && data.data.github_repo) {
        loadCodeFiles()
      }
    } catch (err) {
      toast.error('Failed to load project')
    } finally {
      setLoading(false)
    }
  }

  const loadCodeFiles = async () => {
    setLoadingCode(true)
    try {
      const userStakeholder = stakeholders.find(s => s.email === user?.emailAddresses[0]?.emailAddress)
      const stakeholderId = userStakeholder?.id || null
      
      const url = stakeholderId 
        ? `${API_URL}/api/projects/${projectId}/code/latest?stakeholder_id=${stakeholderId}`
        : `${API_URL}/api/projects/${projectId}/code/latest`
      
      const res = await fetch(url)
      const data = await res.json()
      
      if (data.success) {
        setFiles(data.data.files || {})
        console.log(`Loaded ${Object.keys(data.data.files || {}).length} files from GitHub`)
      }
    } catch (err) {
      console.error('Failed to load code files:', err)
    } finally {
      setLoadingCode(false)
    }
  }

  const handleRefine = async () => {
    if (!refinementText.trim()) {
      toast.error('Please enter a refinement request')
      return
    }

    setRefining(true)

    try {
      const userStakeholder = stakeholders.find(s => s.email === user?.emailAddresses[0]?.emailAddress)
      
      const res = await fetch(`${API_URL}/api/projects/${projectId}/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: parseInt(projectId),
          stakeholder_id: userStakeholder?.id || 1,
          request_text: refinementText,
          ai_model_preference: 'auto'
        })
      })
      
      const data = await res.json()
      
      if (data.success) {
        toast.success('Refinement queued! Your teammate will process this with V0.')
        setRefinementText('')
      } else {
        toast.error(data.error || 'Failed to create refinement')
      }
    } catch (err) {
      toast.error('Network error')
    } finally {
      setRefining(false)
    }
  }

  const handlePush = (target: 'main' | 'branch') => {
    setPushTarget(target)
    
    if (target === 'main') {
      setShowPushDialog(true)
    } else {
      createBranchAndPR()
    }
  }

  const createBranchAndPR = async () => {
    setPushing(true)
    
    try {
      const userStakeholder = stakeholders.find(s => s.email === user?.emailAddresses[0]?.emailAddress)
      
      const res = await fetch(`${API_URL}/api/projects/${projectId}/create-branch-and-pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stakeholder_id: userStakeholder?.id || 1,
          files: files,
          pr_title: `Refinement: ${refinementText.slice(0, 50)}...`,
          pr_description: `Refinement requested by ${userStakeholder?.name || 'Team Member'}:\n\n${refinementText}`
        })
      })
      
      const data = await res.json()
      
      if (data.success) {
        toast.success('PR created successfully!')
        if (data.data.pr_url) {
          window.open(data.data.pr_url, '_blank')
        }
      } else {
        toast.error(data.error || 'Failed to create PR')
      }
    } catch (err) {
      toast.error('Network error')
    } finally {
      setPushing(false)
    }
  }

  const pushToMainBranch = async () => {
    setPushing(true)
    setShowPushDialog(false)
    
    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}/push-to-main`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          files: files,
          commit_message: `Update: ${refinementText.slice(0, 100)}`
        })
      })
      
      const data = await res.json()
      
      if (data.success) {
        toast.success('Changes pushed to main branch!')
      } else {
        toast.error(data.error || 'Failed to push to main')
      }
    } catch (err) {
      toast.error('Network error')
    } finally {
      setPushing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
                <Home className="h-4 w-4 mr-2" />
                Home
              </Button>
              <div className="h-6 w-px bg-border" />
              <Button variant="ghost" size="sm" onClick={() => router.push('/workspace')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Workspace
              </Button>
              <div className="h-6 w-px bg-border" />
              <Sparkles className="h-5 w-5 text-purple-600" />
              <h1 className="text-xl font-bold">{project?.name || 'Project'}</h1>
              <Badge variant={project?.status === 'built' ? 'default' : 'secondary'}>
                {project?.status}
              </Badge>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/team/${projectId}`)}
              >
                <Users className="h-4 w-4 mr-2" />
                Team ({stakeholders.length})
              </Button>
              {project?.github_repo && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(project.github_repo, '_blank')}
                >
                  <GitBranch className="h-4 w-4 mr-2" />
                  GitHub
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-10rem)]">
          {/* Left - Preview */}
          <Card className="h-full flex flex-col">
            <div className="p-4 border-b bg-gray-50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button
                  variant={view === 'preview' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setView('preview')}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Preview
                </Button>
                <Button
                  variant={view === 'code' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setView('code')}
                >
                  <Code2 className="h-4 w-4 mr-2" />
                  Code
                </Button>
              </div>
              {project?.v0_preview_url && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => window.open(project.v0_preview_url, '_blank')}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open in New Tab
                </Button>
              )}
            </div>
            
            <CardContent className="flex-1 p-0 overflow-hidden">
              {view === 'preview' ? (
                <div className="h-full bg-white">
                  {project?.v0_preview_url ? (
                    <iframe
                      src={project.v0_preview_url}
                      className="w-full h-full border-0"
                      title="Project Preview"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      <div className="text-center">
                        <p className="mb-2">No preview available</p>
                        <p className="text-sm">Generate refinement to see updates</p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-full overflow-auto p-4 bg-gray-50 font-mono text-sm">
                  {loadingCode ? (
                    <div className="flex items-center justify-center h-full">
                      <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
                    </div>
                  ) : Object.keys(files).length > 0 ? (
                    <div className="space-y-4">
                      {Object.entries(files).map(([path, content]: [string, any], idx: number) => (
                        <div key={idx} className="bg-white p-4 rounded border">
                          <div className="flex items-center justify-between mb-2">
                            <div className="font-semibold text-blue-600">{path}</div>
                            <Badge variant="secondary" className="text-xs">
                              {content.length} chars
                            </Badge>
                          </div>
                          <pre className="text-xs overflow-x-auto bg-gray-50 p-3 rounded max-h-96">{content}</pre>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      <div className="text-center">
                        <Code2 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                        <p>No code files loaded yet</p>
                        <Button
                          variant="outline"
                          size="sm"
                          className="mt-4"
                          onClick={loadCodeFiles}
                        >
                          Load Files from GitHub
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Right - Refinement */}
          <Card className="h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <div className="mb-4">
                <h3 className="font-semibold text-lg mb-2 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  Refine Your MVP
                </h3>
                <p className="text-sm text-muted-foreground">
                  Describe improvements - your frontend teammate handles V0 integration
                </p>
              </div>

              <Textarea
                placeholder="Example: Make the hero section more modern with a gradient background. Add a prominent call-to-action button."
                value={refinementText}
                onChange={(e) => setRefinementText(e.target.value)}
                className="flex-1 resize-none mb-4 min-h-[200px]"
              />

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
                <p className="text-sm font-semibold mb-2">Tips:</p>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>• Be specific about what you want</li>
                  <li>• Mention colors, layouts, or features</li>
                  <li>• Changes go through PR review process</li>
                </ul>
              </div>

              <div className="space-y-2">
                <Button
                  onClick={handleRefine}
                  disabled={refining || !refinementText.trim()}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  {refining ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Queueing Refinement...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Send Refinement Request
                    </>
                  )}
                </Button>

                {/* Push Options */}
                <div className="pt-4 border-t">
                  <p className="text-sm font-semibold mb-3">Push Changes:</p>
                  {!isLoaded || !user ? (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => handlePush('main')}
                      disabled={pushing || Object.keys(files).length === 0}
                    >
                      {pushing ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Pushing...
                        </>
                      ) : (
                        <>
                          <GitBranch className="h-4 w-4 mr-2" />
                          Push to Main Branch
                        </>
                      )}
                    </Button>
                  ) : (
                    <div className="grid grid-cols-2 gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePush('main')}
                        disabled={pushing || Object.keys(files).length === 0}
                      >
                        {pushing ? 'Pushing...' : 'Push to Main'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePush('branch')}
                        disabled={pushing || Object.keys(files).length === 0}
                        className="bg-green-50 hover:bg-green-100"
                      >
                        {pushing ? 'Creating...' : 'Create PR'}
                      </Button>
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground mt-2">
                    {Object.keys(files).length} files loaded from GitHub
                  </p>
                </div>
              </div>

              {/* Team Members Preview */}
              {stakeholders.length > 0 && (
                <div className="mt-6 pt-6 border-t">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold">Team ({stakeholders.length})</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/team/${projectId}`)}
                    >
                      Manage
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {stakeholders.slice(0, 4).map((member) => (
                      <div key={member.id} className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xs">
                          {member.name.charAt(0)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{member.name}</p>
                        </div>
                        <Badge variant="secondary" className="text-xs">{member.role}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Push to Main Warning Dialog */}
      <Dialog open={showPushDialog} onOpenChange={setShowPushDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Push to Main Branch?</DialogTitle>
            <DialogDescription>
              You're about to push changes directly to the main branch. This will update the production code immediately without review.
            </DialogDescription>
          </DialogHeader>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-yellow-800">Warning:</p>
            <p className="text-sm text-yellow-700 mt-1">
              Pushing to main bypasses the PR review process. Consider creating a branch instead if you have team members.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowPushDialog(false)}
              disabled={pushing}
            >
              Cancel
            </Button>
            <Button
              onClick={pushToMainBranch}
              disabled={pushing}
              className="bg-yellow-600 hover:bg-yellow-700"
            >
              {pushing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Pushing...
                </>
              ) : (
                'Push to Main Anyway'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
