from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from mcp_servers import web_search_tools


@dataclass
class NovelAgentDeps:
    # 根据用户输入提取基线
    baseline: str
    # 字数限制
    word_limit: int


novel_agent = Agent(
    model=chat_model,
    deps_type=NovelAgentDeps,
    toolsets=[web_search_tools],
    output_type=str,
)


@novel_agent.instructions
def novel_agent_instructions(context: RunContext[NovelAgentDeps]) -> str:
    baseline = context.deps.baseline
    word_limit = context.deps.word_limit
    return f"""你是一个专业小说作者。根据以下基线创作小说文案，要求尽可能具体、生动、有情感张力，并提供结构化输出以便编辑和扩展。

基线：{baseline}
字数要求：{word_limit}

# Background：
- 作为一名短篇小说专家，你能准确的理解用户提供的小说主题，并根据主题和要求创作小说内容

# Skills：
- 信息查询能力：在你开始编写之前，你可以通过调用工具获取优质的写作资源。
- 主题理解能力：能够准确理解主题的核心思想和要求，确保小说内容与主题紧密相关。
- 角色塑造能力：根据主题需要，创造出有深度、有个性的角色，使他们的行为和情感符合主题设定。
- 扎实的文学功底：掌握基本的文学理论，如叙事结构、人物塑造、情节设计等。
- 流畅的文笔：能够用简洁、生动的语言描述复杂的情感和场景，吸引读者的阅读兴趣。
- 逻辑推理能力：确保故事情节的逻辑性和连贯性，避免出现不合理的情节跳跃或矛盾。

# Constraints：
- 禁止出现小说章节之间不连贯
- 禁止出现矛盾的情节

现在请使用中文进行小说编写。仅需要编写正文，不要包含其他内容。
"""


# 测试agent
if __name__ == "__main__":
    import asyncio

    async def main():
        async with novel_agent:
            res = await novel_agent.run(
                user_prompt="请写一个关于人工智能的短篇小说，字数在1000字以内。",
                deps=NovelAgentDeps(
                    baseline="请写一个关于人工智能的短篇小说，字数在1000字以内。",
                    word_limit=1000,
                ),
            )
        print(res.output)

    asyncio.run(main())
