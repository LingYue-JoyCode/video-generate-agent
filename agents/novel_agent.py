from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from utils.novel import read_novel_content
from pathlib import Path


@dataclass
class NovelAgentDeps:
    novel_file_path: str = ""  # 小说源文件路径
    chunk_size: int = 500      # 每次读取字符数，可配置


novel_agent = Agent(
    model=chat_model,
    deps_type=NovelAgentDeps,
)


@novel_agent.tool
def read_novel_chunk(ctx: RunContext[NovelAgentDeps]) -> str:
    """
    智能读取小说内容，自动检测编码并使用jieba进行句子分割
    """
    novel_file_path = ctx.deps.novel_file_path
    chunk_size = ctx.deps.chunk_size
    
    # 使用utils中的读取函数
    result = read_novel_content(novel_file_path, chunk_size)
    
    # 确保输出目录存在并写入内容
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if result:
        with open(output_dir / 'content.txt', 'a', encoding='utf-8') as f:
            f.write(result + '\n')
    
    return result


@novel_agent.instructions
def generate_content(ctx: RunContext[NovelAgentDeps]) -> str:
    """
    根据小说源文件生成内容
    """
    return """
你是一个小说内容处理助手，负责从小说文件中读取内容。

请调用 read_novel_chunk 工具来读取小说内容。
"""