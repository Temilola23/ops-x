import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/services/api";
import type { Project } from "@/types";

export function useProject(projectId: string | null) {
  const queryClient = useQueryClient();

  // Fetch single project
  const { data, isLoading, error } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => (projectId ? apiClient.getProject(projectId) : null),
    enabled: !!projectId,
  });

  return {
    project: data?.data,
    isLoading,
    error,
  };
}

export function useProjects() {
  const queryClient = useQueryClient();

  // Fetch all projects
  const { data, isLoading, error } = useQuery({
    queryKey: ["projects"],
    queryFn: () => apiClient.getProjects(),
  });

  // Create project mutation
  const createProject = useMutation({
    mutationFn: ({ name, prompt }: { name: string; prompt: string }) =>
      apiClient.createProject(name, prompt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  return {
    projects: data?.data || [],
    isLoading,
    error,
    createProject: createProject.mutate,
    isCreating: createProject.isPending,
  };
}
