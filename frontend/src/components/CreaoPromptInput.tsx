"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Sparkles } from "lucide-react";
import { apiClient } from "@/services/api";
import { toast } from "sonner";
import type { CreaoRequest } from "@/types";

interface CreaoPromptInputProps {
  onProjectCreated?: (projectId: string, appUrl: string) => void;
}

export function CreaoPromptInput({ onProjectCreated }: CreaoPromptInputProps) {
  const [projectName, setProjectName] = useState("");
  const [prompt, setPrompt] = useState("");
  const [isBuilding, setIsBuilding] = useState(false);

  const handleBuild = async () => {
    if (!projectName.trim() || !prompt.trim()) {
      toast.error("Please provide both project name and prompt");
      return;
    }

    setIsBuilding(true);

    try {
      // Create the project
      const projectResponse = await apiClient.createProject(
        projectName,
        prompt
      );

      if (!projectResponse.success || !projectResponse.data) {
        throw new Error("Failed to create project");
      }

      const projectId = projectResponse.data.id;

      toast.success("Project created! Building with Creao...");

      // Build with Creao
      const buildRequest: CreaoRequest = {
        project_id: projectId,
        spec: {
          name: projectName,
          entities: [],
          pages: ["Home", "Dashboard"],
          requirements: prompt.split("\n").filter(Boolean),
        },
      };

      const buildResponse = await apiClient.buildWithCreao(buildRequest);

      if (buildResponse.success && buildResponse.data) {
        toast.success("Build complete!");
        onProjectCreated?.(projectId, buildResponse.data.app_url);

        // Reset form
        setProjectName("");
        setPrompt("");
      } else {
        throw new Error("Build failed");
      }
    } catch (error) {
      console.error("Build error:", error);
      toast.error("Failed to build project. Please try again.");
    } finally {
      setIsBuilding(false);
    }
  };

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          One-Prompt Startup
        </CardTitle>
        <CardDescription>
          Describe your startup idea, and we&apos;ll build a working MVP with AI
          agents
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="projectName">Project Name</Label>
          <Input
            id="projectName"
            placeholder="My Awesome Startup"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            disabled={isBuilding}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="prompt">Describe Your Idea</Label>
          <Textarea
            id="prompt"
            placeholder="Build a platform for investors to ask questions about companies. Include user authentication, a chat interface, and analytics dashboard..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isBuilding}
            rows={8}
            className="resize-none"
          />
          <p className="text-xs text-muted-foreground">
            Be specific about features, tech requirements, and user flows
          </p>
        </div>

        <Button
          onClick={handleBuild}
          disabled={isBuilding || !projectName.trim() || !prompt.trim()}
          className="w-full"
          size="lg"
        >
          {isBuilding ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Building with Creao...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-4 w-4" />
              Build MVP
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
