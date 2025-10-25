"use server";

import { v0 } from "v0-sdk";

/**
 * Server Action: Create a new v0 chat with enhanced configuration
 * This runs on the server, keeping the V0_API_KEY secure
 *
 * Uses v0 Platform API features:
 * - system context for better results
 * - modelConfiguration for control
 * - proper response handling with latestVersion
 */
export async function createV0Chat(message: string) {
  try {
    console.log("Creating v0 chat with message:", message.substring(0, 100));

    // Create chat with system context and model configuration
    // Reference: https://v0.app/docs/api/platform/reference/chats/create
    const chat = await v0.chats.create({
      message,
      system:
        "You are an expert full-stack developer specializing in modern web applications. Create production-ready code using Next.js 14, React, TypeScript, Tailwind CSS, and shadcn/ui components. Ensure the code is clean, well-structured, and follows best practices.",
      modelConfiguration: {
        thinking: true, // Enable multi-step thinking for better results
        imageGenerations: false, // Disable image generation for faster response
      },
    });

    console.log("v0 chat response:", JSON.stringify(chat, null, 2));

    // Extract data from response according to v0 API structure
    const chatId = "id" in chat ? chat.id : "";

    // Files and demo URL are in latestVersion object
    const latestVersion = "latestVersion" in chat ? chat.latestVersion : null;
    const previewUrl = latestVersion?.demoUrl || "";
    const files = latestVersion?.files || [];

    console.log("Extracted data:", {
      chatId,
      previewUrl,
      fileCount: files.length,
      files: files.map((f: any) => f.name || f.path || "unknown"),
    });

    return {
      success: true,
      data: {
        chatId,
        previewUrl,
        files: files.map((f: any) => ({
          name: f.name || f.path || "",
          content: f.content || f.source || "",
        })),
      },
    };
  } catch (error: any) {
    console.error("v0 create error:", error);
    console.error("Error details:", JSON.stringify(error, null, 2));
    return {
      success: false,
      error: error.message || "Failed to create chat with v0",
    };
  }
}

/**
 * Server Action: Send a follow-up message to refine the app
 * This allows iterative refinement like "Add dark mode" or "Make it responsive"
 *
 * Reference: https://v0.app/docs/api/platform/reference/chats/create
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

    console.log("v0 sendMessage response:", JSON.stringify(response, null, 2));

    // Extract data from response - files are in latestVersion
    const latestVersion =
      "latestVersion" in response ? response.latestVersion : null;
    const previewUrl = latestVersion?.demoUrl || "";
    const files = latestVersion?.files || [];

    console.log("Extracted refinement data:", {
      previewUrl,
      fileCount: files.length,
      files: files.map((f: any) => f.name || f.path || "unknown"),
    });

    return {
      success: true,
      data: {
        previewUrl,
        files: files.map((f: any) => ({
          name: f.name || f.path || "",
          content: f.content || f.source || "",
        })),
      },
    };
  } catch (error: any) {
    console.error("v0 sendMessage error:", error);
    console.error("Error details:", JSON.stringify(error, null, 2));
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
