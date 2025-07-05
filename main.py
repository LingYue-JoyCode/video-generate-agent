# 导入日志监控库logfire
import logfire
import asyncio
import dotenv
import os
from pathlib import Path

# 导入主控制器
from agents.scene_agent import scene_agent, SceneAgentDeps
from utils.novel import read_novel_content

dotenv.load_dotenv('.env')

MODE = os.getenv("MODE")

if MODE == "dev":
    # 配置logfire日志监控
    logfire.configure()
    # 对pydantic_ai进行监控
    logfire.instrument_pydantic_ai()


# 创建cache
cache_dir = Path(".cache")
cache_dir.mkdir(exist_ok=True)

os.makedirs('output/images', exist_ok=True)
os.makedirs('output/audio', exist_ok=True)

async def main():
    """
    主函数 - AI视频生成系统入口
    """
    print("🎬 欢迎使用AI视频生成系统!")
    print("=" * 50)

    # 配置生成参数
    novel_file_path = "assets/novel/index.txt"  # 设置为你的小说文件路径
    chunk_size = 500      # 每次读取字符数
    overlap_sentences = 1 # 重叠句子数

    print("🎯 生成设置:")
    print(f"   小说源文件: {novel_file_path}")
    print(f"   读取块大小: {chunk_size}字符")
    print(f"   重叠句子数: {overlap_sentences}")
    print("=" * 50)

    result = read_novel_content(novel_file_path, chunk_size)

    # 等待 scene_agent 执行完成后再进入下一轮
    await scene_agent.run("请生成分镜脚本", deps=SceneAgentDeps(novel_content=result.content))

    # while True:
    #     result = read_novel_content(novel_file_path, chunk_size)

    #     # 等待 scene_agent 执行完成后再进入下一轮
    #     await scene_agent.run("请生成分镜脚本", deps=SceneAgentDeps(novel_content=result.content))

    #     if not result.continue_read:
    #         break

if __name__ == "__main__":
    asyncio.run(main())
