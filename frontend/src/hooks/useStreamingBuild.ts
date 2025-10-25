import { useState, useCallback } from "react";
import type { AppBuildRequest } from "@/types";

interface BuildStatus {
  type: string;
  phase?: string;
  message?: string;
  progress?: number;
  filename?: string;
  content?: string;
  html?: string;
  repo_url?: string;
  app_url?: string;
  error?: string;
}

export function useStreamingBuild() {
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [previewHtml, setPreviewHtml] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startBuild = useCallback(async (request: AppBuildRequest) => {
    setIsBuilding(true);
    setError(null);
    setFiles([]);
    setProgress(0);
    setPreviewHtml("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/mcp/app/build/hybrid`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ...request,
            use_v0: true, // Enable V0 for beautiful UI
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Build failed: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data: BuildStatus = JSON.parse(line.substring(6));

              switch (data.type) {
                case "status":
                  setStatus(data.message || "");
                  if (data.progress) setProgress(data.progress);
                  break;

                case "file_created":
                  if (data.filename) {
                    setFiles((prev) => [...prev, data.filename!]);
                  }
                  break;

                case "preview_ready":
                  if (data.html) {
                    setPreviewHtml(data.html);
                  }
                  break;

                case "complete":
                  setIsBuilding(false);
                  return {
                    repo_url: data.repo_url,
                    app_url: data.app_url,
                  };

                case "error":
                  throw new Error(data.message || "Build failed");
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Build failed");
      setIsBuilding(false);
      throw err;
    }
  }, []);

  return {
    startBuild,
    status,
    progress,
    previewHtml,
    files,
    isBuilding,
    error,
  };
}
