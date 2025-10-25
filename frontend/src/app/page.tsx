"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { CreaoPromptInput } from "@/components/CreaoPromptInput";
import { Button } from "@/components/ui/button";
import { Sparkles, GitBranch, Users, Zap } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [showPrompt, setShowPrompt] = useState(false);

  const handleProjectCreated = (projectId: string) => {
    router.push(`/dashboard/${projectId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="w-12 h-12 text-primary" />
            <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              OPS-X
            </h1>
          </div>
          <p className="text-2xl text-muted-foreground mb-8">
            One-Prompt Startup Platform
          </p>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Turn a single idea into a working MVP with AI agents, Git-style
            collaboration, and automated workflows. Built for Cal Hacks 12.0.
          </p>
        </div>

        {/* Features */}
        {!showPrompt && (
          <div className="grid md:grid-cols-3 gap-6 mb-12 max-w-5xl mx-auto">
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
              <Sparkles className="w-8 h-8 text-purple-500 mb-4" />
              <h3 className="text-xl font-bold mb-2">One Prompt Build</h3>
              <p className="text-muted-foreground text-sm">
                Describe your startup idea and watch AI agents build a working
                MVP using Creao
              </p>
            </div>
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
              <GitBranch className="w-8 h-8 text-blue-500 mb-4" />
              <h3 className="text-xl font-bold mb-2">Git-Style Branching</h3>
              <p className="text-muted-foreground text-sm">
                Stakeholders can branch, iterate, and merge with automated
                conflict detection
              </p>
            </div>
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
              <Users className="w-8 h-8 text-green-500 mb-4" />
              <h3 className="text-xl font-bold mb-2">Multiplayer Chat</h3>
              <p className="text-muted-foreground text-sm">
                Role-based collaboration with Janitor AI facilitating decisions
              </p>
            </div>
          </div>
        )}

        {/* CTA or Prompt Input */}
        <div className="max-w-4xl mx-auto">
          {!showPrompt ? (
            <div className="text-center">
              <Button
                size="lg"
                onClick={() => setShowPrompt(true)}
                className="text-lg px-8 py-6"
              >
                <Zap className="mr-2 h-5 w-5" />
                Start Building Your Startup
              </Button>
              <p className="mt-4 text-sm text-muted-foreground">
                Powered by Creao, Fetch.ai, Janitor AI, and more
              </p>
            </div>
          ) : (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <CreaoPromptInput onProjectCreated={handleProjectCreated} />
            </div>
          )}
        </div>

        {/* Tech Stack */}
        <div className="mt-20 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Integrates with industry-leading platforms
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-xs text-muted-foreground">
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              Creao
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              Fetch.ai
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              Janitor AI
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              Postman
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              CodeRabbit
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              Chroma
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full">
              Deepgram
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
