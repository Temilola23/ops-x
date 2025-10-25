"use client";

import { use, useState } from "react";
import { useProject } from "@/hooks/useProject";
import { useAgentStatus } from "@/hooks/useAgentStatus";
import { AgentPanel } from "@/components/AgentPanel";
import { BranchVisualizer } from "@/components/BranchVisualizer";
import { StakeholderDashboard } from "@/components/StakeholderDashboard";
import { ConflictResolver } from "@/components/ConflictResolver";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, MessageSquare, Loader2, Home } from "lucide-react";
import Link from "next/link";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default function DashboardPage({ params }: PageProps) {
  const { projectId } = use(params);
  const { project, isLoading } = useProject(projectId);
  const [conflicts] = useState([]); // TODO: Fetch from conflict scan API

  // Mock stakeholders - replace with actual API call
  const stakeholders = [
    {
      id: "1",
      name: "Alice Chen",
      email: "alice@startup.com",
      role: "Founder" as const,
    },
    {
      id: "2",
      name: "Bob Smith",
      email: "bob@startup.com",
      role: "Frontend" as const,
    },
    {
      id: "3",
      name: "Carol Johnson",
      email: "carol@startup.com",
      role: "Backend" as const,
    },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Project not found</h1>
          <Button asChild>
            <Link href="/">
              <Home className="mr-2 h-4 w-4" />
              Go Home
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <Link href="/" className="text-2xl font-bold text-primary">
                  OPS-X
                </Link>
                <span className="text-muted-foreground">/</span>
                <h1 className="text-2xl font-bold">{project.name}</h1>
              </div>
              {project.app_url && (
                <a
                  href={project.app_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline flex items-center gap-1 mt-1"
                >
                  View App
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button asChild variant="outline">
                <Link href={`/chat/${project.id}`}>
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Team Chat
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Project Info & Agents */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Project Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Owner
                  </div>
                  <div className="text-sm">{project.owner_id}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Default Branch
                  </div>
                  <Badge variant="outline" className="font-mono">
                    {project.default_branch}
                  </Badge>
                </div>
                {project.creao_project_id && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">
                      Creao Project
                    </div>
                    <div className="text-xs font-mono text-muted-foreground">
                      {project.creao_project_id}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <AgentPanel projectId={projectId} />
          </div>

          {/* Right Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <Tabs defaultValue="branches" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="branches">Branches</TabsTrigger>
                <TabsTrigger value="team">Team</TabsTrigger>
                <TabsTrigger value="conflicts">Conflicts</TabsTrigger>
              </TabsList>
              <TabsContent value="branches" className="mt-6">
                <BranchVisualizer projectId={projectId} />
              </TabsContent>
              <TabsContent value="team" className="mt-6">
                <StakeholderDashboard stakeholders={stakeholders} />
              </TabsContent>
              <TabsContent value="conflicts" className="mt-6">
                <ConflictResolver projectId={projectId} conflicts={conflicts} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}
