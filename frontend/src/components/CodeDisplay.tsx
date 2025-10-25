"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Copy, Check, FileCode } from "lucide-react";
import { toast } from "sonner";

interface V0File {
  name: string;
  content: string;
}

interface CodeDisplayProps {
  files: V0File[];
}

export function CodeDisplay({ files }: CodeDisplayProps) {
  const [copiedFile, setCopiedFile] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState(files[0]?.name || "");

  const copyToClipboard = async (content: string, fileName: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFile(fileName);
      toast.success(`Copied ${fileName} to clipboard`);
      setTimeout(() => setCopiedFile(null), 2000);
    } catch (err) {
      toast.error("Failed to copy code");
    }
  };

  if (files.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center space-y-2">
          <FileCode className="w-12 h-12 mx-auto opacity-20" />
          <p className="text-sm">No files generated yet</p>
        </div>
      </div>
    );
  }

  // Group files by directory
  const fileTree = files.reduce((acc, file) => {
    const parts = file.name.split("/");
    const dir = parts.length > 1 ? parts[0] : "root";
    if (!acc[dir]) acc[dir] = [];
    acc[dir].push(file);
    return acc;
  }, {} as Record<string, V0File[]>);

  return (
    <div className="h-full flex flex-col">
      {/* File Stats */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">
            {files.length} files generated
          </span>
        </div>
        <div className="flex gap-2">
          {Object.keys(fileTree).map((dir, index) => (
            <Badge
              key={`${dir}-${index}`}
              variant="outline"
              className="text-xs"
            >
              {dir}: {fileTree[dir].length}
            </Badge>
          ))}
        </div>
      </div>

      {/* File Tabs */}
      <Tabs
        value={selectedFile}
        onValueChange={setSelectedFile}
        className="flex-1 flex flex-col"
      >
        <ScrollArea className="border-b">
          <TabsList className="w-full justify-start h-auto p-2 bg-transparent">
            {files.map((file) => (
              <TabsTrigger
                key={file.name}
                value={file.name}
                className="text-xs font-mono px-3 py-1.5 data-[state=active]:bg-accent"
              >
                {file.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </ScrollArea>

        {/* File Content */}
        {files.map((file) => (
          <TabsContent
            key={file.name}
            value={file.name}
            className="flex-1 m-0 relative"
          >
            <Card className="h-full m-4 flex flex-col border-2">
              {/* File Header */}
              <div className="flex items-center justify-between p-3 border-b bg-muted/30">
                <div className="flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-mono font-semibold">
                    {file.name}
                  </span>
                  <Badge variant="secondary" className="text-xs">
                    {file.content.split("\n").length} lines
                  </Badge>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(file.content, file.name)}
                  className="gap-2"
                >
                  {copiedFile === file.name ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy
                    </>
                  )}
                </Button>
              </div>

              {/* Code Content */}
              <ScrollArea className="flex-1 p-4">
                <pre className="text-xs font-mono leading-relaxed">
                  <code className="text-foreground">{file.content}</code>
                </pre>
              </ScrollArea>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
