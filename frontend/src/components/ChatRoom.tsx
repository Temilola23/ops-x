"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot } from "lucide-react";
import { useChatRoom } from "@/hooks/useChatRoom";
import { formatDistanceToNow } from "date-fns";
import type { StakeholderRole, ChatMessage as ChatMessageType } from "@/types";

interface ChatRoomProps {
  chatId: string;
  userRole: StakeholderRole;
  userName: string;
}

const roleColors: Record<StakeholderRole, string> = {
  Founder: "bg-purple-500",
  Frontend: "bg-blue-500",
  Backend: "bg-green-500",
  Investor: "bg-yellow-500",
  Facilitator: "bg-pink-500",
};

function ChatMessage({ message }: { message: ChatMessageType }) {
  const initials = message.author_name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <div className="flex gap-3 py-3">
      <Avatar className="h-8 w-8">
        <AvatarFallback
          className={message.is_ai ? "bg-primary" : roleColors[message.role]}
        >
          {message.is_ai ? <Bot className="h-4 w-4" /> : initials}
        </AvatarFallback>
      </Avatar>
      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">{message.author_name}</span>
          <Badge variant="outline" className="text-xs">
            {message.role}
          </Badge>
          <span className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(message.timestamp), {
              addSuffix: true,
            })}
          </span>
        </div>
        <p className="text-sm text-foreground whitespace-pre-wrap">
          {message.text}
        </p>
      </div>
    </div>
  );
}

export function ChatRoom({ chatId, userRole, userName }: ChatRoomProps) {
  const [inputMessage, setInputMessage] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage, isSending } = useChatRoom(chatId, userRole);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (inputMessage.trim() && !isSending) {
      sendMessage(inputMessage.trim());
      setInputMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="border-b">
        <CardTitle className="flex items-center justify-between">
          <span>Team Chat</span>
          <Badge className={roleColors[userRole]}>{userRole}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="space-y-1">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No messages yet. Start the conversation!
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))
            )}
          </div>
        </ScrollArea>
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              placeholder={`Message as ${userRole}...`}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isSending}
            />
            <Button
              onClick={handleSend}
              disabled={isSending || !inputMessage.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
