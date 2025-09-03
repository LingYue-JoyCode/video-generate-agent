from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model

@dataclass
class CharacterAgentOutput:
    name: str
    character_setting: str

character_agent = Agent(model=chat_model, output_type=list[CharacterAgentOutput])

@character_agent.instructions
def generate_sd_prompt(ctx: RunContext) -> str:
    """为小说人物生成 Stable Diffusion 角色提示词（中文说明、英文提示词）。"""
    with open("output/novel_content.txt", "r", encoding="utf-8") as f:
        novel_content = f.read()
    return f"""
你是一名专业插画师。请从下方小说内容中抽取所有主要人物，并为每位角色生成用于 Stable Diffusion 的角色提示词（SD prompt）。

小说原文片段：
{novel_content}

产出要求（请严格遵守）：
1) 输出格式：仅输出 JSON 数组字符串，不要使用 Markdown 代码块，不要添加说明文字或多余字段。数组中每个元素必须包含字段："name"（中文原名，不要翻译）、"character_setting"（英文短语）。
2) 语言与形式：character_setting 只能使用英文短语，使用英文逗号分隔，不写完整句子；将重要短语放在前面以增加权重。
3) 权重表达：允许对关键短语使用括号权重，例如 (phrase:1.2)，常见范围 0.5–1.5。
4) 必含信息（按优先级从高到低组织）：
     - 性别标签：从 "a man" / "a woman" / "a boy" / "a girl" 中选择其一，并置于最前。
     - 年龄段：如 20s, 30s, teenager, child。
     - 外观细节：发色与发型、瞳色、肤色、脸型、体型、五官特征、表情、显著特征（疤痕、痣、雀斑等）。
     - 服饰与配件：服装风格（casual wear / formal attire / school uniform / armor / traditional 等）、材质、颜色、饰品、道具。
     - 其他必要描述：如果文本未明确，给出合理、常见且不与原文冲突的通用描述。
5) 去重与一致性：同名角色合并为一个条目，并根据文本整合其稳定且显著的形象要素。
"""

# 测试agent
if __name__ == "__main__":
    import asyncio

    async def main():
        async with character_agent:
            res = await character_agent.run(
                user_prompt="请按照要求生成角色设定。",
            )
        print(res.output)

    asyncio.run(main())
