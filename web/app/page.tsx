"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgentStateRender } from "@copilotkit/react-core";
import React, { useRef, useState } from "react";

type AgentState = {
  message: string;
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
      const min = 220, max = 600;
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
            <span className="mt-1 h-2 w-2 animate-pulse rounded-full bg-emerald-500" aria-hidden />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium uppercase tracking-wide text-gray-600 dark:text-gray-300">LLM Planing</span>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300 dark:ring-emerald-800">active</span>
              </div>
              <details className="group mt-1">
                <summary className="flex cursor-pointer list-none select-none items-center gap-1 text-sm text-gray-800 transition-colors hover:text-gray-900 dark:text-gray-100 dark:hover:text-white">
                  <span className="inline-block max-w-full truncate align-bottom" title={state.message}>
                    {state.message}
                  </span>
                  <span className="ml-1 text-xs text-blue-600 group-open:hidden hover:underline">展开</span>
                  <span className="ml-1 hidden text-xs text-blue-600 group-open:inline hover:underline">收起</span>
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
        <main className="w-full h-full flex items-center justify-center bg-white">
          <CopilotChat className="h-[100vh] w-[90vw] rounded-lg shadow-lg bg-white" />
        </main>
      )}
      {/* 左右结构模式 */}
      {expanded && (
  <div className="flex h-full">
    {/* 左侧：完整聊天窗口 */}
    <aside
      className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-50 to-white transition-all duration-500"
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
      className="bg-white border-l flex flex-col items-center pt-8 transition-all duration-500 ease-in-out"
      style={{
        width: leftWidth,
        minWidth: 220,
        maxWidth: 600,
        opacity: expanded ? 1 : 0,
        transform: expanded ? "translateX(0)" : "translateX(40px)",
      }}
    >
      <div className="text-lg font-bold text-blue-600 mb-4">聊天摘要</div>
      <div className="w-full px-4">{leftContent}</div>
    </section>
  </div>
)}
    </div>
  );
}
