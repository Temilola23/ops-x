"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2, AlertCircle, Circle } from "lucide-react";
import { useAgentStatus } from "@/hooks/useAgentStatus";
import type { AgentStatus as AgentStatusType, AgentType } from "@/types";

interface AgentPanelProps {
  projectId: string;
}

const agentIcons: Record<AgentType, string> = {
  planner: "🧠",
  frontend: "🎨",
  backend: "⚙️",
  facilitator: "🤝",
  pitch: "📊",
};

const statusConfig: Record<
  AgentStatusType,
  { icon: React.ReactNode; color: string; label: string }
> = {
  idle: {
    icon: <Circle className="h-4 w-4" />,
    color: "text-gray-400",
    label: "Idle",
  },
  thinking: {
    icon: <Loader2 className="h-4 w-4 animate-spin" />,
    color: "text-blue-500",
    label: "Thinking",
  },
  executing: {
    icon: <Loader2 className="h-4 w-4 animate-spin" />,
    color: "text-green-500",
    label: "Executing",
  },
  error: {
    icon: <AlertCircle className="h-4 w-4" />,
    color: "text-red-500",
    label: "Error",
  },
};

export function AgentPanel({ projectId }: AgentPanelProps) {
  const { agents, isLoading, error } = useAgentStatus(projectId);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8 text-red-500">
          <AlertCircle className="h-5 w-5 mr-2" />
          Failed to load agents
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Agents</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {agents.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No agents active
            </p>
          ) : (
            agents.map((agent) => {
              const status = statusConfig[agent.status];
              return (
                <div
                  key={agent.id}
                  className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{agentIcons[agent.type]}</span>
                    <div>
                      <div className="font-semibold text-sm">{agent.name}</div>
                      {agent.current_task && (
                        <div className="text-xs text-muted-foreground mt-0.5">
                          {agent.current_task}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="gap-1">
                      <span className={status.color}>{status.icon}</span>
                      <span className="text-xs">{status.label}</span>
                    </Badge>
                  </div>
                </div>
              );
            })
          )}
        </div>
        {agents.some((a) => a.agentverse_url) && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-xs text-muted-foreground mb-2">
              Deployed on Fetch.ai Agentverse:
            </p>
            <div className="space-y-1">
              {agents
                .filter((a) => a.agentverse_url)
                .map((agent) => (
                  <a
                    key={agent.id}
                    href={agent.agentverse_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-primary hover:underline block"
                  >
                    {agent.name} →
                  </a>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
