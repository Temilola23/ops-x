import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "./useWebSocket";
import { apiClient } from "@/services/api";
import type { ChatMessage, StakeholderRole } from "@/types";

interface UseChatRoomProps {
  projectId: string | null;
  stakeholderId: number | null;
  userRole: StakeholderRole;
}

export function useChatRoom({
  projectId,
  stakeholderId,
  userRole,
}: UseChatRoomProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const { on, joinRoom, leaveRoom } = useWebSocket();
  const queryClient = useQueryClient();

  // Fetch chat history
  const { data, isLoading } = useQuery({
    queryKey: ["chat-messages", projectId],
    queryFn: () => (projectId ? apiClient.getChatMessages(projectId) : null),
    enabled: !!projectId,
  });

  useEffect(() => {
    if (data?.data) {
      setMessages(data.data);
    }
  }, [data]);

  // Join/leave chat room (use projectId as room)
  useEffect(() => {
    if (projectId) {
      joinRoom(projectId);
      return () => leaveRoom(projectId);
    }
  }, [projectId, joinRoom, leaveRoom]);

  // Listen for new messages
  useEffect(() => {
    const unsubscribe = on<any>("chat:message", (payload) => {
      if (payload.project_id === parseInt(projectId || "0")) {
        // Add new messages to the list (deduplicate by ID)
        if (payload.messages && Array.isArray(payload.messages)) {
          setMessages((prev) => {
            const existingIds = new Set(prev.map((m) => m.id));
            const newMessages = payload.messages.filter(
              (msg: ChatMessage) => !existingIds.has(msg.id)
            );
            return [...prev, ...newMessages];
          });
        }
      }
    });

    return () => unsubscribe();
  }, [on, projectId]);

  // Send message mutation
  const sendMessage = useMutation({
    mutationFn: (text: string) => {
      if (!projectId || !stakeholderId)
        throw new Error("No project or stakeholder ID");
      return apiClient.sendChatMessage(projectId, stakeholderId, text);
    },
    onSuccess: (response) => {
      // Messages already added via WebSocket, but we can handle errors here
      if (!response.success) {
        console.error("Failed to send message:", response.error);
      }
    },
  });

  return {
    messages,
    isLoading,
    sendMessage: sendMessage.mutate,
    isSending: sendMessage.isPending,
  };
}
