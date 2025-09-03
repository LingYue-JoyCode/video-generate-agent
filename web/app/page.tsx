"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCopilotAction } from "@copilotkit/react-core";

export default function App() {
  useCopilotAction({
    name: "get_weather",
    available: "frontend",
    render: ({ status, args }) => (
      <p className="text-gray-500 mt-2">
        {status !== "complete" && "Calling weather API..."}
        {status === "complete" && `Called the weather API for ${args.location}.`}
      </p>
    ),
  });

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col justify-between">
        <div>
          <div className="px-6 py-6 flex items-center border-b">
            <span className="text-xl font-bold text-blue-600">Video-Generate-Agent</span>
          </div>
          <nav className="mt-6 px-4">
            <ul>
              <li className="mb-2">
                <a
                  href="#"
                  className="block px-4 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium"
                >
                  新对话
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="block px-4 py-2 rounded text-gray-500 hover:bg-blue-50 hover:text-blue-600"
                >
                  历史会话
                </a>
              </li>
            </ul>
          </nav>
        </div>
        <div className="px-6 py-4 border-t text-xs text-gray-400">
          CopilotKit Chat © 2025
        </div>
      </aside>
      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-white">
        <div className="w-full max-w-2xl p-6">
          <CopilotChat
            labels={{
              title: "AI 助手",
              initial: "你好！👋 有什么可以帮您？",
            }}
            className="rounded-lg shadow-lg bg-white"
          />
        </div>
      </main>
    </div>
  );
}
