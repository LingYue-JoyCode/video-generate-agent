import React, { useEffect, useState } from "react";

// 工具函数：扁平化 mockdata
function flattenFiles(data: any) {
  const result: any[] = [];
  function walk(node: any) {
    if (node.type === "file") {
      result.push(node);
    } else if (node.children) {
      node.children.forEach(walk);
    }
  }
  walk(data);
  return result.sort((a, b) => (a.mtime > b.mtime ? 1 : -1));
}

export default RightPanel = ({ data }: { data: any }) => {
  const allFiles = flattenFiles(data);
  const [visibleCount, setVisibleCount] = useState(1);

  useEffect(() => {
    if (visibleCount < allFiles.length) {
      const timer = setTimeout(() => setVisibleCount(visibleCount + 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [visibleCount, allFiles.length]);

  return (
    <div className="w-full px-4 py-6 space-y-4">
      {allFiles.slice(0, visibleCount).map((file, idx) => (
        <div
          key={file.path}
          className="rounded-lg shadow bg-white p-4 flex items-center gap-4"
        >
          {/* 图片 */}
          {file.ext === ".png" && (
            <img
              src={`/mock/${file.path}`}
              alt={file.name}
              className="w-32 h-20 object-cover rounded"
            />
          )}
          {/* 音频 */}
          {file.ext === ".mp3" && (
            <audio controls src={`/mock/${file.path}`} className="w-48" />
          )}
          {/* 视频 */}
          {file.ext === ".mp4" && (
            <video
              controls
              src={`/mock/${file.path}`}
              className="w-48 rounded"
            />
          )}
          {/* 文本/脚本/字幕 */}
          {[".txt", ".srt", ".json"].includes(file.ext) && (
            <div className="flex-1">
              <div className="font-semibold text-blue-600">{file.name}</div>
              <div className="text-xs text-gray-400">{file.ext}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};