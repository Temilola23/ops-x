'use client'

import { usePathname, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Home, 
  Users, 
  Code2, 
  GitBranch, 
  Sparkles, 
  MessageSquare, 
  BarChart3,
  User,
  Bot
} from 'lucide-react'
import { UserButton } from '@clerk/nextjs'

interface ProjectNavProps {
  projectId: string
  projectName?: string
}

export function ProjectNav({ projectId, projectName }: ProjectNavProps) {
  const pathname = usePathname()
  const router = useRouter()

  const navItems = [
    {
      name: 'Dashboard',
      href: `/project/${projectId}`,
      icon: Home,
      description: 'Project overview & refinements'
    },
    {
      name: 'Team',
      href: `/team/${projectId}`,
      icon: Users,
      description: 'Manage team members'
    },
    {
      name: 'Code',
      href: `/project/${projectId}/code`,
      icon: Code2,
      description: 'Browse generated code'
    },
    {
      name: 'Branches',
      href: `/project/${projectId}/branches`,
      icon: GitBranch,
      description: 'Git branches & PRs'
    },
    {
      name: 'Agents',
      href: `/project/${projectId}/agents`,
      icon: Bot,
      description: 'AI agents working on your project'
    },
    {
      name: 'Chat',
      href: `/project/${projectId}/chat`,
      icon: MessageSquare,
      description: 'Team discussion'
    },
    {
      name: 'Analytics',
      href: `/project/${projectId}/analytics`,
      icon: BarChart3,
      description: 'Project insights'
    }
  ]

  const isActive = (href: string) => pathname === href

  return (
    <div className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        {/* Top Bar */}
        <div className="flex items-center justify-between py-4 border-b">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/')}
            >
              ← Back to Home
            </Button>
            {projectName && (
              <>
                <div className="h-6 w-px bg-border" />
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  <h1 className="text-xl font-bold">{projectName}</h1>
                  <Badge variant="outline" className="ml-2">
                    Active
                  </Badge>
                </div>
              </>
            )}
          </div>

          <div className="flex items-center gap-4">
            <Button
              size="sm"
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              onClick={() => router.push(`/project/${projectId}#refine`)}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Refine MVP
            </Button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto py-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.href)

            return (
              <button
                key={item.href}
                onClick={() => router.push(item.href)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${active 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
                title={item.description}
              >
                <Icon className="h-4 w-4" />
                {item.name}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

