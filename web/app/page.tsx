"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useCopilotAction } from "@copilotkit/react-core";

export default function App() {
  useCopilotAction({
    name: "get_weather",
    available: "frontend", // Mark this as render only
    render: ({ status, args }) => {
      return (
        <p className="text-gray-500 mt-2">
          {status !== "complete" && "Calling weather API..."}
          {status === "complete" &&
            `Called the weather API for ${args.location}.`}
        </p>
      );
    },
  });
  return (
    <main>
      <h1>Your main content</h1>

      <CopilotSidebar
        labels={{
          title: "Popup Assistant",
          initial: "Hi! I'm connected to an agent. How can I help?",
        }}
      />
    </main>
  );
}
