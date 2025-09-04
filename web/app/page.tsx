"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgentStateRender, useCoAgent } from "@copilotkit/react-core";
import React, { useRef, useState, useEffect } from "react";
// import { mockdata } from "./mock";

type AgentState = {
  message: string;
};
// 工具函数：扁平化所有文件
function flattenFiles(data: any) {
  const result: any[] = [];
  function walk(node: any) {
    if (node.type === "file") {
      result.push(node);
    } else if (node.children && Array.isArray(node.children)) {
      node.children.forEach(walk);
    }
  }
  walk(data);
  // 按 mtime 排序
  return result.sort((a, b) => (a.mtime > b.mtime ? 1 : -1));
}

export default function App() {
  const [expanded, setExpanded] = useState(false);
  const [leftWidth, setLeftWidth] = useState(350);
  const [rightFileList, setRightFileList] = useState({});
  const lastFetchRef = useRef<number>(0);

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

      fetchTaskList();
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

  const fetchTaskList = async () => {
    const now = Date.now();
    if (now - lastFetchRef.current < 10 * 1000) {
      // 距离上次请求不足5秒，直接返回
      return;
    }
    lastFetchRef.current = now;
    try {
      const response = await fetch("http://10.195.171.23:8000/api/output-tree");
      const result = await response.json();
      setRightFileList(result);
      if (!expanded) setExpanded(true);
    } catch (err) {
      console.error(err);
    }
  };

  const coAgent = useCoAgent({
    name: "main_agent",
  });

  const FileNode = ({ node }: { node: any }) => {
    const [open, setOpen] = useState(true);

    if (node.type === "directory") {
      return (
        <div className="mb-2">
          <div
            className="flex items-center cursor-pointer select-none font-semibold text-indigo-700"
            onClick={() => setOpen((v) => !v)}
          >
            <span className="mr-2">{open ? "▼" : "▶"}</span>
            <span>{node.name}</span>
          </div>
          {open && (
            <div className="ml-6 border-l border-gray-200 pl-4">
              {node.children?.map((child: any) => (
                <FileNode key={child.path || child.name} node={child} />
              ))}
            </div>
          )}
        </div>
      );
    }

    // 文件类型展示
    return (
      <div className="my-2 p-3 rounded-lg shadow bg-white flex items-center gap-4 relative">
        {/* 图片 */}
        {node.ext === ".png" && (
          <img
            src={`/mock/${node.path}`}
            alt={node.name}
            className="w-24 h-16 object-cover rounded"
          />
        )}
        {/* 音频 */}
        {node.ext === ".mp3" && (
          <audio controls src={`/mock/${node.path}`} className="w-40" />
        )}
        {/* 视频 */}
        {node.ext === ".mp4" && (
          <video controls src={`/mock/${node.path}`} className="w-40 rounded" />
        )}
        {/* 文本/脚本/字幕 */}
        {[".txt", ".srt", ".json"].includes(node.ext) && (
          <div className="flex-1">
            <div className="font-semibold text-blue-600">{node.name}</div>
            <div className="text-xs text-gray-400">{node.ext}</div>
          </div>
        )}

        <div className="absolute top-4 right-6 z-30">
          <button
            className="p-2 cursor-pointer rounded-full bg-gray-200 hover:bg-gray-300 shadow transition"
            onClick={() => {
              // TODO: 替换为你的下载逻辑
              alert("下载功能待实现");
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4"
              />
            </svg>
          </button>
        </div>
      </div>
    );
  };

  const RightPanel = ({ data }: { data: any }) => (
    <div className="w-full px-4 py-6">
      {Array.isArray(data?.children) &&
        data.children.map((folder: any) => (
          <FileNode key={folder.path || folder.name} node={folder} />
        ))}
    </div>
  );

  return (
    <div className="relative w-full h-screen bg-gray-50">
      {/* 展开/收起按钮 */}
      {/* <button
        className="absolute top-4 right-4 z-20 px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition"
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? "收起为全屏" : "展开为左右结构"}
      </button> */}
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
              <RightPanel data={rightFileList} />
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
