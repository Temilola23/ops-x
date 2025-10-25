import { useEffect, useState, useCallback } from "react";
import { wsService } from "@/services/websocket";
import type { WSEvent } from "@/types";

export function useWebSocket(autoConnect = true) {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (autoConnect) {
      wsService.connect();
      setIsConnected(wsService.isConnected);
    }

    return () => {
      if (autoConnect) {
        wsService.disconnect();
      }
    };
  }, [autoConnect]);

  const on = useCallback(
    <T = any>(eventType: string, callback: (data: T) => void) => {
      return wsService.on(eventType, callback);
    },
    []
  );

  const emit = useCallback(<T = any>(eventType: string, data: T) => {
    wsService.emit(eventType, data);
  }, []);

  const joinRoom = useCallback((roomId: string) => {
    wsService.joinRoom(roomId);
  }, []);

  const leaveRoom = useCallback((roomId: string) => {
    wsService.leaveRoom(roomId);
  }, []);

  return {
    isConnected,
    on,
    emit,
    joinRoom,
    leaveRoom,
  };
}
