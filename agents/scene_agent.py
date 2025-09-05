import json
from pydantic_ai import Agent, RunContext
from agents.image_agent import ImageAgentDeps, image_agent
from utils.llm import chat_model
from ag_ui.core import EventType, StateSnapshotEvent

scene_agent = Agent(model=chat_model, output_type=list[str])


@scene_agent.instructions
def generate_scenes_and_images(ctx: RunContext) -> str:
    """生成分镜脚本和对应的图片"""

    with open("output/novel_content.txt", "r", encoding="utf-8") as f:
        novel_content = f.read()

    return f"""
你是一位专业且严谨的分镜师，负责将小说内容拆分为适合拍摄的视频分镜。下面给出小说原文，请基于原文严格拆分分镜片段，输出格式和约束都必须遵守。

小说原文如下：
{novel_content}

请严格遵守以下规则并仅输出最终结果（不要任何解释或额外文本）：

1) 输出格式：直接返回一个合法的 JSON 数组，数组元素为字符串。例如：["第一段原文...", "第二段原文..."]
2) 数量限制：分镜数量不超过 10 个。
3) 原文一致性：每个分镜必须是小说原文中的连续片段（不可改写、不可概括、不可补充），字符必须与原文完全一致（保留标点与换行）。
4) 顺序与重叠：分镜顺序必须与原文顺序一致，片段之间不得重叠；可以不覆盖全书，但不得改变原文顺序。
5) 长度建议：建议每段控制在约 50–300 字之间（根据情节密度可适当调整），但不要人为拆分导致句义中断。
6) 清理细节：每个数组元素应去除首尾多余空白，但内部应保留原文换行与空格。
7) 严格输出：不要包含解释、标题、编号、注释或多余字符；不要使用 Markdown 或代码块包装。

最后需要调用generate_scenes工具进行场景的生成。
"""


@scene_agent.tool_plain
async def generate_scenes(scripts: list[str]) -> StateSnapshotEvent:
    with open("output/character_settings.json", "r", encoding="utf-8") as f:
        character_settings = f.read()

    scene = []
    for item in scripts:
        result = await image_agent.run(
            "请生成分镜图像",
            deps=ImageAgentDeps(script=item, character_settings=character_settings),
        )
        sd_prompt = result.output
        scene.append({"script": item, "sd_prompt": sd_prompt})

    with open("output/scenes.json", "w", encoding="utf-8") as f:
        json.dump(scene, f, ensure_ascii=False, indent=4)

    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"message": "分镜生成完成"},
    )


if __name__ == "__main__":
    import asyncio

    async def main():
        async with scene_agent:
            res = await scene_agent.run(
                user_prompt="请帮我生成合适的分镜",
            )
        print(res.output)

    asyncio.run(main())
