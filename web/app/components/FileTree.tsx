"use client";

import React, { useState } from "react";
import { ChevronRightIcon, ChevronDownIcon } from "@heroicons/react/24/outline";
import {
  FolderIcon,
  DocumentIcon,
  MusicalNoteIcon,
  PhotoIcon,
  VideoCameraIcon,
  CodeBracketIcon,
} from "@heroicons/react/24/solid";

interface FileNode {
  name: string;
  type: "file" | "directory";
  path: string;
  children?: FileNode[];
  size?: number;
  mtime?: string;
  ext?: string;
}

interface FileTreeProps {
  data: FileNode;
  onFileSelect?: (file: FileNode) => void;
}

const getFileIcon = (ext: string) => {
  switch (ext) {
    case ".mp3":
    case ".wav":
      return <MusicalNoteIcon className="w-4 h-4 text-blue-500" />;
    case ".png":
    case ".jpg":
    case ".jpeg":
      return <PhotoIcon className="w-4 h-4 text-green-500" />;
    case ".mp4":
    case ".avi":
      return <VideoCameraIcon className="w-4 h-4 text-purple-500" />;
    case ".json":
      return <CodeBracketIcon className="w-4 h-4 text-yellow-500" />;
    case ".txt":
    case ".srt":
      return <DocumentIcon className="w-4 h-4 text-gray-500" />;
    default:
      return <DocumentIcon className="w-4 h-4 text-gray-500" />;
  }
};

const formatFileSize = (bytes?: number) => {
  if (!bytes) return "";
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

const TreeNode: React.FC<{
  node: FileNode;
  depth: number;
  onFileSelect?: (file: FileNode) => void;
}> = ({ node, depth, onFileSelect }) => {
  const [isExpanded, setIsExpanded] = useState(depth === 0);

  const handleToggle = () => {
    if (node.type === "directory") {
      setIsExpanded(!isExpanded);
    } else {
      onFileSelect?.(node);
    }
  };

  return (
    <div>
      <div
        className={`flex items-center py-1 px-2 hover:bg-gray-100 cursor-pointer rounded-md transition-colors duration-150 ${
          node.type === "file" ? "hover:bg-blue-50" : ""
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={handleToggle}
      >
        {node.type === "directory" && (
          <div className="w-4 h-4 mr-1 flex items-center justify-center">
            {isExpanded ? (
              <ChevronDownIcon className="w-3 h-3 text-gray-500" />
            ) : (
              <ChevronRightIcon className="w-3 h-3 text-gray-500" />
            )}
          </div>
        )}
        
        <div className="flex items-center mr-2">
          {node.type === "directory" ? (
            <FolderIcon className="w-4 h-4 text-blue-600" />
          ) : (
            getFileIcon(node.ext || "")
          )}
        </div>
        
        <span className="flex-1 text-sm text-gray-700 truncate">
          {node.name}
        </span>
        
        {node.type === "file" && node.size && (
          <span className="text-xs text-gray-400 ml-2">
            {formatFileSize(node.size)}
          </span>
        )}
      </div>
      
      {node.type === "directory" && isExpanded && node.children && (
        <div>
          {node.children.map((child, index) => (
            <TreeNode
              key={`${child.path}-${index}`}
              node={child}
              depth={depth + 1}
              onFileSelect={onFileSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const FileTree: React.FC<FileTreeProps> = ({ data, onFileSelect }) => {
  return (
    <div className="w-full h-full overflow-y-auto">
      <TreeNode node={data} depth={0} onFileSelect={onFileSelect} />
    </div>
  );
};
