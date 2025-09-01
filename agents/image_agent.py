from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from utils.comfyui import generate_image


@dataclass
class ImageAgentDeps:
    script: str = ""
    character_settings: str = ""
    scene_id: int = 0


image_agent = Agent(model=chat_model, deps_type=ImageAgentDeps, output_type=str)


@image_agent.instructions
def generate_sd_prompt(ctx: RunContext[ImageAgentDeps]) -> str:
    """生成分镜脚本和对应的图片"""

    script = ctx.deps.script
    character_settings = ctx.deps.character_settings
    return f"""
Please generate a Stable Diffusion (SD) image prompt based on the following information:
Scene Script: {script}
Character Settings: {character_settings}

Prompt Writing Guidelines:
1. Write in English. Prompts must be in English, as the CLIP model is trained on English datasets.
2. Use concise phrases, separated by English commas, instead of full sentences.
3. Place the most important phrases at the beginning of the prompt for higher weight.
4. You may explicitly set weights using parentheses, e.g., (phrase:1.5). Typical weights range from 0.5 to 1.5.

Notes:
1. Select one character from the Character Settings, use their description as-is, and incorporate it into the prompt without modification.
2. After the task description, add a description of the character's action and expression, e.g., "sitting on a chair".
3. Include a description of the scene, e.g., "school, classroom".
4. Make the prompt as detailed and vivid as possible, focusing on visual elements.

example:
<PUT THE CHARACTER SETTINGS HERE>, angry, sitting on a chair, school, classroom, detailed background, high resolution

After generating the prompt, call the generate_image_by_comfyui tool to generate the corresponding image.
"""

@image_agent.tool
def generate_image_by_comfyui(ctx: RunContext[ImageAgentDeps], sd_prompt: str) -> str:
    """生成分镜脚本和对应的图片"""
    scene_id = ctx.deps.scene_id

    # cache sd_prompt
    with open(f"output/sd_prompt_scene_{scene_id}.txt", "w", encoding="utf-8") as f:
        f.write(sd_prompt)

    # Call the image generation API or function here
    generate_image(prompt_text=sd_prompt, save_path=f"output/images/scene_{scene_id}.png")

    return "success"
