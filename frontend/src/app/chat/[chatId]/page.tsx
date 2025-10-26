"use client";

import { use, useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
import { ChatRoom } from "@/components/ChatRoom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Home, ArrowLeft, Loader2, MessageSquare } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PageProps {
  params: Promise<{ chatId: string }>;
}

interface Project {
  id: number;
  name: string;
  status: string;
}

interface Stakeholder {
  id: number;
  name: string;
  email: string;
  role: string;
  status: string;
}

export default function ChatPage({ params }: PageProps) {
  const { chatId } = use(params);
  const router = useRouter();
  const { user, isLoaded } = useUser();

  const [project, setProject] = useState<Project | null>(null);
  const [stakeholder, setStakeholder] = useState<Stakeholder | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // chatId is actually projectId
  const projectId = chatId;

  useEffect(() => {
    if (isLoaded && user) {
      loadChatData();
    }
  }, [isLoaded, user, projectId]);

  // Listen for preview URL updates via polling
  useEffect(() => {
    if (!projectId) return;

    const checkForUpdates = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/projects/${projectId}`);
        const data = await response.json();
        if (data.success && data.data.v0_preview_url !== previewUrl) {
          console.log("🔄 Preview URL updated:", data.data.v0_preview_url);
          setPreviewUrl(data.data.v0_preview_url);
          toast.success("Preview updated! Check the changes →");
        }
      } catch (err) {
        console.error("Failed to check for updates:", err);
      }
    }, 5000); // Check every 5 seconds

    return () => clearInterval(checkForUpdates);
  }, [projectId, previewUrl]);

  const loadChatData = async () => {
    try {
      // Ensure User record exists for Clerk user
      if (user?.id && user?.emailAddresses[0]?.emailAddress) {
        console.log("Ensuring User record exists for Clerk user...");
        await fetch(`${API_URL}/api/auth/clerk-user`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clerk_user_id: user.id,
            email: user.emailAddresses[0].emailAddress,
            name: user.fullName || user.firstName,
          }),
        });
      }

      // Load project
      const projectRes = await fetch(`${API_URL}/api/projects/${projectId}`);
      const projectData = await projectRes.json();

      if (!projectData.success) {
        toast.error("Project not found");
        router.push("/workspace");
        return;
      }

      setProject(projectData.data);
      setPreviewUrl(projectData.data.v0_preview_url);

      // Load stakeholders and find current user
      const stakeholdersRes = await fetch(
        `${API_URL}/api/projects/${projectId}/stakeholders`
      );
      const stakeholdersData = await stakeholdersRes.json();

      if (stakeholdersData.success && Array.isArray(stakeholdersData.data)) {
        // Find current user's stakeholder record
        let userStakeholder = stakeholdersData.data.find(
          (s: Stakeholder) => s.email === user?.emailAddresses[0]?.emailAddress
        );

        // If no stakeholder found, auto-create one for the user
        if (!userStakeholder) {
          const currentUserEmail = user?.emailAddresses[0]?.emailAddress;

          if (currentUserEmail) {
            console.log("User not found in stakeholders, creating record...");

            try {
              const createStakeholderRes = await fetch(
                `${API_URL}/api/projects/${projectId}/stakeholders`,
                {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    name: user?.fullName || user?.firstName || "Project Member",
                    email: currentUserEmail,
                    role: "Founder", // Default role - can be changed later
                  }),
                }
              );

              const createResult = await createStakeholderRes.json();
              if (createResult.success) {
                console.log(
                  "✅ Created stakeholder record:",
                  createResult.data
                );
                userStakeholder = {
                  id: createResult.data.id,
                  name: createResult.data.name,
                  email: createResult.data.email,
                  role: createResult.data.role,
                  status: createResult.data.status || "active",
                };
                toast.success("Welcome to the chat!");
              }
            } catch (err) {
              console.error("Failed to create stakeholder:", err);
            }
          }
        }

        if (userStakeholder) {
          setStakeholder(userStakeholder);
        } else {
          // User is not a stakeholder and couldn't be added
          toast.error("You are not a member of this project");
          router.push("/workspace");
          return;
        }
      }
    } catch (err) {
      console.error("Failed to load chat data:", err);
      toast.error("Failed to load chat");
    } finally {
      setLoading(false);
    }
  };

  if (!isLoaded || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-[400px]">
          <CardContent className="p-12 text-center">
            <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-purple-600" />
            <p className="text-muted-foreground">Loading chat room...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!project || !stakeholder) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-[400px]">
          <CardContent className="p-12 text-center">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-xl font-semibold mb-2">Chat not available</h3>
            <p className="text-muted-foreground mb-6">
              Unable to load this chat room.
            </p>
            <Button onClick={() => router.push("/workspace")}>
              Back to Workspace
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <Link href="/" className="text-2xl font-bold text-primary">
                  OPS-X
                </Link>
                <p className="text-sm text-muted-foreground">
                  {project.name} • Team Chat
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button asChild variant="outline" size="sm">
                <Link href={`/refine/${projectId}`}>
                  <Home className="mr-2 h-4 w-4" />
                  Project
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Chat */}
          <div className="lg:col-span-1">
            <ChatRoom
              projectId={projectId}
              stakeholderId={stakeholder.id}
              userRole={stakeholder.role as any}
              userName={stakeholder.name}
            />
          </div>

          {/* Right Column - Live Preview */}
          <div className="lg:col-span-2">
            <Card className="h-[calc(100vh-100px)] flex flex-col">
              <CardHeader className="border-b">
                <CardTitle className="flex items-center gap-2">
                  <span>Live Preview</span>
                  <Badge variant="outline" className="text-xs">
                    Updates automatically
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 p-0">
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
                    <div className="text-center p-8">
                      <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-20" />
                      <p>Preview will appear here</p>
                      <p className="text-sm mt-2">
                        Request UI changes in chat to see updates
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
