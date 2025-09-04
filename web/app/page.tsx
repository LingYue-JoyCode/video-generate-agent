"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgentStateRender } from "@copilotkit/react-core";
import React, { useRef, useState, useEffect } from "react";
import { mockdata } from "./mock";

type AgentState = {
  message: string;
};

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

const RightPanel = ({ data }: { data: any }) => {
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

export default function App() {
  const [expanded, setExpanded] = useState(false);
  const [leftWidth, setLeftWidth] = useState(350);
  const dragging = useRef(false);

  // 拖拽事件
  const handleMouseDown = () => {
    dragging.current = true;
    document.body.style.cursor = "col-resize";
  };
  const handleMouseUp = () => {
    dragging.current = false;
    document.body.style.cursor = "";
  };
  const handleMouseMove = (e: MouseEvent) => {
    if (dragging.current) {
      const min = 220,
        max = 600;
      setLeftWidth(Math.max(min, Math.min(max, e.clientX)));
    }
  };
  React.useEffect(() => {
    if (expanded) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      return () => {
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }
  });

  // CopilotKit 状态渲染
  const leftContent = useCoAgentStateRender<AgentState>({
    name: "main_agent",
    render: ({ state }) => {
      if (!state.message) return null;
      return (
        <div
          className="mt-3 w-full max-w-xs rounded-lg border border-gray-200 bg-white/70 shadow-sm backdrop-blur-sm dark:border-zinc-700 dark:bg-zinc-900/60"
          aria-live="polite"
        >
          <div className="flex items-start gap-3 p-3">
            <span
              className="mt-1 h-2 w-2 animate-pulse rounded-full bg-emerald-500"
              aria-hidden
            />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium uppercase tracking-wide text-gray-600 dark:text-gray-300">
                  LLM Planing
                </span>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300 dark:ring-emerald-800">
                  active
                </span>
              </div>
              <details className="group mt-1">
                <summary className="flex cursor-pointer list-none select-none items-center gap-1 text-sm text-gray-800 transition-colors hover:text-gray-900 dark:text-gray-100 dark:hover:text-white">
                  <span
                    className="inline-block max-w-full truncate align-bottom"
                    title={state.message}
                  >
                    {state.message}
                  </span>
                  <span className="ml-1 text-xs text-blue-600 group-open:hidden hover:underline">
                    展开
                  </span>
                  <span className="ml-1 hidden text-xs text-blue-600 group-open:inline hover:underline">
                    收起
                  </span>
                </summary>
                <div className="mt-2 max-h-48 overflow-y-auto rounded-md border border-gray-100 bg-gray-50 p-3 text-sm text-gray-700 dark:border-zinc-700 dark:bg-zinc-800 dark:text-gray-200">
                  {state.message}
                </div>
              </details>
            </div>
          </div>
        </div>
      );
    },
  });

  const RightPanel = ({ data }: { data: any }) => {
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
            className="rounded-lg shadow bg-white p-4 flex items-center gap-4 relative"
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
            <div className="absolute top-0.5 right-0.5">
              <button className="p-2 rounded-full bg-gray-200 hover:bg-gray-300">
                <svg
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  x="0px"
                  y="0px"
                  viewBox="0 0 512 512"
                  enable-background="new 0 0 512 512"
                  className="h-4 w-4"
                >
                  <path
                    d="M416,199.5h-91.4V64H187.4v135.5H96l160,158.1L416,199.5z M96,402.8V448h320v-45.2H96z"
                    fill="currentColor"
                  />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="relative w-full h-screen bg-gray-50">
      {/* 展开/收起按钮 */}
      <button
        className="absolute top-4 right-4 z-20 px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition"
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? "收起为全屏" : "展开为左右结构"}
      </button>
      {/* 全屏模式 */}
      {!expanded && (
        <main className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-200 via-white to-indigo-200">
          {/* 优化后的描述区 */}

          {/* 聊天窗口 */}
          <CopilotChat
            className="h-[80vh] w-[80vw] rounded-xl shadow-2xl border border-indigo-100" // 去掉 bg-white
          ></CopilotChat>
          {/* <CopilotChat className="h-[80vh] w-[80vw] rounded-xl shadow-2xl border border-indigo-100" /> */}
        </main>
      )}
      {/* 左右结构模式 */}
      {expanded && (
        <div className="flex h-full">
          {/* 左侧：完整聊天窗口 */}
          <aside
            className="flex-1 flex items-center justify-center bg-gradient-to-br transition-all duration-500
            from-blue-200 via-white to-indigo-200
            "
            style={{ minWidth: 320 }}
          >
            <CopilotChat className="h-[80vh] w-full max-w-2xl rounded-lg shadow-lg bg-white" />
          </aside>
          {/* 拖拽条 */}
          <div
            className="w-2 cursor-col-resize bg-blue-100 hover:bg-blue-300 transition"
            onMouseDown={handleMouseDown}
            style={{ zIndex: 10 }}
          />
          {/* 右侧：聊天摘要，带过渡动画 */}
          <section
            className="bg-white border-l flex flex-col items-center pt-8 transition-all duration-500 ease-in-out
            overflow-y-auto
            "
            style={{
              width: leftWidth,
              minWidth: 220,
              maxWidth: 600,
              opacity: expanded ? 1 : 0,
              transform: expanded ? "translateX(0)" : "translateX(40px)",
            }}
          >
            <div className="text-lg font-bold text-blue-600 mb-4"></div>
            <div className="w-full px-4">
              <RightPanel data={mockdata} />
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
