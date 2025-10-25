"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Sparkles, Loader2, Zap, GitBranch, Users, Rocket } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export function LandingHero() {
  const router = useRouter();
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [isBuilding, setIsBuilding] = useState(false);

  const handleGenerate = async () => {
    if (!projectName.trim() || !description.trim()) {
      toast.error("Please fill in both fields");
      return;
    }

    setIsBuilding(true);

    // Store in sessionStorage and navigate
    sessionStorage.setItem("opsx_project_name", projectName);
    sessionStorage.setItem("opsx_project_description", description);

    router.push("/build");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="flex-1 flex items-center justify-center px-4 py-20">
        <div className="max-w-4xl w-full space-y-12">
          {/* Header */}
          <div className="text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border bg-muted/50">
              <Sparkles className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-medium">
                AI-Powered MVP Generation
              </span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
              Build Your Startup
              <br />
              <span className="bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 bg-clip-text text-transparent">
                In One Prompt
              </span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Transform your idea into a working MVP with version control,
              multiplayer collaboration, and AI-powered code reviews—all in
              minutes.
            </p>
          </div>

          {/* Input Card */}
          <Card className="border-2 shadow-xl">
            <CardContent className="p-8 space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="projectName" className="text-base">
                    Project Name
                  </Label>
                  <Input
                    id="projectName"
                    placeholder="e.g., TaskFlow, ShopMate, CalendarPro"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isBuilding}
                    className="text-lg h-12"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description" className="text-base">
                    Describe Your Idea
                  </Label>
                  <Textarea
                    id="description"
                    placeholder="Build a task management app with projects, due dates, priority levels, and team collaboration. Include a dashboard with analytics, dark mode support, and mobile-responsive design..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isBuilding}
                    rows={6}
                    className="text-base resize-none"
                  />
                  <p className="text-xs text-muted-foreground">
                    Be specific about features, design preferences, and user
                    flows. Press Cmd/Ctrl + Enter to generate.
                  </p>
                </div>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={
                  isBuilding || !projectName.trim() || !description.trim()
                }
                size="lg"
                className="w-full h-14 text-lg gap-2"
              >
                {isBuilding ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Initializing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate My MVP
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-500/10">
                <Zap className="w-6 h-6 text-purple-500" />
              </div>
              <h3 className="font-semibold">Lightning Fast</h3>
              <p className="text-sm text-muted-foreground">
                Go from idea to working app in under 60 seconds
              </p>
            </div>

            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-500/10">
                <GitBranch className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="font-semibold">Git Integration</h3>
              <p className="text-sm text-muted-foreground">
                Automatic GitHub repo with version control built-in
              </p>
            </div>

            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/10">
                <Users className="w-6 h-6 text-green-500" />
              </div>
              <h3 className="font-semibold">Team Collaboration</h3>
              <p className="text-sm text-muted-foreground">
                Invite stakeholders to refine and iterate together
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-6">
        <div className="container mx-auto px-4 flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Rocket className="w-4 h-4" />
          <span>Powered by v0.dev, Google Gemini, Fetch.ai & more</span>
        </div>
      </footer>
    </div>
  );
}
