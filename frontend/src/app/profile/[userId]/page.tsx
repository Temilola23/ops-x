'use client'

import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  User, 
  Mail, 
  Calendar, 
  GitBranch, 
  Code2, 
  MessageSquare,
  Award,
  Activity,
  ArrowLeft
} from 'lucide-react'

export default function ProfilePage() {
  const params = useParams()
  const router = useRouter()
  const userId = params.userId as string

  // Mock data - will be replaced with real data
  const profile = {
    name: "Team Member",
    email: "member@example.com",
    role: "Frontend Engineer",
    joined: "2 days ago",
    avatar: null,
    stats: {
      refinements: 5,
      commits: 12,
      prs: 3,
      comments: 8
    },
    currentTasks: [
      { id: 1, title: "Improve landing page design", status: "in_progress" },
      { id: 2, title: "Add dark mode support", status: "pending" }
    ],
    recentActivity: [
      { id: 1, type: "refinement", message: "Refined button component styling", time: "2 hours ago" },
      { id: 2, type: "comment", message: "Commented on navigation PR", time: "5 hours ago" },
      { id: 3, type: "pr", message: "Created PR #3: Update color scheme", time: "1 day ago" }
    ],
    contributions: [
      { file: "app/page.tsx", changes: "+45 -12" },
      { file: "components/hero.tsx", changes: "+32 -5" },
      { file: "app/globals.css", changes: "+28 -3" }
    ]
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

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'refinement': return Code2
      case 'comment': return MessageSquare
      case 'pr': return GitBranch
      default: return Activity
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md">
        <div className="container mx-auto px-4 py-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Profile Info */}
          <div className="space-y-6">
            {/* Profile Card */}
            <Card>
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <div className="h-24 w-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-3xl mx-auto">
                    {profile.name.charAt(0)}
                  </div>
                  
                  <div>
                    <h2 className="text-2xl font-bold">{profile.name}</h2>
                    <Badge className={`${getRoleBadgeColor(profile.role)} text-white mt-2`}>
                      {profile.role}
                    </Badge>
                  </div>

                  <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center justify-center gap-2">
                      <Mail className="h-4 w-4" />
                      {profile.email}
                    </div>
                    <div className="flex items-center justify-center gap-2">
                      <Calendar className="h-4 w-4" />
                      Joined {profile.joined}
                    </div>
                  </div>

                  <div className="pt-4">
                    <Button className="w-full">
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Send Message
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5 text-purple-600" />
                  Contributions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Refinements</span>
                  <Badge variant="secondary">{profile.stats.refinements}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Commits</span>
                  <Badge variant="secondary">{profile.stats.commits}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Pull Requests</span>
                  <Badge variant="secondary">{profile.stats.prs}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Comments</span>
                  <Badge variant="secondary">{profile.stats.comments}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Activity & Tasks */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Tasks */}
            <Card>
              <CardHeader>
                <CardTitle>Current Tasks</CardTitle>
                <CardDescription>Active assignments and work in progress</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {profile.currentTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`h-2 w-2 rounded-full ${task.status === 'in_progress' ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} />
                      <span className="font-medium">{task.title}</span>
                    </div>
                    <Badge variant={task.status === 'in_progress' ? 'default' : 'secondary'}>
                      {task.status === 'in_progress' ? 'In Progress' : 'Pending'}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {profile.recentActivity.map((activity) => {
                  const Icon = getActivityIcon(activity.type)
                  return (
                    <div key={activity.id} className="flex items-start gap-4">
                      <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">{activity.message}</p>
                        <p className="text-sm text-muted-foreground">{activity.time}</p>
                      </div>
                    </div>
                  )
                })}
              </CardContent>
            </Card>

            {/* Code Contributions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code2 className="h-5 w-5" />
                  Code Contributions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {profile.contributions.map((contrib, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors font-mono text-sm"
                  >
                    <span className="text-gray-700">{contrib.file}</span>
                    <span className="text-green-600 font-semibold">{contrib.changes}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

