from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model

@dataclass
class CharacterAgentDeps:
    novel_content: str = ""

character_agent = Agent(
    model=chat_model,
    deps_type=CharacterAgentDeps,
    output_type=str
)

@character_agent.instructions
def generate_sd_prompt(ctx: RunContext[CharacterAgentDeps]) -> str:
    """生成分镜脚本和对应的图片"""
    novel_content = ctx.deps.novel_content
    return f"""
You are a professional illustrator. Your task is to extract all character profiles from the provided text and generate detailed SD (Stable Diffusion) prompts for each character.

Here is the original novel excerpt:
{novel_content}

Prompt writing guidelines:
1. Write in English - Prompts must be in English, as the CLIP model is trained on English datasets.
2. Use phrases - Use concise phrases instead of full sentences, separated by English commas for easy management and weight adjustment.
3. Weight management - The importance of each phrase is determined by its position in the prompt; phrases at the beginning have higher weight and are more likely to appear in the generated image.
4. Weight expression - You can explicitly set weights using parentheses, e.g., (phrase:1.5) means the phrase has 1.5x normal weight. Typical weights range from 0.5 to 1.5.
5. For young female characters, always include: alisa mikhailovna kujou (roshidere)
6. For young male characters, always include: masachika kuze, short hair

Each character's prompt must include:
1. Gender: Use one of "a man", "a woman", "a boy", "a girl"
2. Age group (e.g., 20s, 30s, teenager, child)
3. Distinctive appearance: e.g., hair color and style, eye color, body type, clothing, accessories, facial expression, and any unique features
4. Clothing: e.g., casual wear, formal attire, armor, etc.
5. Describe each character as detailed as possible in English, including all visible features, accessories, and any unique traits.

Example output:
```json
[
    {{
    "name": "张三", (original character name, do not translate to English)
    "character_setting": "a man, 30s, masachika kuze, short hair, brown hair, hair between eyes, brown eyes, short hair, black hair, brown eyes, athletic build, wearing a suit, confident expression"
    }},
    {{
    "name": "翠花", (original character name, do not translate to English)
    "character_setting": "a girl, 20s, alisa mikhailovna kujou (roshidere), long white hair, black eyes, slender build, floral dress, gentle smile"
    }}
]
```

Please generate detailed SD prompts for the main characters based on the novel excerpt above.
"""
