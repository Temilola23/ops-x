import { io, Socket } from "socket.io-client";
import type { WSEvent } from "@/types";

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  connect(url?: string) {
    if (this.socket?.connected) {
      return;
    }

    const wsUrl =
      url || process.env.NEXT_PUBLIC_WS_URL || "http://localhost:8432";

    this.socket = io(wsUrl, {
      transports: ["websocket"],
      auth: {
        token: localStorage.getItem("auth_token"),
      },
    });

    this.socket.on("connect", () => {
      console.log("WebSocket connected");
    });

    this.socket.on("disconnect", () => {
      console.log("WebSocket disconnected");
    });

    this.socket.on("error", (error) => {
      console.error("WebSocket error:", error);
    });

    // Generic event handler
    this.socket.onAny((eventType: string, data: any) => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.forEach((callback) => callback(data));
      }
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on<T = any>(eventType: string, callback: (data: T) => void) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(callback);
      }
    };
  }

  emit<T = any>(eventType: string, data: T) {
    if (this.socket?.connected) {
      this.socket.emit(eventType, data);
    } else {
      console.warn("Cannot emit event: WebSocket not connected");
    }
  }

  joinRoom(roomId: string) {
    this.emit("join_room", { room_id: roomId });
  }

  leaveRoom(roomId: string) {
    this.emit("leave_room", { room_id: roomId });
  }

  sendMessage(chatId: string, message: string, role: string) {
    this.emit("chat:message", {
      chat_id: chatId,
      text: message,
      role,
      timestamp: new Date(),
    });
  }

  get isConnected(): boolean {
    return this.socket?.connected ?? false;
  }
}

export const wsService = new WebSocketService();
export default wsService;
