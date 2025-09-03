import json
import os
from pydantic_ai import Agent, RunContext
from utils.comfyui import generate_image
from utils.edge_tts import generate_audio_for_script
from utils.llm import chat_model
from .character_agent import character_agent
from .novel_agent import novel_agent, NovelAgentDeps
from .scene_agent import scene_agent
from utils.video import generate_video
from ag_ui.core import EventType, StateSnapshotEvent
from pydantic import BaseModel
from pydantic_ai.ag_ui import StateDeps
from utils.config import system_prompt


class AgentState(BaseModel):
    """State for the agent."""

    message: str = ""


main_agent = Agent(model=chat_model, deps_type=StateDeps[AgentState])


@main_agent.instructions
def main_instructions(ctx: RunContext[StateDeps[AgentState]]) -> str:
    return f"""
你是一个短视频制作agent，你的主要任务是根据用户提供的小说基线进行小说的编写和短视频的生成。

你的工作流程如下：
1. 调用工具创建小说
2. 调用工具创建人物设定
3. 调用工具生成分镜场景
4. 调用工具生成图片
5. 调用工具生成音频和字幕
6. 调用工具生成最终视频

{system_prompt}
"""


@main_agent.tool_plain
async def novel_creation(baseline: str, word_limit: int = 1000) -> StateSnapshotEvent:
    result = await novel_agent.run(
        user_prompt="请根据要求编写小说。",
        deps=NovelAgentDeps(baseline=baseline, word_limit=word_limit),
    )
    # save novel
    novel_content = result.output
    with open("output/novel_content.txt", "w", encoding="utf-8") as f:
        f.write(novel_content)
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "小说内容已创建。"},
    )


@main_agent.tool_plain
async def send_current_plan(message: str, detail: str) -> StateSnapshotEvent:
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT, snapshot={"message": message, "detail": detail}
    )


@main_agent.tool_plain
async def generate_character_settings() -> StateSnapshotEvent:
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
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "角色设定已创建。"},
    )


@main_agent.tool_plain
async def generate_scenes() -> StateSnapshotEvent:
    await scene_agent.run(
        user_prompt="请根据要求生成场景。",
    )
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "场景已创建。"},
    )


@main_agent.tool_plain
async def generate_images() -> StateSnapshotEvent:
    with open("output/scenes.json", "r", encoding="utf-8") as f:
        scene = json.load(f)

    for idx, item in enumerate(scene):
        # 1) 生成分镜图像
        generate_image(
            prompt_text=item["sd_prompt"],
            save_path=f"output/images/scene_{idx}.png",
        )

    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "分镜图像已生成。"},
    )


@main_agent.tool_plain
async def generate_audios() -> StateSnapshotEvent:
    with open("output/scenes.json", "r", encoding="utf-8") as f:
        scene = json.load(f)

    for idx, item in enumerate(scene):
        # 2) 保存脚本文本
        script_path = f"output/scripts/scene_{idx}.txt"
        os.makedirs("output/scripts", exist_ok=True)
        with open(script_path, "w", encoding="utf-8") as sf:
            sf.write(item["script"])
        # 3) 生成音频与字幕
        audio_path = f"output/audio/scene_{idx}.mp3"
        srt_path = f"output/subtitles/scene_{idx}.srt"
        generate_audio_for_script(
            script_path=script_path, audio_path=audio_path, srt_path=srt_path
        )

    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "分镜配音已生成。"},
    )


@main_agent.tool_plain
async def generate_final_video() -> StateSnapshotEvent:
    generate_video()
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "最终视频已生成。"},
    )


# 测试agent
if __name__ == "__main__":
    import asyncio

    async def main():
        async with main_agent:
            res = await main_agent.run(
                user_prompt="请写一个关于人工智能的短篇小说，字数在1000字以内。",
                deps=StateDeps[AgentState](state=AgentState()),
            )
        print(res.output)

    asyncio.run(main())
