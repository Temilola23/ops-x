'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Sparkles, 
  Users, 
  MessageSquare, 
  FolderKanban,
  Plus,
  ExternalLink,
  Loader2,
  GitBranch
} from 'lucide-react'
import { UserButton } from '@clerk/nextjs'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Project {
  id: number
  name: string
  status: string
  github_repo: string | null
  app_url: string | null
  created_at: string
}

interface TeamMember {
  id: number
  name: string
  email: string
  role: string
  status: string
}

export default function WorkspaceLanding() {
  const router = useRouter()
  const { user, isLoaded } = useUser()

  const [projects, setProjects] = useState<Project[]>([])
  const [teams, setTeams] = useState<TeamMember[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'projects' | 'team' | 'chat'>('projects')

  useEffect(() => {
    if (isLoaded && user) {
      loadUserData()
    }
  }, [isLoaded, user])

  const loadUserData = async () => {
    try {
      // Load user's projects (filtered by user email)
      const projectsRes = await fetch(`${API_URL}/api/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.success && Array.isArray(projectsData.data)) {
        // Sort by creation date (newest first) and show only last 10
        const userProjects = projectsData.data
          .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 10)
        
        setProjects(userProjects)
        
        // Load team members ONLY from user's projects
        const allTeamMembers: TeamMember[] = []
        for (const project of userProjects) {
          const teamRes = await fetch(`${API_URL}/api/projects/${project.id}/stakeholders`)
          const teamData = await teamRes.json()
          if (teamData.success && Array.isArray(teamData.data)) {
            allTeamMembers.push(...teamData.data)
          }
        }
        
        // Remove duplicates by email
        const uniqueTeam = allTeamMembers.filter((member, index, self) =>
          index === self.findIndex((m) => m.email === member.email)
        )
        setTeams(uniqueTeam)
      }
    } catch (err) {
      console.error('Failed to load workspace data:', err)
      toast.error('Failed to load workspace data')
    } finally {
      setLoading(false)
    }
  }

  if (!isLoaded || loading) {
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
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-purple-600" />
            <h1 className="text-2xl font-bold">OPS-X Workspace</h1>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/')}
            >
              Back to Home
            </Button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">
            Welcome back, {user?.firstName || 'there'}!
          </h2>
          <p className="text-muted-foreground">
            Manage your projects, collaborate with teams, and build amazing products.
          </p>
        </div>

        {/* Main Navigation Tabs */}
        <div className="flex items-center gap-2 mb-6 border-b">
          <button
            onClick={() => setActiveTab('projects')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'projects'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <FolderKanban className="inline h-4 w-4 mr-2" />
            Projects
          </button>
          <button
            onClick={() => setActiveTab('team')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'team'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Users className="inline h-4 w-4 mr-2" />
            Team
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-6 py-3 font-medium transition-all border-b-2 ${
              activeTab === 'chat'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <MessageSquare className="inline h-4 w-4 mr-2" />
            Chat Rooms
          </button>
        </div>

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Your Projects</h3>
              <Button
                onClick={() => router.push('/')}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </div>

            {projects.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Sparkles className="h-16 w-16 mx-auto mb-4 text-purple-600 opacity-50" />
                  <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
                  <p className="text-muted-foreground mb-6">
                    Create your first MVP from a single prompt!
                  </p>
                  <Button
                    onClick={() => router.push('/')}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Create First Project
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <Card key={project.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="mb-2">{project.name}</CardTitle>
                          <Badge variant={project.status === 'built' ? 'default' : 'secondary'}>
                            {project.status}
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground mb-3">
                        Created {new Date(project.created_at).toLocaleDateString()}
                      </p>
                      <div className="flex flex-col gap-2">
                        <Button
                          onClick={() => router.push(`/refine/${project.id}`)}
                          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                        >
                          <Sparkles className="h-4 w-4 mr-2" />
                          Open & Refine
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => router.push(`/team/${project.id}`)}
                          className="w-full"
                        >
                          <Users className="h-4 w-4 mr-2" />
                          Manage Team
                        </Button>
                        {project.github_repo && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(project.github_repo!, '_blank')}
                            className="w-full"
                          >
                            <GitBranch className="h-4 w-4 mr-2" />
                            GitHub
                            <ExternalLink className="h-3 w-3 ml-auto" />
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Team Tab */}
        {activeTab === 'team' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Your Team</h3>
              <p className="text-sm text-muted-foreground">
                {teams.length} member{teams.length !== 1 ? 's' : ''}
              </p>
            </div>

            {teams.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Users className="h-16 w-16 mx-auto mb-4 text-purple-600 opacity-50" />
                  <h3 className="text-xl font-semibold mb-2">No team members yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Team members will appear here when you invite them to projects.
                  </p>
                  <Button
                    onClick={() => router.push('/')}
                    variant="outline"
                  >
                    Create a project to start collaborating
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {teams.map((member) => (
                  <Card 
                    key={member.id} 
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => toast.info(`Profile page for ${member.name} coming soon!`)}
                  >
                    <CardContent className="flex items-center gap-4 p-6">
                      <div className="h-14 w-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
                        {member.name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold">{member.name}</h4>
                        <p className="text-sm text-muted-foreground truncate">{member.email}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge>{member.role}</Badge>
                          <Badge variant={member.status === 'active' ? 'default' : 'secondary'} className="text-xs">
                            {member.status}
                          </Badge>
                        </div>
                      </div>
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation()
                          toast.info('Chat feature coming soon!')
                        }}
                      >
                        <MessageSquare className="h-4 w-4" />
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Chat Rooms Tab */}
        {activeTab === 'chat' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold mb-6">Chat Rooms</h3>

            <Card>
              <CardContent className="p-12 text-center">
                <MessageSquare className="h-16 w-16 mx-auto mb-4 text-purple-600 opacity-50" />
                <h3 className="text-xl font-semibold mb-2">No chat rooms yet</h3>
                <p className="text-muted-foreground">
                  Chat rooms will appear here when you join project teams.
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

