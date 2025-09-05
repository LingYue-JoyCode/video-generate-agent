"use client";

import React from "react";

interface FileNode {
  name: string;
  type: "file" | "directory";
  path: string;
  size?: number;
  mtime?: string;
  ext?: string;
}

interface FilePreviewProps {
  file: FileNode | null;
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return "";
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

const formatDate = (dateString?: string) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleString();
};

export const FilePreview: React.FC<FilePreviewProps> = ({ file }) => {
  if (!file) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <div className="text-4xl mb-4">📁</div>
          <p>选择一个文件来预览</p>
        </div>
      </div>
    );
  }

  const renderPreview = () => {
    switch (file.ext) {
      case ".png":
      case ".jpg":
      case ".jpeg":
        return (
          <div className="w-full">
            <img
              src={`/api/files/${file.path}`}
              alt={file.name}
              className="max-w-full max-h-96 object-contain rounded-lg shadow-md"
              onError={(e) => {
                // 如果API路径不存在，尝试使用mock路径
                (e.target as HTMLImageElement).src = `/mock/${file.path}`;
              }}
            />
          </div>
        );
      
      case ".mp3":
      case ".wav":
        return (
          <div className="w-full">
            <audio 
              controls 
              className="w-full"
              src={`/api/files/${file.path}`}
              onError={(e) => {
                // 如果API路径不存在，尝试使用mock路径
                (e.target as HTMLAudioElement).src = `/mock/${file.path}`;
              }}
            >
              您的浏览器不支持音频播放
            </audio>
          </div>
        );
      
      case ".mp4":
      case ".avi":
        return (
          <div className="w-full">
            <video 
              controls 
              className="max-w-full max-h-96 rounded-lg shadow-md"
              src={`/api/files/${file.path}`}
              onError={(e) => {
                // 如果API路径不存在，尝试使用mock路径
                (e.target as HTMLVideoElement).src = `/mock/${file.path}`;
              }}
            >
              您的浏览器不支持视频播放
            </video>
          </div>
        );
      
      case ".txt":
      case ".srt":
      case ".json":
        return (
          <div className="w-full">
            <div className="bg-gray-100 p-4 rounded-lg">
              <FileContentViewer filePath={file.path} />
            </div>
          </div>
        );
      
      default:
        return (
          <div className="text-center text-gray-500">
            <div className="text-4xl mb-4">📄</div>
            <p>暂不支持预览此文件类型</p>
          </div>
        );
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* 文件信息头部 */}
      <div className="border-b border-gray-200 p-4 bg-white">
        <h3 className="font-semibold text-lg text-gray-800 mb-2">{file.name}</h3>
        <div className="text-sm text-gray-600 space-y-1">
          <div>类型: {file.ext || "未知"}</div>
          {file.size && <div>大小: {formatFileSize(file.size)}</div>}
          {file.mtime && <div>修改时间: {formatDate(file.mtime)}</div>}
        </div>
      </div>
      
      {/* 文件预览内容 */}
      <div className="flex-1 p-4 overflow-auto bg-gray-50">
        {renderPreview()}
      </div>
    </div>
  );
};

// 文件内容查看器组件
const FileContentViewer: React.FC<{ filePath: string }> = ({ filePath }) => {
  const [content, setContent] = React.useState<string>("");
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    setLoading(true);
    fetch(`/api/files/content/${filePath}`)
      .then(res => res.text())
      .then(text => setContent(text))
      .catch(() => setContent("无法加载文件内容"))
      .finally(() => setLoading(false));
  }, [filePath]);

  if (loading) {
    return <div className="text-center">加载中...</div>;
  }

  return (
    <pre className="whitespace-pre-wrap text-sm font-mono max-h-96 overflow-auto">
      {content}
    </pre>
  );
};
