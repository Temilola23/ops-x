'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { ProjectNav } from '@/components/ProjectNav'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Bot, 
  Sparkles, 
  Code2, 
  Palette, 
  Database,
  MessageSquare,
  Users,
  Zap,
  CheckCircle2,
  Loader2,
  Brain
} from 'lucide-react'

export default function AgentsDashboard() {
  const params = useParams()
  const projectId = params.projectId as string

  // Mock agents data
  const agents = [
    {
      id: 1,
      name: "V0 Frontend Agent",
      type: "frontend",
      icon: Palette,
      status: "active",
      progress: 75,
      currentTask: "Refining hero section with gradient background",
      completedTasks: 12,
      skills: ["React", "Tailwind CSS", "UI/UX", "Responsive Design"],
      color: "blue"
    },
    {
      id: 2,
      name: "Claude Backend Agent",
      type: "backend",
      icon: Database,
      status: "active",
      progress: 60,
      currentTask: "Creating API endpoints for user authentication",
      completedTasks: 8,
      skills: ["FastAPI", "PostgreSQL", "REST APIs", "Authentication"],
      color: "green"
    },
    {
      id: 3,
      name: "Facilitator Agent",
      type: "facilitator",
      icon: Users,
      status: "idle",
      progress: 100,
      currentTask: "Monitoring team collaboration",
      completedTasks: 15,
      skills: ["Task Management", "Team Coordination", "PR Reviews", "Conflict Resolution"],
      color: "purple"
    },
    {
      id: 4,
      name: "Code Review Agent",
      type: "reviewer",
      icon: CheckCircle2,
      status: "idle",
      progress: 100,
      currentTask: "Ready to review next PR",
      completedTasks: 6,
      skills: ["CodeRabbit Integration", "Best Practices", "Security", "Performance"],
      color: "pink"
    }
  ]

  const recentActivity = [
    { agent: "V0 Frontend Agent", action: "Updated color scheme to match brand guidelines", time: "2 min ago", icon: Palette },
    { agent: "Claude Backend Agent", action: "Created /api/users endpoint with JWT auth", time: "15 min ago", icon: Database },
    { agent: "Facilitator Agent", action: "Assigned task 'Add dark mode' to Frontend Agent", time: "1 hour ago", icon: Users },
    { agent: "Code Review Agent", action: "Approved PR #4: Improve mobile responsiveness", time: "2 hours ago", icon: CheckCircle2 }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-gray-400'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-400'
    }
  }

  const getAgentColor = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'from-blue-500 to-cyan-500',
      green: 'from-green-500 to-emerald-500',
      purple: 'from-purple-500 to-pink-500',
      pink: 'from-pink-500 to-rose-500'
    }
    return colors[color] || colors.purple
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <ProjectNav projectId={projectId} projectName="Project" />

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">AI Agents</h1>
              <p className="text-muted-foreground">Autonomous AI assistants working on your project</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Agents</p>
                  <p className="text-3xl font-bold">4</p>
                </div>
                <Bot className="h-10 w-10 text-purple-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Now</p>
                  <p className="text-3xl font-bold">2</p>
                </div>
                <Zap className="h-10 w-10 text-green-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Tasks Completed</p>
                  <p className="text-3xl font-bold">41</p>
                </div>
                <CheckCircle2 className="h-10 w-10 text-blue-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Efficiency</p>
                  <p className="text-3xl font-bold">94%</p>
                </div>
                <Sparkles className="h-10 w-10 text-pink-600 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agents Grid */}
          <div className="lg:col-span-2 space-y-4">
            {agents.map((agent) => {
              const Icon = agent.icon
              return (
                <Card key={agent.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className={`h-16 w-16 rounded-xl bg-gradient-to-br ${getAgentColor(agent.color)} flex items-center justify-center flex-shrink-0`}>
                        <Icon className="h-8 w-8 text-white" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="font-bold text-lg">{agent.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <div className={`h-2 w-2 rounded-full ${getStatusColor(agent.status)} ${agent.status === 'active' ? 'animate-pulse' : ''}`} />
                              <span className="text-sm text-muted-foreground capitalize">{agent.status}</span>
                              <span className="text-sm text-muted-foreground">•</span>
                              <span className="text-sm text-muted-foreground">{agent.completedTasks} tasks completed</span>
                            </div>
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div>
                            <p className="text-sm font-medium mb-2">{agent.currentTask}</p>
                            {agent.status === 'active' && (
                              <div className="space-y-1">
                                <Progress value={agent.progress} className="h-2" />
                                <p className="text-xs text-muted-foreground text-right">{agent.progress}% complete</p>
                              </div>
                            )}
                          </div>

                          <div className="flex flex-wrap gap-2">
                            {agent.skills.map((skill, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Activity Feed */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Agent Activity
                </CardTitle>
                <CardDescription>Real-time updates from your AI team</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {recentActivity.map((activity, idx) => {
                  const Icon = activity.icon
                  return (
                    <div key={idx} className="flex items-start gap-3">
                      <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">{activity.agent}</p>
                        <p className="text-sm text-muted-foreground">{activity.action}</p>
                        <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                      </div>
                    </div>
                  )
                })}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Agent Controls</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Zap className="h-4 w-4 mr-2" />
                  Deploy New Agent
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Code2 className="h-4 w-4 mr-2" />
                  Configure Agents
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  View Agent Logs
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

