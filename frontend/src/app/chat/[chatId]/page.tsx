"use client";

import { use } from "react";
import { ChatRoom } from "@/components/ChatRoom";
import { AgentPanel } from "@/components/AgentPanel";
import { Button } from "@/components/ui/button";
import { Home, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface PageProps {
  params: Promise<{ chatId: string }>;
}

export default function ChatPage({ params }: PageProps) {
  const { chatId } = use(params);
  const router = useRouter();

  // TODO: Fetch actual user role and project ID from context/auth
  const userRole = "Founder" as const;
  const userName = "Current User";
  const projectId = chatId; // Using chatId as projectId for now

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
                  Team Collaboration
                </p>
              </div>
            </div>
            <Button asChild variant="outline">
              <Link href={`/dashboard/${projectId}`}>
                <Home className="mr-2 h-4 w-4" />
                Dashboard
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Chat */}
          <div className="lg:col-span-2">
            <ChatRoom chatId={chatId} userRole={userRole} userName={userName} />
          </div>

          {/* Right Column - Agents */}
          <div>
            <AgentPanel projectId={projectId} />
          </div>
        </div>
      </div>
    </div>
  );
}
