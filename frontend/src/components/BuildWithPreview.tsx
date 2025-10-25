"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Loader2,
  Sparkles,
  Eye,
  Code2,
  Send,
  Home,
  Github,
  ExternalLink,
} from "lucide-react";
import { toast } from "sonner";
import { createV0Chat, sendV0Message } from "@/app/actions/v0";
import { CodeDisplay } from "@/components/CodeDisplay";
import { apiClient } from "@/services/api";

interface V0File {
  name: string;
  content: string;
}

interface BuildWithPreviewProps {
  onProjectCreated?: (projectId: string) => void;
}

export function BuildWithPreview({ onProjectCreated }: BuildWithPreviewProps) {
  // Initial build state
  const [projectName, setProjectName] = useState("");
  const [prompt, setPrompt] = useState("");
  const [isBuilding, setIsBuilding] = useState(false);

  // v0 chat state
  const [chatId, setChatId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [files, setFiles] = useState<V0File[]>([]);

  // Refinement state
  const [refinementPrompt, setRefinementPrompt] = useState("");
  const [isRefining, setIsRefining] = useState(false);

  // GitHub state
  const [repoUrl, setRepoUrl] = useState("");
  const [isPushingToGitHub, setIsPushingToGitHub] = useState(false);
  const [backendProjectId, setBackendProjectId] = useState<string | null>(null);

  // Loading states
  const [loadingPhase, setLoadingPhase] = useState<
    "idle" | "generating" | "ready"
  >("idle");

  const handleBuild = async () => {
    if (!projectName.trim() || !prompt.trim()) {
      toast.error("Please provide both project name and prompt");
      return;
    }

    setIsBuilding(true);
    setLoadingPhase("generating");

    try {
      // Step 1: Create project in backend
      const projectResponse = await apiClient.createProject(
        projectName,
        prompt
      );

      if (!projectResponse.success || !projectResponse.data) {
        throw new Error("Failed to create project");
      }

      const projectId = projectResponse.data.id;
      setBackendProjectId(projectId);

      // Step 2: Create full prompt with project context
      const fullPrompt = `Create a modern web app called "${projectName}".

${prompt}

Requirements:
- Use Next.js 14 with App Router
- Use shadcn/ui components for beautiful UI
- Use Tailwind CSS for styling
- Use Lucide icons
- Make it responsive and modern
- Include proper error handling
- Add loading states`;

      // Step 3: Call v0 Server Action (secure, server-side)
      const result = await createV0Chat(fullPrompt);

      if (result.success && result.data && result.data.previewUrl) {
        setChatId(result.data.chatId || "");
        setPreviewUrl(result.data.previewUrl || "");
        setFiles(result.data.files || []);
        setLoadingPhase("ready");
        toast.success("Preview ready! 🎉");

        // Notify parent component
        if (onProjectCreated && projectId) {
          onProjectCreated(projectId);
        }
      } else {
        toast.error(result.error || "Build failed");
        setLoadingPhase("idle");
      }
    } catch (error) {
      console.error("Build error:", error);
      toast.error("Failed to build project");
      setLoadingPhase("idle");
    } finally {
      setIsBuilding(false);
    }
  };

  const handlePushToGitHub = async () => {
    if (!backendProjectId || !chatId || files.length === 0) {
      toast.error("No project to push");
      return;
    }

    setIsPushingToGitHub(true);

    try {
      // Call backend to save to GitHub
      const response = await apiClient.saveToGitHub({
        project_id: backendProjectId,
        project_name: projectName,
        files: files,
        v0_chat_id: chatId,
        v0_preview_url: previewUrl,
        description: `Generated with v0.dev - ${projectName}`,
      });

      if (response.success && response.data) {
        setRepoUrl(response.data.repo_url);
        toast.success("Code pushed to GitHub! 🎉");
      } else {
        toast.error(response.error || "Failed to push to GitHub");
      }
    } catch (error) {
      console.error("GitHub push error:", error);
      toast.error("Failed to push to GitHub");
    } finally {
      setIsPushingToGitHub(false);
    }
  };

  const handleRefine = async () => {
    if (!chatId || !refinementPrompt.trim()) return;

    setIsRefining(true);
    setLoadingPhase("generating");

    try {
      // Send refinement message to existing v0 chat
      const result = await sendV0Message(chatId, refinementPrompt);

      if (result.success && result.data && result.data.previewUrl) {
        // Update preview URL (v0 automatically updates the demo)
        setPreviewUrl(result.data.previewUrl || "");
        setFiles(result.data.files || []);
        setLoadingPhase("ready");
        setRefinementPrompt("");
        toast.success("Updated! ✨");
      } else {
        toast.error(result.error || "Refinement failed");
      }
    } catch (error) {
      console.error("Refinement error:", error);
      toast.error("Failed to refine");
    } finally {
      setIsRefining(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      if (!chatId) {
        handleBuild();
      } else {
        handleRefine();
      }
    }
  };

  const resetProject = () => {
    setChatId(null);
    setPreviewUrl("");
    setFiles([]);
    setProjectName("");
    setPrompt("");
    setRefinementPrompt("");
    setRepoUrl("");
    setBackendProjectId(null);
    setLoadingPhase("idle");
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header with Prompt Input */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">Build Your MVP</h1>
                <p className="text-sm text-muted-foreground">
                  Powered by v0.dev
                </p>
              </div>
            </div>
            {chatId && (
              <Button onClick={resetProject} variant="outline" size="sm">
                <Home className="mr-2 h-4 w-4" />
                Start New Project
              </Button>
            )}
          </div>

          {!chatId ? (
            // Initial Prompt Input
            <div className="space-y-4 max-w-4xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2 md:col-span-1">
                  <Label htmlFor="projectName">Project Name</Label>
                  <Input
                    id="projectName"
                    placeholder="My Startup"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    disabled={isBuilding}
                    onKeyDown={handleKeyDown}
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="prompt">Describe Your App</Label>
                  <Textarea
                    id="prompt"
                    placeholder="E.g., A todo app with categories, due dates, and a dark mode toggle..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    disabled={isBuilding}
                    rows={3}
                    className="resize-none"
                    onKeyDown={handleKeyDown}
                  />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleBuild}
                  disabled={isBuilding || !projectName.trim() || !prompt.trim()}
                  size="lg"
                  className="gap-2"
                >
                  {isBuilding ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Building with v0...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Build MVP
                    </>
                  )}
                </Button>
                <p className="text-xs text-muted-foreground">
                  Cmd/Ctrl + Enter to build
                </p>
              </div>
            </div>
          ) : (
            // Refinement Input
            <div className="flex gap-2 max-w-4xl">
              <Textarea
                placeholder="Refine your app... (e.g., 'Add dark mode', 'Make it responsive', 'Add user authentication')"
                value={refinementPrompt}
                onChange={(e) => setRefinementPrompt(e.target.value)}
                disabled={isRefining}
                rows={2}
                className="resize-none flex-1"
                onKeyDown={handleKeyDown}
              />
              <Button
                onClick={handleRefine}
                disabled={isRefining || !refinementPrompt.trim()}
                size="lg"
                className="gap-2"
              >
                {isRefining ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Refine
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Preview & Code Tabs */}
      {previewUrl && (
        <Tabs defaultValue="preview" className="flex-1 flex flex-col">
          <div className="border-b bg-muted/30">
            <div className="container mx-auto px-6">
              <div className="flex items-center justify-between">
                <TabsList className="bg-transparent border-0 h-12">
                  <TabsTrigger value="preview" className="gap-2">
                    <Eye className="h-4 w-4" />
                    Preview
                    {loadingPhase === "generating" && (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="code" className="gap-2">
                    <Code2 className="h-4 w-4" />
                    Code
                    {files.length > 0 && (
                      <span className="text-xs text-muted-foreground">
                        ({files.length} files)
                      </span>
                    )}
                  </TabsTrigger>
                </TabsList>

                {/* GitHub Actions */}
                <div className="flex items-center gap-2">
                  {repoUrl ? (
                    <Button
                      onClick={() => window.open(repoUrl, "_blank")}
                      variant="default"
                      size="sm"
                      className="gap-2"
                    >
                      <Github className="h-4 w-4" />
                      View on GitHub
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  ) : (
                    <Button
                      onClick={handlePushToGitHub}
                      disabled={isPushingToGitHub || !files.length}
                      variant="default"
                      size="sm"
                      className="gap-2"
                    >
                      {isPushingToGitHub ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Pushing...
                        </>
                      ) : (
                        <>
                          <Github className="h-4 w-4" />
                          Push to GitHub
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Preview Tab */}
          <TabsContent
            value="preview"
            className="flex-1 m-0 relative data-[state=active]:flex"
          >
            {/* Loading Overlay - Lovable style */}
            <div
              className={`
                absolute inset-0 z-10
                bg-white/80 dark:bg-gray-900/80 
                backdrop-blur-sm 
                transition-opacity duration-500
                flex items-center justify-center
                ${
                  loadingPhase === "ready"
                    ? "opacity-0 pointer-events-none"
                    : "opacity-100"
                }
              `}
            >
              <div className="text-center space-y-4">
                <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
                <div>
                  <p className="text-lg font-semibold">
                    {loadingPhase === "generating"
                      ? "Generating your app..."
                      : "Almost ready..."}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    v0 is crafting beautiful UI for you
                  </p>
                </div>
              </div>
            </div>

            {/* v0 Preview iframe */}
            <iframe
              src={previewUrl}
              className="w-full h-full border-0"
              title="Live Preview"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
              allow="accelerometer; camera; encrypted-media; geolocation; gyroscope; microphone; midi; payment; usb"
            />
          </TabsContent>

          {/* Code Tab */}
          <TabsContent
            value="code"
            className="flex-1 m-0 data-[state=active]:flex"
          >
            <CodeDisplay files={files} />
          </TabsContent>
        </Tabs>
      )}

      {/* Empty State */}
      {!previewUrl && !isBuilding && (
        <div className="flex-1 flex items-center justify-center text-muted-foreground">
          <div className="text-center space-y-4 max-w-md">
            <Eye className="w-16 h-16 mx-auto opacity-20" />
            <div>
              <p className="text-lg font-semibold">Ready to build?</p>
              <p className="text-sm mt-2">
                Describe your app idea above and watch it come to life in
                real-time
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
