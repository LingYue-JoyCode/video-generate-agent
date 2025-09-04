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
    
    const content = fs.readFileSync(fullPath);
    const ext = path.extname(fullPath).toLowerCase();
    
    // 设置适当的 Content-Type
    let contentType = "application/octet-stream";
    switch (ext) {
      case ".png":
        contentType = "image/png";
        break;
      case ".jpg":
      case ".jpeg":
        contentType = "image/jpeg";
        break;
      case ".mp3":
        contentType = "audio/mpeg";
        break;
      case ".mp4":
        contentType = "video/mp4";
        break;
      case ".txt":
        contentType = "text/plain";
        break;
      case ".json":
        contentType = "application/json";
        break;
      case ".srt":
        contentType = "text/plain";
        break;
    }
    
    return new NextResponse(content, {
      headers: {
        "Content-Type": contentType,
      },
    });
  } catch (error) {
    console.error("Error serving file:", error);
    return new NextResponse("Internal server error", { status: 500 });
  }
}
