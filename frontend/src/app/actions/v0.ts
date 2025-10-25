"use server";

import { v0 } from "v0-sdk";

/**
 * Server Action: Create a new v0 chat
 * This runs on the server, keeping the V0_API_KEY secure
 */
export async function createV0Chat(message: string) {
  try {
    console.log("Creating v0 chat with message:", message.substring(0, 100));

    // v0 SDK automatically uses V0_API_KEY from environment
    const chat = await v0.chats.create({ message });

    // Handle both ChatDetail and streaming response types
    const chatId = "id" in chat ? chat.id : "";
    const previewUrl = "demo" in chat ? chat.demo : "";
    const files = "files" in chat && chat.files ? chat.files : [];

    console.log("v0 chat created:", chatId);

    return {
      success: true,
      data: {
        chatId,
        previewUrl, // This is the iframe URL
        files: files.map((f: any) => ({
          name: f.name || "",
          content: f.content || "",
        })),
      },
    };
  } catch (error: any) {
    console.error("v0 create error:", error);
    return {
      success: false,
      error: error.message || "Failed to create chat with v0",
    };
  }
}

/**
 * Server Action: Send a follow-up message to refine the app
 * This allows iterative refinement like "Add dark mode" or "Make it responsive"
 */
export async function sendV0Message(chatId: string, message: string) {
  try {
    console.log(
      "Sending v0 message to chat:",
      chatId,
      "message:",
      message.substring(0, 100)
    );

    const response = await v0.chats.sendMessage({
      chatId,
      message,
    });

    // Handle response types
    const previewUrl = "demo" in response ? response.demo : "";
    const files = "files" in response && response.files ? response.files : [];

    console.log("v0 message sent successfully");

    return {
      success: true,
      data: {
        previewUrl, // Updated preview URL
        files: files.map((f: any) => ({
          name: f.name || "",
          content: f.content || "",
        })),
      },
    };
  } catch (error: any) {
    console.error("v0 sendMessage error:", error);
    return {
      success: false,
      error: error.message || "Failed to send message to v0",
    };
  }
}

/**
 * Server Action: Get chat history (optional, for future use)
 */
export async function getV0Chat(chatId: string) {
  try {
    // This would fetch chat details if v0 SDK supports it
    // For now, just return structure
    return {
      success: true,
      data: {
        chatId,
        // Can be extended when v0 SDK supports chat retrieval
      },
    };
  } catch (error: any) {
    console.error("v0 getChat error:", error);
    return {
      success: false,
      error: error.message || "Failed to get chat from v0",
    };
  }
}
