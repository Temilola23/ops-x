import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useWebSocket } from "./useWebSocket";
import { apiClient } from "@/services/api";
import type { Agent } from "@/types";

export function useAgentStatus(projectId: string | null) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const { on } = useWebSocket();

  // Fetch initial agent data
  const { data, isLoading, error } = useQuery({
    queryKey: ["agents", projectId],
    queryFn: () => (projectId ? apiClient.getAgents(projectId) : null),
    enabled: !!projectId,
    refetchInterval: 10000, // Refetch every 10 seconds as fallback
  });

  useEffect(() => {
    if (data?.data) {
      setAgents(data.data);
    }
  }, [data]);

  // Listen for real-time agent status updates
  useEffect(() => {
    const unsubscribe = on("agent:status", (updatedAgent: Agent) => {
      setAgents((prev) =>
        prev.map((agent) =>
          agent.id === updatedAgent.id ? updatedAgent : agent
        )
      );
    });

    return () => {
      unsubscribe();
    };
  }, [on]);

  return {
    agents,
    isLoading,
    error,
  };
}
