import "./globals.css";
import { ReactNode } from "react";
import { CopilotKit } from "@copilotkit/react-core";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="h-screen w-screen">
        {/* This points to the runtime we setup in the previous step */}
        <CopilotKit runtimeUrl="/api/copilotkit" agent="main_agent">
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
