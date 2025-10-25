// Core project types
export interface Project {
  id: string;
  name: string;
  owner_id: string;
  creao_project_id?: string;
  app_url?: string;
  default_branch: string;
  created_at: Date;
  updated_at: Date;
}

// Branch types
export interface Branch {
  name: string;
  base_sha: string;
  status: "active" | "merged" | "closed";
  author_id: string;
  pr_url?: string;
  mergeable: boolean;
  created_at: Date;
}

// Stakeholder roles
export type StakeholderRole =
  | "Founder"
  | "Frontend"
  | "Backend"
  | "Investor"
  | "Facilitator";

export interface Stakeholder {
  id: string;
  name: string;
  email: string;
  role: StakeholderRole;
  avatar?: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  chat_id: string;
  role: StakeholderRole;
  author_id: string;
  author_name: string;
  text: string;
  timestamp: Date;
  is_ai?: boolean;
}

export interface ChatRoom {
  id: string;
  project_id: string;
  name: string;
  participants: Stakeholder[];
  created_at: Date;
}

// Agent types
export type AgentType =
  | "planner"
  | "frontend"
  | "backend"
  | "facilitator"
  | "pitch";
export type AgentStatus = "idle" | "thinking" | "executing" | "error";

export interface Agent {
  id: string;
  type: AgentType;
  name: string;
  status: AgentStatus;
  current_task?: string;
  agentverse_url?: string;
}

// Conflict types
export interface Conflict {
  type: "schema" | "api" | "auth" | "ui";
  files: string[];
  description: string;
  suggestion: string;
  severity: "low" | "medium" | "high";
}

// MCP Request/Response types
export interface AppBuildRequest {
  project_id: string;
  spec: {
    name: string;
    entities: Array<{ name: string; fields: string[] }>;
    pages: string[];
    requirements: string[];
  };
}

export interface AppBuildResponse {
  app_url: string;
  repo_url?: string;
  components: Array<{ id: string; type: string }>;
  api_schema: Array<{
    path: string;
    method: string;
    input: string;
    output: string;
  }>;
  status: string;
}

export interface RepoPatchRequest {
  repo: string;
  branch: string;
  files: Array<{
    path: string;
    content: string;
    mode: "file" | "tree";
  }>;
  commit_message: string;
}

export interface RepoPatchResponse {
  commit_sha: string;
  pr_url: string;
  status: "created" | "updated" | "error";
}

export interface ConflictScanRequest {
  repo: string;
  branches: string[];
  focus: string[];
}

export interface ConflictScanResponse {
  conflicts: Conflict[];
}

export interface PitchGenerateResponse {
  script: string;
  slides_md: string;
  audio_url?: string;
}

export interface YCPackResponse {
  yc_json: Record<string, any>;
  yc_pdf_path: string;
}

// Artifact types
export type ArtifactType =
  | "spec"
  | "flow_json"
  | "audio"
  | "pdf"
  | "transcript"
  | "slides";

export interface Artifact {
  id: string;
  type: ArtifactType;
  project_id: string;
  sha256: string;
  url: string;
  created_at: Date;
}

// WebSocket event types
export type WSEventType =
  | "chat:message"
  | "agent:status"
  | "branch:update"
  | "conflict:detected"
  | "build:progress"
  | "pr:review";

export interface WSEvent<T = any> {
  type: WSEventType;
  payload: T;
  timestamp: Date;
}

// API Response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
