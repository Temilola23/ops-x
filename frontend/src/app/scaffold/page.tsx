"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Home,
  Send,
  Loader2,
  Github,
  ExternalLink,
  Code,
  Eye,
  GripVertical,
} from "lucide-react";
import { toast } from "sonner";
import { createV0Chat, sendV0Message } from "@/app/actions/v0";
import { apiClient } from "@/services/api";
import { FileTree } from "@/components/FileTree";
import { BuildingLoader } from "@/components/BuildingLoader";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";

interface V0File {
  name: string;
  content: string;
}

export default function ScaffoldPage() {
  const router = useRouter();

  // Project info from landing page
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  // Build state
  const [chatId, setChatId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [files, setFiles] = useState<V0File[]>([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [loadingPhase, setLoadingPhase] = useState<
    "idle" | "generating" | "ready"
  >("idle");

  // Refinement state
  const [refinementPrompt, setRefinementPrompt] = useState("");
  const [isRefining, setIsRefining] = useState(false);

  // GitHub state
  const [backendProjectId, setBackendProjectId] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [isPushingToGitHub, setIsPushingToGitHub] = useState(false);

  // View state
  const [view, setView] = useState<"preview" | "code">("preview");

  // Load project info and start build
  useEffect(() => {
    const name = sessionStorage.getItem("opsx_project_name");
    const desc = sessionStorage.getItem("opsx_project_description");

    if (!name || !desc) {
      toast.error("No project info found");
      router.push("/");
      return;
    }

    setProjectName(name);
    setProjectDescription(desc);

    // Auto-start build
    startBuild(name, desc);
  }, []);

  const startBuild = async (name: string, desc: string) => {
    setLoadingPhase("generating");

    try {
      // Step 1: Create project in backend
      const projectResponse = await apiClient.createProject(name, desc);

      if (!projectResponse.success || !projectResponse.data) {
        throw new Error("Failed to create project");
      }

      setBackendProjectId(projectResponse.data.id);

      // Step 2: Create full prompt
      const fullPrompt = `Create a modern web app called "${name}".

${desc}

Requirements:
- Use Next.js 14 with App Router
- Use shadcn/ui components for beautiful UI
- Use Tailwind CSS for styling
- Use Lucide icons
- Make it responsive and modern
- Include proper error handling
- Add loading states`;

      // Step 3: Call v0
      console.log("Creating v0 chat with prompt:", fullPrompt);

      const result = await createV0Chat(fullPrompt);

      if (result.success && result.data && result.data.previewUrl) {
        setChatId(result.data.chatId || "");
        setPreviewUrl(result.data.previewUrl || "");
        setFiles(result.data.files || []);
        setSelectedFile(result.data.files?.[0]?.name || "");
        setLoadingPhase("ready");
        toast.success("Your MVP is ready! 🎉");
      } else {
        toast.error(result.error || "Build failed");
        setLoadingPhase("idle");
      }
    } catch (error) {
      console.error("Build error:", error);
      toast.error("Failed to build project");
      setLoadingPhase("idle");
    }
  };

  const handleRefine = async () => {
    if (!chatId || !refinementPrompt.trim()) return;

    setIsRefining(true);
    setLoadingPhase("generating");

    try {
      const result = await sendV0Message(chatId, refinementPrompt);

      if (result.success && result.data && result.data.previewUrl) {
        setPreviewUrl(result.data.previewUrl || "");
        setFiles(result.data.files || []);
        setSelectedFile(result.data.files?.[0]?.name || "");
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

  const handlePushToGitHub = async () => {
    if (!backendProjectId || !chatId || files.length === 0) {
      toast.error("No project to push");
      return;
    }

    setIsPushingToGitHub(true);

    try {
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleRefine();
    }
  };

  const selectedFileContent =
    files.find((f) => f.name === selectedFile)?.content || "";

  const handleFileSelect = (fileName: string) => {
    console.log("File selected:", fileName);
    setSelectedFile(fileName);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              onClick={() => router.push("/")}
              variant="ghost"
              size="sm"
              className="gap-2"
            >
              <Home className="w-4 h-4" />
              Home
            </Button>
            <div className="border-l h-6" />
            <div>
              <h1 className="font-semibold">{projectName}</h1>
              <p className="text-xs text-muted-foreground truncate max-w-md">
                {projectDescription}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {repoUrl ? (
              <Button
                onClick={() => window.open(repoUrl, "_blank")}
                variant="default"
                size="sm"
                className="gap-2"
              >
                <Github className="w-4 h-4" />
                View on GitHub
                <ExternalLink className="w-3 h-3" />
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
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Pushing...
                  </>
                ) : (
                  <>
                    <Github className="w-4 h-4" />
                    Push to GitHub
                  </>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Refinement Input */}
        {chatId && (
          <div className="container mx-auto px-4 pb-3">
            <div className="flex gap-2">
              <Textarea
                placeholder="Refine your app... (e.g., 'Add dark mode toggle' or 'Make the navbar sticky')"
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
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Refine
                  </>
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Cmd/Ctrl + Enter to refine
            </p>
          </div>
        )}
      </div>

      {/* Resizable Split View */}
      <PanelGroup direction="horizontal" className="flex-1">
        {/* LEFT PANEL - File Tree + Code Viewer */}
        <Panel defaultSize={50} minSize={30} maxSize={70}>
          <PanelGroup direction="vertical">
            {/* File Tree Panel */}
            <Panel defaultSize={50} minSize={20}>
              <div className="h-full overflow-y-auto">
                {files.length > 0 ? (
                  <FileTree
                    files={files}
                    selectedFile={selectedFile}
                    onFileSelect={handleFileSelect}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center p-4 text-center text-sm text-muted-foreground">
                    <div>
                      <Code className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No files yet</p>
                    </div>
                  </div>
                )}
              </div>
            </Panel>

            {/* Resize Handle - Horizontal */}
            <PanelResizeHandle className="h-1 bg-border hover:bg-primary transition-colors flex items-center justify-center group">
              <div className="w-12 h-1 rounded-full bg-muted-foreground/20 group-hover:bg-primary/50 transition-colors" />
            </PanelResizeHandle>

            {/* Code Viewer Panel */}
            <Panel defaultSize={50} minSize={20}>
              <div className="h-full flex flex-col">
                <div className="border-b p-2 bg-muted/30 flex-shrink-0">
                  <p className="text-xs font-mono font-semibold px-2">
                    {selectedFile || "No file selected"}
                  </p>
                </div>
                <div className="flex-1 overflow-y-auto">
                  {selectedFileContent ? (
                    <pre className="p-4 text-xs font-mono leading-relaxed">
                      <code>{selectedFileContent}</code>
                    </pre>
                  ) : (
                    <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
                      Select a file to view its content
                    </div>
                  )}
                </div>
              </div>
            </Panel>
          </PanelGroup>
        </Panel>

        {/* Resize Handle - Vertical */}
        <PanelResizeHandle className="w-1 bg-border hover:bg-primary transition-colors flex items-center justify-center group">
          <div className="h-12 w-1 rounded-full bg-muted-foreground/20 group-hover:bg-primary/50 transition-colors" />
          <GripVertical className="absolute w-4 h-4 text-muted-foreground/50 group-hover:text-primary transition-colors" />
        </PanelResizeHandle>

        {/* RIGHT PANEL - Preview */}
        <Panel defaultSize={50} minSize={30} maxSize={70}>
          <div className="h-full relative bg-muted/10">
            {/* Loading Overlay */}
            {loadingPhase === "generating" && <BuildingLoader />}

            {/* Preview iframe */}
            {previewUrl ? (
              <iframe
                src={previewUrl}
                className="w-full h-full border-0"
                title="Live Preview"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
              />
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Eye className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>Preview will appear here</p>
                </div>
              </div>
            )}
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}
