"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";

interface AgentPanelProps {
  projectId: string;
}

interface Agent {
  name: string;
  icon: string;
  description: string;
  available: boolean;
}

export function AgentPanel({ projectId }: AgentPanelProps) {
  // These are the agents that are actually integrated in your system
  const [agents] = useState<Agent[]>([
    {
      name: "v0 Frontend Agent",
      icon: "🎨",
      description: "UI/UX generation & refinements",
      available: true, // Always available if project has v0_chat_id
    },
    {
      name: "Claude Backend Agent",
      icon: "⚙️",
      description: "API & database logic",
      available: true, // Always available
    },
    {
      name: "Janitor AI Moderator",
      icon: "🤝",
      description: "Team chat moderation",
      available: true, // Always available in chat
    },
    {
      name: "Fetch.ai Router",
      icon: "🤖",
      description: "Intelligent task routing",
      available: true, // Always active
    },
  ]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>AI Agents</span>
          <Badge variant="outline" className="gap-1">
            <CheckCircle2 className="h-3 w-3 text-green-500" />
            <span className="text-xs">Active</span>
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {agents.map((agent, index) => (
            <div
              key={index}
              className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <span className="text-2xl">{agent.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm mb-1">{agent.name}</div>
                <div className="text-xs text-muted-foreground">
                  {agent.description}
                </div>
              </div>
              {agent.available && (
                <div className="flex-shrink-0">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground mb-2">💡 How it works:</p>
          <ul className="text-xs text-muted-foreground space-y-1">
            <li>• Send messages in chat</li>
            <li>• Fetch.ai detects task type</li>
            <li>• Routes to appropriate agent</li>
            <li>• Changes applied automatically</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
