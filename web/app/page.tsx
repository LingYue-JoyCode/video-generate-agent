"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCoAgentStateRender } from "@copilotkit/react-core";

type AgentState = {
  message: string;
  detail: string;
};

export default function App() {
  // Add a state renderer to observe predictions
  useCoAgentStateRender<AgentState>({
    name: "main_agent",
    render: ({ state }) => {
      if (!state.message) return null;
      return (
        <div
          className="mt-3 w-full max-w-3xl rounded-lg border border-gray-200 bg-white/70 shadow-sm backdrop-blur-sm dark:border-zinc-700 dark:bg-zinc-900/60"
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
                  {state.detail}
                </div>
              </details>
            </div>
          </div>
        </div>
      );
    },
  });
  return (
    <main className="w-full h-full">
      <CopilotChat className="h-screen w-screen" />
    </main>
  );
}
