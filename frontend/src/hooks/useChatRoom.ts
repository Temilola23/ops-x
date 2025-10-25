import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "./useWebSocket";
import { apiClient } from "@/services/api";
import type { ChatMessage, StakeholderRole } from "@/types";

export function useChatRoom(chatId: string | null, userRole: StakeholderRole) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const { on, joinRoom, leaveRoom } = useWebSocket();
  const queryClient = useQueryClient();

  // Fetch chat history
  const { data, isLoading } = useQuery({
    queryKey: ["chat-messages", chatId],
    queryFn: () => (chatId ? apiClient.getChatMessages(chatId) : null),
    enabled: !!chatId,
  });

  useEffect(() => {
    if (data?.data) {
      setMessages(data.data);
    }
  }, [data]);

  // Join/leave chat room
  useEffect(() => {
    if (chatId) {
      joinRoom(chatId);
      return () => leaveRoom(chatId);
    }
  }, [chatId, joinRoom, leaveRoom]);

  // Listen for new messages
  useEffect(() => {
    const unsubscribe = on<ChatMessage>("chat:message", (message) => {
      if (message.chat_id === chatId) {
        setMessages((prev) => [...prev, message]);
      }
    });

    return () => unsubscribe();
  }, [on, chatId]);

  // Send message mutation
  const sendMessage = useMutation({
    mutationFn: (text: string) => {
      if (!chatId) throw new Error("No chat ID");
      return apiClient.sendChatMessage(chatId, userRole, text);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-messages", chatId] });
    },
  });

  return {
    messages,
    isLoading,
    sendMessage: sendMessage.mutate,
    isSending: sendMessage.isPending,
  };
}
