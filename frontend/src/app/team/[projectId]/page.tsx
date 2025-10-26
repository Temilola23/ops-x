"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Users, UserPlus, Mail, Calendar } from "lucide-react";
import { isAuthenticated, getCurrentUser, logout } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8432";

interface Stakeholder {
  id: number;
  name: string;
  email: string;
  role: string;
  github_branch: string | null;
  created_at: string;
}

export default function TeamDashboard() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([]);
  const [showInvite, setShowInvite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    name: "",
    email: "",
    role: "Frontend",
  });
  const [inviteMessage, setInviteMessage] = useState("");

  useEffect(() => {
    // Check auth
    if (!isAuthenticated()) {
      router.push("/");
      return;
    }

    loadStakeholders();
  }, [projectId, router]);

  const loadStakeholders = async () => {
    try {
      const res = await fetch(
        `${API_URL}/api/projects/${projectId}/stakeholders`
      );
      const data = await res.json();
      if (data.success) {
        setStakeholders(data.data);
      }
    } catch (err) {
      console.error("Failed to load stakeholders:", err);
    }
  };

  const handleInvite = async () => {
    if (!inviteForm.name || !inviteForm.email) {
      alert("Please fill in all fields");
      return;
    }

    setLoading(true);
    setInviteMessage("");

    try {
      const res = await fetch(`${API_URL}/api/projects/${projectId}/invite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inviteForm),
      });

      const data = await res.json();

      if (data.success) {
        setInviteMessage(data.data.message);
        loadStakeholders();

        // Reset form after 5 seconds
        setTimeout(() => {
          setShowInvite(false);
          setInviteMessage("");
          setInviteForm({ name: "", email: "", role: "Frontend" });
        }, 5000);
      } else {
        alert(data.error || "Failed to send invitation");
      }
    } catch (err) {
      alert("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      Founder: "bg-purple-500 hover:bg-purple-600",
      Frontend: "bg-blue-500 hover:bg-blue-600",
      Backend: "bg-green-500 hover:bg-green-600",
      Investor: "bg-yellow-500 hover:bg-yellow-600",
      Facilitator: "bg-pink-500 hover:bg-pink-600",
    };
    return colors[role] || "bg-gray-500 hover:bg-gray-600";
  };

  const user = getCurrentUser();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Users className="h-6 w-6 text-purple-600" />
            <h1 className="text-2xl font-bold">Team Management</h1>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <span className="text-sm text-muted-foreground">
                {user.name} ({user.email})
              </span>
            )}
            <Button variant="outline" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Members</p>
                  <p className="text-3xl font-bold">{stakeholders.length}</p>
                </div>
                <Users className="h-10 w-10 text-purple-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">With Branches</p>
                  <p className="text-3xl font-bold">
                    {stakeholders.filter((s) => s.github_branch).length}
                  </p>
                </div>
                <Calendar className="h-10 w-10 text-blue-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending</p>
                  <p className="text-3xl font-bold">
                    {stakeholders.filter((s) => !s.github_branch).length}
                  </p>
                </div>
                <Mail className="h-10 w-10 text-pink-600 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Invite Form */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Team Members</h2>
          <Button
            onClick={() => setShowInvite(!showInvite)}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            {showInvite ? "Cancel" : "Invite Member"}
          </Button>
        </div>

        {showInvite && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Invite Team Member</CardTitle>
              <CardDescription>
                Send an invitation email with OTP to join the project
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={inviteForm.name}
                    onChange={(e) =>
                      setInviteForm({ ...inviteForm, name: e.target.value })
                    }
                    placeholder="John Doe"
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={inviteForm.email}
                    onChange={(e) =>
                      setInviteForm({ ...inviteForm, email: e.target.value })
                    }
                    placeholder="john@example.com"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Select
                  value={inviteForm.role}
                  onValueChange={(value) =>
                    setInviteForm({ ...inviteForm, role: value })
                  }
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Founder">Founder</SelectItem>
                    <SelectItem value="Frontend">Frontend Engineer</SelectItem>
                    <SelectItem value="Backend">Backend Engineer</SelectItem>
                    <SelectItem value="Investor">Investor</SelectItem>
                    <SelectItem value="Facilitator">Facilitator</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {inviteMessage && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <p className="text-sm font-semibold text-green-800">
                    Invitation Sent!
                  </p>
                  <p className="text-xs text-green-600 mt-1">{inviteMessage}</p>
                </div>
              )}

              <Button
                onClick={handleInvite}
                disabled={!inviteForm.name || !inviteForm.email || loading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                {loading ? "Sending Invitation..." : "Send Invitation"}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Team Members List */}
        <div className="grid gap-4">
          {stakeholders.map((member) => (
            <Card key={member.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="flex items-center justify-between p-6">
                <div className="flex items-center gap-4">
                  <div className="h-14 w-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xl">
                    {member.name.charAt(0).toUpperCase()}
                  </div>

                  <div>
                    <h3 className="font-semibold text-lg">{member.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {member.email}
                    </p>
                    {member.github_branch && (
                      <p className="text-xs text-blue-600 mt-1 font-mono">
                        Branch: {member.github_branch}
                      </p>
                    )}
                  </div>
                </div>

                <Badge
                  className={`${getRoleBadgeColor(member.role)} text-white`}
                >
                  {member.role}
                </Badge>
              </CardContent>
            </Card>
          ))}

          {stakeholders.length === 0 && !showInvite && (
            <Card>
              <CardContent className="p-12 text-center">
                <Users className="h-16 w-16 mx-auto text-muted-foreground opacity-50 mb-4" />
                <p className="text-lg font-semibold text-muted-foreground">
                  No team members yet
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Click "Invite Member" to add your first team member!
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
