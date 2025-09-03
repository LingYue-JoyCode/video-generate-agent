# 导入日志监控库logfire
import os
from pathlib import Path
from fastapi import FastAPI
import uvicorn

# 导入主控制器
from agents.main_agent import main_agent

app = FastAPI()

# 创建cache
cache_dir = Path(".cache")
cache_dir.mkdir(exist_ok=True)

os.makedirs("output/images", exist_ok=True)
os.makedirs("output/audio", exist_ok=True)

app.mount("/agent", main_agent.to_ag_ui())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
