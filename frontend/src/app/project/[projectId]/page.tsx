'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ProjectNav } from '@/components/ProjectNav'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog'
import { 
  Sparkles, 
  Loader2, 
  ExternalLink, 
  GitBranch,
  Users,
  Code2,
  MessageSquare,
  TrendingUp
} from 'lucide-react'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ProjectDashboard() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.projectId as string

  const [project, setProject] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [refineDialog, setRefineDialog] = useState(false)
  const [refinementText, setRefinementText] = useState('')
  const [refining, setRefining] = useState(false)

  // Mock data - will be replaced with real API calls
  const mockRefinements = [
    { id: 1, author: "You", request: "Make the hero section more modern", status: "completed", time: "2 hours ago" },
    { id: 2, author: "Team Member", request: "Add dark mode toggle", status: "in_progress", time: "5 hours ago" },
    { id: 3, author: "You", request: "Improve mobile responsiveness", status: "completed", time: "1 day ago" }
  ]

  const mockActivity = [
    { id: 1, user: "You", action: "refined MVP", detail: "Updated color scheme", time: "2h ago" },
    { id: 2, user: "Jane", action: "commented", detail: "Great work on the landing page!", time: "3h ago" },
    { id: 3, user: "John", action: "created PR", detail: "PR #3: Add navigation menu", time: "5h ago" }
  ]

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
    } catch (err) {
      toast.error('Failed to load project')
    } finally {
      setLoading(false)
    }
  }

  const handleRefine = async () => {
    if (!refinementText.trim()) {
      toast.error('Please enter a refinement request')
      return
    }

    setRefining(true)

    // TODO: Implement actual refinement API call
    setTimeout(() => {
      toast.success('Refinement started! Check back in a few moments.')
      setRefining(false)
      setRefineDialog(false)
      setRefinementText('')
      loadProject()
    }, 2000)
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
      <ProjectNav projectId={projectId} projectName={project?.name || "Project"} />

      <div className="container mx-auto px-4 py-8">
        {/* Hero Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Refinements</p>
                  <p className="text-3xl font-bold">12</p>
                </div>
                <Sparkles className="h-10 w-10 text-purple-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Team Members</p>
                  <p className="text-3xl font-bold">4</p>
                </div>
                <Users className="h-10 w-10 text-blue-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pull Requests</p>
                  <p className="text-3xl font-bold">7</p>
                </div>
                <GitBranch className="h-10 w-10 text-green-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Comments</p>
                  <p className="text-3xl font-bold">23</p>
                </div>
                <MessageSquare className="h-10 w-10 text-pink-600 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common tasks for this project</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <Button
                  onClick={() => setRefineDialog(true)}
                  className="h-20 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  <div className="text-center">
                    <Sparkles className="h-6 w-6 mx-auto mb-2" />
                    <span>Refine MVP</span>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  onClick={() => router.push(`/project/${projectId}/code`)}
                  className="h-20"
                >
                  <div className="text-center">
                    <Code2 className="h-6 w-6 mx-auto mb-2" />
                    <span>View Code</span>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  onClick={() => window.open(project?.app_url, '_blank')}
                  className="h-20"
                  disabled={!project?.app_url}
                >
                  <div className="text-center">
                    <ExternalLink className="h-6 w-6 mx-auto mb-2" />
                    <span>Live Preview</span>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  onClick={() => router.push(`/team/${projectId}`)}
                  className="h-20"
                >
                  <div className="text-center">
                    <Users className="h-6 w-6 mx-auto mb-2" />
                    <span>Manage Team</span>
                  </div>
                </Button>
              </CardContent>
            </Card>

            {/* Refinement History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Refinement History
                </CardTitle>
                <CardDescription>All improvements made to this project</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {mockRefinements.map((refinement) => (
                  <div
                    key={refinement.id}
                    className="flex items-start justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm">{refinement.author}</span>
                        <span className="text-xs text-muted-foreground">{refinement.time}</span>
                      </div>
                      <p className="text-sm">{refinement.request}</p>
                    </div>
                    <Badge variant={refinement.status === 'completed' ? 'default' : 'secondary'}>
                      {refinement.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Activity Feed */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Team Activity</CardTitle>
                <CardDescription>Real-time updates from your team</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {mockActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                      {activity.user.charAt(0)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">
                        <span className="font-semibold">{activity.user}</span>
                        {' '}<span className="text-muted-foreground">{activity.action}</span>
                      </p>
                      <p className="text-sm text-muted-foreground truncate">{activity.detail}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Project Links */}
            <Card>
              <CardHeader>
                <CardTitle>Project Links</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => window.open(project?.github_repo, '_blank')}
                  disabled={!project?.github_repo}
                >
                  <GitBranch className="h-4 w-4 mr-2" />
                  GitHub Repository
                  <ExternalLink className="h-3 w-3 ml-auto" />
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => window.open(project?.app_url, '_blank')}
                  disabled={!project?.app_url}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Live Preview
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Refinement Dialog */}
      <Dialog open={refineDialog} onOpenChange={setRefineDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              Refine Your MVP
            </DialogTitle>
            <DialogDescription>
              Describe what you'd like to improve. Our AI agents will make the changes and create a pull request.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Textarea
              placeholder="Example: Make the hero section more modern with a gradient background and larger text. Add a 'Get Started' button that stands out."
              value={refinementText}
              onChange={(e) => setRefinementText(e.target.value)}
              rows={6}
              className="resize-none"
            />

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-sm font-semibold mb-2">💡 Refinement Tips:</p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Be specific about what you want to change</li>
                <li>• Mention colors, sizes, or layouts if relevant</li>
                <li>• You can request multiple changes at once</li>
                <li>• Changes will be reviewed before merging</li>
              </ul>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setRefineDialog(false)}
              disabled={refining}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRefine}
              disabled={refining || !refinementText.trim()}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              {refining ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Refining...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Start Refinement
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

