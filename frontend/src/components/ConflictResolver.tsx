"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, CheckCircle, FileCode, Lightbulb } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/services/api";
import { toast } from "sonner";
import type { Conflict } from "@/types";

interface ConflictResolverProps {
  projectId: string;
  conflicts: Conflict[];
  onRefresh?: () => void;
}

const severityConfig = {
  low: { color: "bg-yellow-500", label: "Low" },
  medium: { color: "bg-orange-500", label: "Medium" },
  high: { color: "bg-red-500", label: "High" },
};

const typeConfig = {
  schema: { icon: "📊", label: "Schema" },
  api: { icon: "🔌", label: "API" },
  auth: { icon: "🔒", label: "Auth" },
  ui: { icon: "🎨", label: "UI" },
};

export function ConflictResolver({
  projectId,
  conflicts,
  onRefresh,
}: ConflictResolverProps) {
  const queryClient = useQueryClient();
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const resolveConflict = useMutation({
    mutationFn: async (conflict: Conflict) => {
      // This would call an endpoint to automatically resolve the conflict
      // For now, it's a placeholder
      return new Promise((resolve) => setTimeout(resolve, 2000));
    },
    onSuccess: () => {
      toast.success("Conflict resolved!");
      onRefresh?.();
      setResolvingId(null);
    },
    onError: () => {
      toast.error("Failed to resolve conflict");
      setResolvingId(null);
    },
  });

  const handleResolve = (conflict: Conflict, index: number) => {
    setResolvingId(`${conflict.type}-${index}`);
    resolveConflict.mutate(conflict);
  };

  if (conflicts.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8 text-green-600">
          <CheckCircle className="h-5 w-5 mr-2" />
          No conflicts detected
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-orange-500" />
          Conflicts Detected ({conflicts.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {conflicts.map((conflict, index) => {
          const type = typeConfig[conflict.type];
          const severity = severityConfig[conflict.severity];
          const conflictId = `${conflict.type}-${index}`;
          const isResolving = resolvingId === conflictId;

          return (
            <Alert key={conflictId} variant="destructive" className="relative">
              <AlertDescription>
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{type.icon}</span>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold">
                            {type.label} Conflict
                          </span>
                          <Badge
                            variant="outline"
                            className={`${severity.color} text-white border-0`}
                          >
                            {severity.label}
                          </Badge>
                        </div>
                        <p className="text-sm">{conflict.description}</p>
                      </div>
                    </div>
                  </div>

                  <div className="pl-9">
                    <div className="space-y-2">
                      <div className="flex items-start gap-2 text-xs">
                        <FileCode className="h-4 w-4 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-medium">Affected files:</span>
                          <div className="mt-1 space-y-0.5">
                            {conflict.files.map((file) => (
                              <div
                                key={file}
                                className="font-mono text-muted-foreground"
                              >
                                {file}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-start gap-2 text-xs bg-blue-50 dark:bg-blue-950 p-2 rounded">
                        <Lightbulb className="h-4 w-4 flex-shrink-0 mt-0.5 text-blue-500" />
                        <div>
                          <span className="font-medium text-blue-700 dark:text-blue-300">
                            Suggestion:
                          </span>
                          <p className="mt-1 text-blue-600 dark:text-blue-400">
                            {conflict.suggestion}
                          </p>
                        </div>
                      </div>
                    </div>

                    <Button
                      onClick={() => handleResolve(conflict, index)}
                      disabled={isResolving}
                      size="sm"
                      className="mt-3"
                    >
                      {isResolving ? "Resolving..." : "Apply Suggestion"}
                    </Button>
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          );
        })}
      </CardContent>
    </Card>
  );
}
