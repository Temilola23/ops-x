"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  GitBranch,
  GitMerge,
  ExternalLink,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/services/api";
import type { Branch } from "@/types";

interface BranchVisualizerProps {
  projectId: string;
  onCreateBranch?: () => void;
}

const statusConfig = {
  active: {
    color: "bg-blue-500",
    icon: <GitBranch className="h-3 w-3" />,
    label: "Active",
  },
  merged: {
    color: "bg-green-500",
    icon: <CheckCircle className="h-3 w-3" />,
    label: "Merged",
  },
  closed: {
    color: "bg-gray-500",
    icon: <AlertCircle className="h-3 w-3" />,
    label: "Closed",
  },
};

export function BranchVisualizer({
  projectId,
  onCreateBranch,
}: BranchVisualizerProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["branches", projectId],
    queryFn: () => apiClient.getBranches(projectId),
    refetchInterval: 10000,
  });

  const branches = data?.data || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Branches
          </CardTitle>
          <Button onClick={onCreateBranch} size="sm" variant="outline">
            <GitBranch className="h-4 w-4 mr-2" />
            New Branch
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading branches...
          </div>
        ) : branches.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <GitBranch className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No branches yet</p>
            <p className="text-xs mt-1">Create a branch to start working</p>
          </div>
        ) : (
          <div className="space-y-3">
            {branches.map((branch) => {
              const config = statusConfig[branch.status];
              return (
                <div
                  key={branch.name}
                  className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold">
                        {branch.name}
                      </span>
                      <Badge
                        variant="outline"
                        className={`${config.color} text-white border-0 gap-1`}
                      >
                        {config.icon}
                        {config.label}
                      </Badge>
                      {!branch.mergeable && (
                        <Badge variant="destructive" className="gap-1">
                          <AlertCircle className="h-3 w-3" />
                          Conflicts
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>Base: {branch.base_sha.slice(0, 7)}</span>
                      <span>Author: {branch.author_id}</span>
                      <span>
                        {new Date(branch.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  {branch.pr_url && (
                    <Button variant="ghost" size="sm" asChild>
                      <a
                        href={branch.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <GitMerge className="h-4 w-4 mr-2" />
                        View PR
                        <ExternalLink className="h-3 w-3 ml-1" />
                      </a>
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
