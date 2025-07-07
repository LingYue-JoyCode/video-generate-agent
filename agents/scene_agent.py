from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from agents.image_agent import ImageAgentDeps, image_agent
from agents.character_agent import CharacterAgentDeps, character_agent
from utils.llm import chat_model
from agents.talk_agent import talk_agent, TalkAgentDeps

@dataclass
class SceneAgentDeps:
    novel_content: str = ""

scene_agent = Agent(
    model=chat_model,
    deps_type=SceneAgentDeps,
    output_type=list[str]
)

@scene_agent.instructions
def generate_scenes_and_images(ctx: RunContext[SceneAgentDeps]) -> str:
    """生成分镜脚本和对应的图片"""

    novel_content = ctx.deps.novel_content

    return f"""
你是一位专业的分镜师，负责将小说内容拆分为合适的视频分镜。

以下是小说的原文：
{novel_content}

请根据小说的原文进行分镜头的拆分。

你需要注意：
1. 你只需要根据小说的原文内容做分块，因此，每个分块的内容拼接在一起必须是小说的原文，不要做总结，不要做改编。
2. 分块的顺序必须与小说的原文顺序一致，不得随意调整。

在完成原文拆分后，你需要调用generate_image_audio工具。
"""

@scene_agent.tool
async def generate_image_audio(ctx: RunContext[SceneAgentDeps], scripts: list[str]) -> None:
    """生成场景音频"""
    novel_content = ctx.deps.novel_content
    # write novel content to cache
    with open("output/novel_content.txt", "w", encoding="utf-8") as f:
        f.write(novel_content)

    # 生成人物设定
    agent_res = await character_agent.run(
        user_prompt="Please generate character settings.",
        deps=CharacterAgentDeps(novel_content=novel_content)
    )

    character_settings = agent_res.output

    # write cache
    with open("output/character_settings.txt", "w", encoding="utf-8") as f:
        f.write(character_settings)
    
    for idx, script in enumerate(scripts):
        await image_agent.run(
            "请生成分镜图像", deps=ImageAgentDeps(script=script, character_settings=character_settings, scene_id=idx)
        )
        await talk_agent.run(
            "请生成场景音频和字幕", deps=TalkAgentDeps(novel_content=novel_content, script=script, scene_id=idx)
        )

    print("场景音频和图像生成完成")
