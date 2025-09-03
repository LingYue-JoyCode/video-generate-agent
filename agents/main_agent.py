import json
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from .character_agent import character_agent
from .novel_agent import novel_agent, NovelAgentDeps
from .scene_agent import scene_agent
from utils.video import generate_video

main_agent = Agent(
    model=chat_model,
)


@main_agent.instructions
def main_instructions(ctx: RunContext) -> str:
    return """
你是一个短视频制作agent，你的主要任务是根据用户提供的小说基线进行小说的编写和短视频的生成。

你的工作流程如下：
1. 调用工具创建小说
2. 调用工具创建人物设定
3. 调用工具生成分镜场景
4. 调用工具生成最终视频
"""


@main_agent.tool
async def novel_creation(ctx: RunContext, baseline: str, word_limit: int = 1000) -> str:
    result = await novel_agent.run(
        user_prompt="请根据要求编写小说。",
        deps=NovelAgentDeps(baseline=baseline, word_limit=word_limit),
    )
    # save novel
    novel_content = result.output
    with open("output/novel_content.txt", "w", encoding="utf-8") as f:
        f.write(novel_content)
    return "小说内容已保存。接下来请生成角色设定。"


@main_agent.tool
async def generate_character_settings(ctx: RunContext) -> str:
    result = await character_agent.run(
        user_prompt="请根据要求生成角色设定。",
    )
    # save character settings
    character_settings = []
    # format to dict
    for item in result.output:
        character_settings.append(
            {
                "name": item.name,
                "character_setting": item.character_setting,
            }
        )
    with open("output/character_settings.json", "w", encoding="utf-8") as f:
        json.dump(character_settings, f, ensure_ascii=False, indent=4)
    return "角色设定已生成。"


@main_agent.tool_plain
async def generate_scenes() -> str:
    result = await scene_agent.run(
        user_prompt="请根据要求生成场景。",
    )
    return "\n".join(result.output)


@main_agent.tool_plain
async def generate_final_video() -> str:
    return generate_video()


# 测试agent
if __name__ == "__main__":
    import asyncio

    async def main():
        async with main_agent:
            res = await main_agent.run(
                user_prompt="请写一个关于人工智能的短篇小说，字数在1000字以内。",
            )
        print(res.output)

    asyncio.run(main())
