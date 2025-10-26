import axios, { AxiosInstance, AxiosError } from "axios";
import type {
  ApiResponse,
  AppBuildRequest,
  V0BuildRequest,
  AppBuildResponse,
  RepoPatchRequest,
  RepoPatchResponse,
  ConflictScanRequest,
  ConflictScanResponse,
  PitchGenerateResponse,
  YCPackResponse,
  Project,
  Branch,
  ChatRoom,
  ChatMessage,
  Agent,
} from "@/types";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor for auth tokens
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("auth_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem("auth_token");
          window.location.href = "/";
        }
        return Promise.reject(error);
      }
    );
  }

  // MCP Endpoints
  async buildApp(
    request: V0BuildRequest
  ): Promise<ApiResponse<AppBuildResponse>> {
    // Use PURE V0 endpoint - NO GEMINI
    const { data } = await this.client.post("/mcp/app/build/v0", request);
    return data;
  }

  async patchRepo(
    request: RepoPatchRequest
  ): Promise<ApiResponse<RepoPatchResponse>> {
    const { data } = await this.client.post("/mcp/repo/patch", request);
    return data;
  }

  async scanConflicts(
    request: ConflictScanRequest
  ): Promise<ApiResponse<ConflictScanResponse>> {
    const { data } = await this.client.post("/mcp/conflict/scan", request);
    return data;
  }

  async summarizeChat(
    chatId: string,
    role: string,
    text: string
  ): Promise<ApiResponse> {
    const { data } = await this.client.post("/mcp/chat/summarize", {
      chat_id: chatId,
      role,
      text,
    });
    return data;
  }

  async generatePitch(
    projectId: string
  ): Promise<ApiResponse<PitchGenerateResponse>> {
    const { data } = await this.client.post("/mcp/pitch/generate", {
      project_id: projectId,
    });
    return data;
  }

  async generateYCPack(
    projectId: string,
    founders: Array<{ name: string; bio: string }>,
    demoUrl: string,
    mediaUrl?: string
  ): Promise<ApiResponse<YCPackResponse>> {
    const { data } = await this.client.post("/mcp/yc/pack", {
      project_id: projectId,
      founders,
      demo_url: demoUrl,
      media_url: mediaUrl,
    });
    return data;
  }

  async exportPostmanFlow(projectId: string): Promise<ApiResponse> {
    const { data } = await this.client.post("/mcp/postman/export", {
      project_id: projectId,
    });
    return data;
  }

  // Project Management
  async getProjects(): Promise<ApiResponse<Project[]>> {
    const { data } = await this.client.get("/api/projects");
    return data;
  }

  async getProject(projectId: string): Promise<ApiResponse<Project>> {
    const { data } = await this.client.get(`/api/projects/${projectId}`);
    return data;
  }

  async createProject(
    name: string,
    prompt: string
  ): Promise<ApiResponse<Project>> {
    const { data } = await this.client.post("/api/projects", { name, prompt });
    return data;
  }

  // Branch Management
  async getBranches(projectId: string): Promise<ApiResponse<Branch[]>> {
    const { data } = await this.client.get(
      `/api/projects/${projectId}/branches`
    );
    return data;
  }

  async createBranch(
    projectId: string,
    branchName: string,
    baseBranch: string
  ): Promise<ApiResponse<Branch>> {
    const { data } = await this.client.post(
      `/api/projects/${projectId}/branches`,
      {
        name: branchName,
        base: baseBranch,
      }
    );
    return data;
  }

  // Chat Management
  async getChatRooms(projectId: string): Promise<ApiResponse<ChatRoom[]>> {
    const { data } = await this.client.get(`/api/projects/${projectId}/chats`);
    return data;
  }

  async getChatMessages(
    projectId: string
  ): Promise<ApiResponse<ChatMessage[]>> {
    const { data } = await this.client.get(
      `/api/projects/${projectId}/chat/messages`
    );
    return data;
  }

  async sendChatMessage(
    projectId: string,
    stakeholderId: number,
    message: string
  ): Promise<ApiResponse<ChatMessage>> {
    const { data } = await this.client.post(
      `/api/projects/${projectId}/chat/message`,
      {
        message,
        stakeholder_id: stakeholderId,
      }
    );
    return data;
  }

  // Agent Management
  async getAgents(projectId: string): Promise<ApiResponse<Agent[]>> {
    const { data } = await this.client.get(`/api/projects/${projectId}/agents`);
    return data;
  }

  async triggerAgent(agentId: string, task: string): Promise<ApiResponse> {
    const { data } = await this.client.post(`/api/agents/${agentId}/trigger`, {
      task,
    });
    return data;
  }

  // GitHub Integration
  async saveToGitHub(payload: {
    project_id: string;
    project_name: string;
    files: Array<{ name: string; content: string }>;
    v0_chat_id?: string;
    v0_preview_url?: string;
    description?: string;
  }): Promise<ApiResponse> {
    const { data } = await this.client.post(
      "/api/projects/save-to-github",
      payload
    );
    return data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
