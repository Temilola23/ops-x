"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { UserPlus, Mail } from "lucide-react";
import type { Stakeholder, StakeholderRole } from "@/types";

interface StakeholderDashboardProps {
  stakeholders: Stakeholder[];
  onInvite?: () => void;
}

const roleColors: Record<StakeholderRole, string> = {
  Founder: "bg-purple-500",
  Frontend: "bg-blue-500",
  Backend: "bg-green-500",
  Investor: "bg-yellow-500",
  Facilitator: "bg-pink-500",
};

const roleDescriptions: Record<StakeholderRole, string> = {
  Founder: "Project owner and decision maker",
  Frontend: "UI/UX and client-side development",
  Backend: "Server, API, and database work",
  Investor: "Strategic advisor and funding",
  Facilitator: "AI coordinator and conflict resolution",
};

export function StakeholderDashboard({
  stakeholders,
  onInvite,
}: StakeholderDashboardProps) {
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Team Stakeholders</CardTitle>
          <Button onClick={onInvite} size="sm" variant="outline">
            <UserPlus className="h-4 w-4 mr-2" />
            Invite
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {stakeholders.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <UserPlus className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No stakeholders yet</p>
              <p className="text-xs mt-1">Invite team members to collaborate</p>
            </div>
          ) : (
            stakeholders.map((stakeholder) => (
              <div
                key={stakeholder.id}
                className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <Avatar className="h-10 w-10">
                  <AvatarFallback className={roleColors[stakeholder.role]}>
                    {getInitials(stakeholder.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="font-semibold text-sm">
                    {stakeholder.name}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Mail className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      {stakeholder.email}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <Badge className={roleColors[stakeholder.role]}>
                    {stakeholder.role}
                  </Badge>
                  <p className="text-xs text-muted-foreground mt-1">
                    {roleDescriptions[stakeholder.role]}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
