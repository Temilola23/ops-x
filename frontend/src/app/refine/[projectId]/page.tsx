"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Sparkles,
  Loader2,
  Users,
  ExternalLink,
  GitBranch,
  ArrowLeft,
  Send,
  Code2,
  Eye,
  Home,
  Github,
  GripVertical,
  Code,
} from "lucide-react";
import { useUser } from "@clerk/nextjs";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import { FileTree } from "@/components/FileTree";
import { BuildingLoader } from "@/components/BuildingLoader";
import { sendV0Message } from "@/app/actions/v0";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RefinePage() {
  const params = useParams();
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const projectId = params.projectId as string;

  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refinementText, setRefinementText] = useState("");
  const [refining, setRefining] = useState(false);
  const [stakeholders, setStakeholders] = useState<any[]>([]);
  const [showPushDialog, setShowPushDialog] = useState(false);
  const [pushTarget, setPushTarget] = useState<"main" | "branch">("main");
  const [files, setFiles] = useState<any>({});
  const [filesArray, setFilesArray] = useState<
    Array<{ name: string; content: string }>
  >([]);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [loadingCode, setLoadingCode] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [showTeamPanel, setShowTeamPanel] = useState(false);

  // v0 state for frontend SDK integration
  const [chatId, setChatId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const fetchPreviewFromGitHub = async (repoUrl: string) => {
    try {
      // Extract owner/repo from GitHub URL
      // Format: https://github.com/owner/repo
      const match = repoUrl.match(/github\.com\/([^\/]+\/[^\/]+)/);
      if (!match) {
        console.error("Invalid GitHub URL format:", repoUrl);
        return;
      }

      const repoPath = match[1];
      console.log("Fetching README from:", repoPath);

      // Fetch README.md from GitHub via raw content
      const readmeUrl = `https://raw.githubusercontent.com/${repoPath}/main/README.md`;
      const response = await fetch(readmeUrl);

      if (!response.ok) {
        console.error("Failed to fetch README:", response.status);
        return;
      }

      const readmeContent = await response.text();

      // Extract preview URL from README
      // Format: [View Live Preview](https://v0.dev/chat/...)
      const previewMatch = readmeContent.match(
        /\[View Live Preview\]\((https:\/\/[^\)]+)\)/
      );

      if (previewMatch && previewMatch[1]) {
        const extractedUrl = previewMatch[1];
        console.log("Extracted preview URL from README:", extractedUrl);
        setPreviewUrl(extractedUrl);

        // Save to database for next time
        await fetch(`${API_URL}/api/projects/${projectId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            v0_preview_url: extractedUrl,
          }),
        });
      } else {
        console.log("No preview URL found in README");
      }
    } catch (error) {
      console.error("Error fetching preview from GitHub:", error);
    }
  };

  const loadProject = async () => {
    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}`);
      const data = await res.json();

      if (data.success) {
        const projectData = data.data;
        setProject(projectData);

        // Load v0 data for frontend SDK
        if (projectData.v0_chat_id) {
          setChatId(projectData.v0_chat_id);
          console.log("Loaded v0 chat ID:", projectData.v0_chat_id);
        }

        // Try to load preview URL from database first
        if (projectData.v0_preview_url) {
          setPreviewUrl(projectData.v0_preview_url);
          console.log(
            "Loaded v0 preview URL from database:",
            projectData.v0_preview_url
          );
        }
        // Fallback: Extract from README.md in GitHub repo
        else if (projectData.github_repo) {
          console.log(
            "Preview URL not in database, fetching from GitHub README..."
          );
          fetchPreviewFromGitHub(projectData.github_repo);
        }
      }

      // Load stakeholders
      const stakeholdersRes = await fetch(
        `${API_URL}/api/projects/${projectId}/stakeholders`
      );
      const stakeholdersData = await stakeholdersRes.json();
      if (stakeholdersData.success) {
        setStakeholders(stakeholdersData.data);
      }

      // Load code files from GitHub
      if (data.success && data.data.github_repo) {
        loadCodeFiles();
      }
    } catch (err) {
      toast.error("Failed to load project");
    } finally {
      setLoading(false);
    }
  };

  const loadCodeFiles = async () => {
    setLoadingCode(true);
    try {
      const userStakeholder = stakeholders.find(
        (s) => s.email === user?.emailAddresses[0]?.emailAddress
      );
      const stakeholderId = userStakeholder?.id || null;

      const url = stakeholderId
        ? `${API_URL}/api/projects/${projectId}/code/latest?stakeholder_id=${stakeholderId}`
        : `${API_URL}/api/projects/${projectId}/code/latest`;

      const res = await fetch(url);
      const data = await res.json();

      if (data.success) {
        const filesObj = data.data.files || {};
        setFiles(filesObj);

        // Convert files object to array for FileTree component
        const filesArr = Object.entries(filesObj).map(([path, content]) => ({
          name: path,
          content: String(content),
        }));
        setFilesArray(filesArr);

        // Set first file as selected
        if (filesArr.length > 0) {
          setSelectedFile(filesArr[0].name);
        }

        console.log(`Loaded ${filesArr.length} files from GitHub`);
      }
    } catch (err) {
      console.error("Failed to load code files:", err);
    } finally {
      setLoadingCode(false);
    }
  };

  const handleRefine = async () => {
    if (!refinementText.trim()) {
      toast.error("Please enter a refinement request");
      return;
    }

    if (!chatId) {
      toast.error(
        "No v0 chat session found. Please rebuild the project from scaffold page."
      );
      return;
    }

    setRefining(true);

    try {
      console.log("Sending v0 refinement:", refinementText);

      // Call v0 SDK via Next.js server action (TypeScript only!)
      const result = await sendV0Message(chatId, refinementText);

      if (result.success && result.data) {
        console.log("Refinement successful:", result.data);

        // Update preview URL and files
        if (result.data.previewUrl) {
          setPreviewUrl(result.data.previewUrl);

          // Sync new preview URL to Python backend for persistence
          await fetch(`${API_URL}/api/projects/${projectId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              v0_preview_url: result.data.previewUrl,
            }),
          });
        }

        if (result.data.files) {
          // Convert files to array format
          const filesArr = result.data.files.map((f: any) => ({
            name: f.name,
            content: f.content,
          }));
          setFilesArray(filesArr);

          // Convert to object format for compatibility
          const filesObj: any = {};
          result.data.files.forEach((f: any) => {
            filesObj[f.name] = f.content;
          });
          setFiles(filesObj);

          // Select first file
          if (filesArr.length > 0) {
            setSelectedFile(filesArr[0].name);
          }
        }

        setRefinementText("");
        toast.success("Refinement applied! ✨ Preview updated.");
      } else {
        toast.error(result.error || "Failed to refine");
      }
    } catch (err) {
      console.error("Refinement error:", err);
      toast.error("Network error");
    } finally {
      setRefining(false);
    }
  };

  const handlePush = (target: "main" | "branch") => {
    setPushTarget(target);

    if (target === "main") {
      setShowPushDialog(true);
    } else {
      createBranchAndPR();
    }
  };

  const createBranchAndPR = async () => {
    setPushing(true);

    try {
      const userStakeholder = stakeholders.find(
        (s) => s.email === user?.emailAddresses[0]?.emailAddress
      );

      const res = await fetch(
        `${API_URL}/api/projects/${projectId}/create-branch-and-pr`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            stakeholder_id: userStakeholder?.id || 1,
            files: files,
            pr_title: `Refinement: ${refinementText.slice(0, 50)}...`,
            pr_description: `Refinement requested by ${
              userStakeholder?.name || "Team Member"
            }:\n\n${refinementText}`,
          }),
        }
      );

      const data = await res.json();

      if (data.success) {
        toast.success("PR created successfully!");
        if (data.data.pr_url) {
          window.open(data.data.pr_url, "_blank");
        }
      } else {
        toast.error(data.error || "Failed to create PR");
      }
    } catch (err) {
      toast.error("Network error");
    } finally {
      setPushing(false);
    }
  };

  const pushToMainBranch = async () => {
    setPushing(true);
    setShowPushDialog(false);

    try {
      const res = await fetch(
        `${API_URL}/api/projects/${projectId}/push-to-main`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            files: files,
            commit_message: `Update: ${refinementText.slice(0, 100)}`,
          }),
        }
      );

      const data = await res.json();

      if (data.success) {
        toast.success("Changes pushed to main branch!");
      } else {
        toast.error(data.error || "Failed to push to main");
      }
    } catch (err) {
      toast.error("Network error");
    } finally {
      setPushing(false);
    }
  };

  const handleFileSelect = (fileName: string) => {
    console.log("File selected:", fileName);
    setSelectedFile(fileName);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleRefine();
    }
  };

  const selectedFileContent =
    filesArray.find((f) => f.name === selectedFile)?.content || "";

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    );
  }

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
            <Button
              onClick={() => router.push("/workspace")}
              variant="ghost"
              size="sm"
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Workspace
            </Button>
            <div className="border-l h-6" />
            <Sparkles className="w-5 h-5 text-purple-600" />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-semibold">{project?.name || "Project"}</h1>
                <Badge
                  variant={
                    project?.status === "built" ? "default" : "secondary"
                  }
                >
                  {project?.status}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground truncate max-w-md">
                {project?.description || "Refine your MVP with AI"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              onClick={() => setShowTeamPanel(!showTeamPanel)}
              variant="outline"
              size="sm"
              className="gap-2"
            >
              <Users className="w-4 h-4" />
              Team ({stakeholders.length})
            </Button>
            {project?.github_repo && (
              <Button
                onClick={() => window.open(project.github_repo, "_blank")}
                variant="outline"
                size="sm"
                className="gap-2"
              >
                <Github className="w-4 h-4" />
                GitHub
                <ExternalLink className="w-3 h-3" />
              </Button>
            )}
            <div className="border-l h-6" />
            <div className="flex gap-2">
              <Button
                onClick={() => handlePush("branch")}
                disabled={pushing || Object.keys(files).length === 0}
                variant="outline"
                size="sm"
                className="gap-2 bg-green-50 hover:bg-green-100"
              >
                {pushing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <GitBranch className="w-4 h-4" />
                    Create PR
                  </>
                )}
              </Button>
              <Button
                onClick={() => handlePush("main")}
                disabled={pushing || Object.keys(files).length === 0}
                variant="default"
                size="sm"
                className="gap-2"
              >
                {pushing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Pushing...
                  </>
                ) : (
                  <>
                    <GitBranch className="w-4 h-4" />
                    Push to Main
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Refinement Input */}
        <div className="container mx-auto px-4 pb-3">
          <div className="flex gap-2">
            <Textarea
              placeholder="Refine your app... (e.g., 'Add dark mode toggle' or 'Make the hero section more modern with a gradient background')"
              value={refinementText}
              onChange={(e) => setRefinementText(e.target.value)}
              disabled={refining}
              rows={2}
              className="resize-none flex-1"
              onKeyDown={handleKeyDown}
            />
            <Button
              onClick={handleRefine}
              disabled={refining || !refinementText.trim()}
              size="lg"
              className="gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              {refining ? (
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
            Cmd/Ctrl + Enter to refine • {filesArray.length} files loaded from
            GitHub
          </p>
        </div>
      </div>

      {/* Resizable Split View */}
      <PanelGroup direction="horizontal" className="flex-1">
        {/* LEFT PANEL - File Tree + Code Viewer */}
        <Panel defaultSize={50} minSize={30} maxSize={70}>
          <PanelGroup direction="vertical">
            {/* File Tree Panel */}
            <Panel defaultSize={50} minSize={20}>
              <div className="h-full overflow-y-auto">
                {loadingCode ? (
                  <div className="h-full flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                  </div>
                ) : filesArray.length > 0 ? (
                  <FileTree
                    files={filesArray}
                    selectedFile={selectedFile}
                    onFileSelect={handleFileSelect}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center p-4 text-center text-sm text-muted-foreground">
                    <div>
                      <Code className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="mb-2">No files loaded yet</p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={loadCodeFiles}
                      >
                        Load Files from GitHub
                      </Button>
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
            {(refining || loadingCode) && <BuildingLoader />}

            {/* Preview iframe */}
            {previewUrl ? (
              <iframe
                key={previewUrl}
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
                  <p className="text-sm mt-2">
                    {chatId
                      ? "Submit a refinement to see updates"
                      : "No v0 preview available. Create project from scaffold page."}
                  </p>
                </div>
              </div>
            )}
          </div>
        </Panel>
      </PanelGroup>

      {/* Team Panel Overlay */}
      {showTeamPanel && stakeholders.length > 0 && (
        <div className="absolute top-16 right-4 w-80 bg-card border rounded-lg shadow-lg p-4 z-50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Users className="w-4 h-4" />
              Team Members ({stakeholders.length})
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowTeamPanel(false)}
            >
              ✕
            </Button>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {stakeholders.map((member) => (
              <div
                key={member.id}
                className="flex items-center gap-2 p-2 rounded hover:bg-muted/50"
              >
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                  {member.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{member.name}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    {member.email}
                  </p>
                </div>
                <Badge variant="secondary" className="text-xs">
                  {member.role}
                </Badge>
              </div>
            ))}
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full mt-4"
            onClick={() => {
              setShowTeamPanel(false);
              router.push(`/team/${projectId}`);
            }}
          >
            Manage Team
          </Button>
        </div>
      )}

      {/* Push to Main Warning Dialog */}
      <Dialog open={showPushDialog} onOpenChange={setShowPushDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Push to Main Branch?</DialogTitle>
            <DialogDescription>
              You're about to push changes directly to the main branch. This
              will update the production code immediately without review.
            </DialogDescription>
          </DialogHeader>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-yellow-800">Warning:</p>
            <p className="text-sm text-yellow-700 mt-1">
              Pushing to main bypasses the PR review process. Consider creating
              a branch instead if you have team members.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowPushDialog(false)}
              disabled={pushing}
            >
              Cancel
            </Button>
            <Button
              onClick={pushToMainBranch}
              disabled={pushing}
              className="bg-yellow-600 hover:bg-yellow-700"
            >
              {pushing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Pushing...
                </>
              ) : (
                "Push to Main Anyway"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
