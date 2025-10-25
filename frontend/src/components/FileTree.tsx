"use client";

import { useState } from "react";
import {
  ChevronRight,
  ChevronDown,
  File,
  Folder,
  FolderOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";

interface V0File {
  name: string;
  content: string;
}

interface FileTreeProps {
  files: V0File[];
  selectedFile: string;
  onFileSelect: (fileName: string) => void;
}

interface FileNode {
  name: string;
  path: string;
  type: "file" | "folder";
  children?: FileNode[];
  content?: string;
}

function buildFileTree(files: V0File[]): FileNode[] {
  const root: FileNode[] = [];
  const folderMap = new Map<string, FileNode>();

  files.forEach((file) => {
    const parts = file.name.split("/");
    let currentPath = "";
    let currentLevel = root;

    parts.forEach((part, index) => {
      currentPath = currentPath ? `${currentPath}/${part}` : part;
      const isFile = index === parts.length - 1;

      if (isFile) {
        currentLevel.push({
          name: part,
          path: file.name,
          type: "file",
          content: file.content,
        });
      } else {
        let folder = folderMap.get(currentPath);
        if (!folder) {
          folder = {
            name: part,
            path: currentPath,
            type: "folder",
            children: [],
          };
          folderMap.set(currentPath, folder);
          currentLevel.push(folder);
        }
        currentLevel = folder.children!;
      }
    });
  });

  return root;
}

function FileTreeNode({
  node,
  level = 0,
  selectedFile,
  onFileSelect,
}: {
  node: FileNode;
  level?: number;
  selectedFile: string;
  onFileSelect: (fileName: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(true);
  const isSelected = node.type === "file" && node.path === selectedFile;

  if (node.type === "file") {
    return (
      <button
        onClick={() => onFileSelect(node.path)}
        className={cn(
          "w-full flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded-md transition-colors text-left",
          isSelected && "bg-accent"
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
      >
        <File className="w-4 h-4 text-muted-foreground flex-shrink-0" />
        <span
          className={cn(
            "font-mono text-xs truncate",
            isSelected && "font-semibold"
          )}
        >
          {node.name}
        </span>
      </button>
    );
  }

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-1 px-2 py-1.5 text-sm hover:bg-accent rounded-md transition-colors text-left"
        style={{ paddingLeft: `${level * 12 + 8}px` }}
      >
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-muted-foreground flex-shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
        )}
        {isOpen ? (
          <FolderOpen className="w-4 h-4 text-blue-500 flex-shrink-0" />
        ) : (
          <Folder className="w-4 h-4 text-blue-500 flex-shrink-0" />
        )}
        <span className="font-mono text-xs font-medium truncate">
          {node.name}
        </span>
      </button>
      {isOpen && node.children && (
        <div>
          {node.children.map((child, index) => (
            <FileTreeNode
              key={`${child.path}-${index}`}
              node={child}
              level={level + 1}
              selectedFile={selectedFile}
              onFileSelect={onFileSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FileTree({ files, selectedFile, onFileSelect }: FileTreeProps) {
  const fileTree = buildFileTree(files);

  return (
    <div className="h-full flex flex-col bg-muted/30 border-r">
      {/* Header */}
      <div className="p-3 border-b bg-background">
        <h3 className="text-sm font-semibold">Files</h3>
        <p className="text-xs text-muted-foreground mt-0.5">
          {files.length} {files.length === 1 ? "file" : "files"}
        </p>
      </div>

      {/* File Tree */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-0.5">
          {fileTree.map((node, index) => (
            <FileTreeNode
              key={`${node.path}-${index}`}
              node={node}
              selectedFile={selectedFile}
              onFileSelect={onFileSelect}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
