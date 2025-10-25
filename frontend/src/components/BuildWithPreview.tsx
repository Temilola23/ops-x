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
import { Progress } from "@/components/ui/progress";
import { Loader2, Sparkles, FileCode, Eye } from "lucide-react";
import { toast } from "sonner";
import { useStreamingBuild } from "@/hooks/useStreamingBuild";
import { apiClient } from "@/services/api";
import type { AppBuildRequest } from "@/types";

interface BuildWithPreviewProps {
  onProjectCreated?: (projectId: string, appUrl: string) => void;
}

export function BuildWithPreview({ onProjectCreated }: BuildWithPreviewProps) {
  const [projectName, setProjectName] = useState("");
  const [prompt, setPrompt] = useState("");
  const [projectId, setProjectId] = useState<string | null>(null);

  const {
    startBuild,
    status,
    progress,
    previewHtml,
    files,
    isBuilding,
    error,
  } = useStreamingBuild();

  const handleBuild = async () => {
    if (!projectName.trim() || !prompt.trim()) {
      toast.error("Please provide both project name and prompt");
      return;
    }

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
      setProjectId(projectId);

      // Build app with streaming
      const buildRequest: AppBuildRequest = {
        project_id: projectId,
        spec: {
          name: projectName,
          entities: [],
          pages: ["Home", "Dashboard"],
          requirements: prompt.split("\n").filter(Boolean),
        },
      };

      const result = await startBuild(buildRequest);

      if (result?.app_url) {
        toast.success("Build complete!");
        onProjectCreated?.(projectId, result.app_url);
        // Reset form
        setProjectName("");
        setPrompt("");
        setProjectId(null);
      }
    } catch (error) {
      console.error("Build error:", error);
      toast.error(error instanceof Error ? error.message : "Failed to build");
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-screen max-h-screen p-6">
      {/* Left Side - Input Form */}
      <div className="space-y-6 overflow-y-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-primary" />
              One-Prompt Startup
            </CardTitle>
            <CardDescription>
              Describe your startup idea, and watch it come to life in real-time
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
                  Building MVP...
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

        {/* Build Status */}
        {(isBuilding || status) && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <FileCode className="w-4 h-4" />
                Build Progress
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Progress value={progress} className="w-full" />
              <p className="text-sm text-muted-foreground">{status}</p>
              
              {files.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Files Created:</p>
                  <ul className="text-xs space-y-1">
                    {files.slice(-5).map((file, idx) => (
                      <li key={idx} className="text-muted-foreground">
                        {file}
                      </li>
                    ))}
                    {files.length > 5 && (
                      <li className="text-muted-foreground">
                        ... and {files.length - 5} more
                      </li>
                    )}
                  </ul>
                </div>
              )}

              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Right Side - Live Preview */}
      <Card className="h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <CardTitle className="text-sm flex items-center gap-2">
            <Eye className="w-4 h-4" />
            Live Preview
          </CardTitle>
          <CardDescription className="text-xs">
            Watch your app come to life as we build it
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 p-0 overflow-hidden">
          {previewHtml ? (
            <div className="relative w-full h-full">
              {/* Blur overlay while building */}
              {isBuilding && (
                <div className="absolute inset-0 bg-background/50 backdrop-blur-sm z-10 flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto" />
                    <p className="text-sm text-muted-foreground">
                      Generating UI with V0...
                    </p>
                  </div>
                </div>
              )}
              
              {/* Preview iframe */}
              <iframe
                srcDoc={previewHtml}
                className="w-full h-full border-0"
                title="Live Preview"
                sandbox="allow-scripts"
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center space-y-2">
                <Eye className="w-12 h-12 mx-auto opacity-20" />
                <p className="text-sm">
                  Preview will appear here when you start building
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
