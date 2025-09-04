import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const filePath = params.path.join("/");
    const projectRoot = process.cwd();
    const fullPath = path.join(projectRoot, "..", "output", filePath);
    
    // 检查文件是否存在
    if (!fs.existsSync(fullPath)) {
      return new NextResponse("File not found", { status: 404 });
    }
    
    // 检查是否在允许的目录内
    const realPath = fs.realpathSync(fullPath);
    const allowedDir = fs.realpathSync(path.join(projectRoot, "..", "output"));
    
    if (!realPath.startsWith(allowedDir)) {
      return new NextResponse("Access denied", { status: 403 });
    }
    
    // 只允许读取文本文件
    const ext = path.extname(fullPath).toLowerCase();
    if (![".txt", ".json", ".srt"].includes(ext)) {
      return new NextResponse("File type not supported for content view", { status: 400 });
    }
    
    const content = fs.readFileSync(fullPath, "utf-8");
    
    return new NextResponse(content, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  } catch (error) {
    console.error("Error reading file content:", error);
    return new NextResponse("Internal server error", { status: 500 });
  }
}
