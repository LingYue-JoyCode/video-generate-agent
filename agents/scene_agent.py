from dataclasses import dataclass
import asyncio
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from utils.scene import (
    read_content_file,
    save_scenes_scripts,
    batch_generate_images,
    clean_scenes_data,
)
from agents.talk_agent import talk_agent, TalkAgentDeps


@dataclass
class SceneAgentDeps:
    content_file: str = "output/content.txt"  # 小说内容文件路径


scene_agent = Agent(
    model=chat_model,
    deps_type=SceneAgentDeps,
)


@scene_agent.instructions
def generate_scenes_and_images(ctx: RunContext[SceneAgentDeps]) -> str:
    """生成分镜脚本和对应的图片"""
    return """
你是一位专业的分镜师，负责将小说内容转换为视频分镜脚本。

## 工作流程：
1. 调用 read_content 工具读取小说内容
2. 调用 generate_scenes 工具保存分镜脚本（必须严格按照JSON格式）
3. 调用 generate_images_and_audio 工具同时生成图片和音频

## 重要：generate_scenes工具的数据格式要求

调用generate_scenes时，scenes_data参数必须是包含以下字段的JSON数组：

```json
[
  {
    "scene_id": 1,
    "script": "当前image_prompt对应的原文片段，不要包含章节标题，例如：第xx章",
    "image_prompt": "stable diffusion提示词，用于生成分镜的图片",
  }
]
```

## Stable Diffusion 提示词编写指南

### 1. 基本语法规则
- **逗号分隔**：每个描述元素用逗号分隔，如：`girl, blue eyes, blonde hair`
- **权重控制**：使用括号调整权重
  - `(keyword)` = 1.1倍权重
  - `((keyword))` = 1.21倍权重
  - `(keyword:1.5)` = 1.5倍权重
  - `[keyword]` = 0.9倍权重（降低权重）

### 2. 提示词结构顺序（重要性递减）
1. **主体人物/角色**：性别、年龄、外貌特征
2. **服装/造型**：衣服、配饰、发型
3. **表情/情绪**：面部表情、情绪状态
4. **动作/姿势**：具体动作、身体姿态
5. **场景/环境**：地点、背景、时间
6. **画面质量**：画质、风格、构图
7. **技术参数**：光线、视角、特效

### 3. 人物描述最佳实践
**外貌特征**（保持角色一致性）：
- 性别：`man, woman, boy, girl, teenager, adult`
- 年龄：`young, middle-aged, elderly, child, teen`
- 眼睛：`blue eyes, brown eyes, green eyes, large eyes, sharp eyes`
- 发色：`blonde hair, black hair, brown hair, red hair, white hair`
- 发型：`long hair, short hair, curly hair, straight hair, ponytail`
- 肤色：`pale skin, tan skin, dark skin, fair skin`

**表情情绪**：
- 积极：`smiling, happy, joyful, excited, confident, peaceful`
- 消极：`sad, angry, worried, scared, surprised, confused`
- 中性：`serious, calm, focused, thinking, determined`

### 4. 场景环境描述
**室内场景**：
- `bedroom, kitchen, living room, classroom, office, library, cafe`
- `indoors, interior, cozy room, spacious hall`

**室外场景**：
- `park, street, forest, beach, mountain, city, countryside`
- `outdoors, nature, urban, landscape`

**时间/光线**：
- `daylight, sunlight, golden hour, sunset, night, moonlight`
- `bright lighting, soft lighting, dramatic lighting, natural light`

### 5. 画面质量提升词汇
**通用质量词**：
- `masterpiece, best quality, high resolution, detailed, sharp focus`
- `professional, cinematic, artistic, beautiful, stunning`

**画面构图**：
- `close-up, medium shot, full body, portrait, wide shot`
- `front view, side view, back view, three-quarter view`

### 6. 风格控制
**艺术风格**：
- `realistic, photorealistic, anime style, cartoon style, oil painting`
- `digital art, concept art, illustration, photography`

### 7. 实用示例模板
```
基础模板：
[主体] + [外貌] + [服装] + [表情] + [动作] + [场景] + [质量词]

具体例子：
"young woman, long black hair, blue eyes, wearing white dress, gentle smile, sitting by window, cozy bedroom, soft natural lighting, masterpiece, best quality, detailed"

角色一致性例子：
场景1: "teenage girl, shoulder-length brown hair, green eyes, school uniform, happy expression, walking, school corridor, bright lighting, high quality"
场景2: "teenage girl, shoulder-length brown hair, green eyes, school uniform, surprised expression, standing, classroom, natural light, high quality"
```

## 重要注意事项：
1. **脚本连贯性**：script中的原文片段拼接起来应为整个小说内容，不能删减导致文本不连贯
2. **角色一致性**：同一角色在不同分镜中必须保持外貌特征一致（发色、眼色、年龄、基本服装等）
3. **提示词长度**：建议每个image_prompt控制在75-100个词以内，避免过长
4. **英文用词**：使用简洁明确的英文单词，避免复杂句式
5. **权重平衡**：重要特征可适当加权，如角色外貌特征使用`(blonde hair:1.1)`
6. **场景变化**：不同场景的环境描述要准确反映故事情节的变化

通过遵循这些规则，可以生成高质量、风格一致的分镜图片。
"""


@scene_agent.tool
def read_content(ctx: RunContext[SceneAgentDeps]) -> str:
    """读取小说内容文件"""
    content_file = ctx.deps.content_file

    try:
        return read_content_file(content_file)

    except Exception as e:
        return f"读取内容失败: {str(e)}"


@scene_agent.tool
def generate_scenes(ctx: RunContext[SceneAgentDeps], scenes_data: list) -> str:
    """保存AI生成的分镜脚本"""
    try:
        # 清理和验证数据
        cleaned_scenes = clean_scenes_data(scenes_data)

        if not cleaned_scenes:
            return "错误: 没有有效的场景数据"

        # 保存分镜脚本
        result = save_scenes_scripts(cleaned_scenes)

        return f"成功保存 {len(cleaned_scenes)} 个场景的分镜脚本。{result}"

    except Exception as e:
        return f"保存分镜脚本失败: {str(e)}"


@scene_agent.tool
async def generate_images_and_audio(ctx: RunContext[SceneAgentDeps]) -> str:
    """同时生成场景图片和音频文件"""
    try:
        # 从保存的脚本文件中读取场景数据
        from utils.scene import load_scenes_scripts

        scenes_scripts = load_scenes_scripts()

        if not scenes_scripts:
            return "❌ 没有找到场景脚本数据"

        total_scenes = len(scenes_scripts)
        image_results = []
        audio_results = []

        async def run_video_generation():
            """视频生成任务"""
            try:
                image_result = batch_generate_images(scenes_scripts)
                image_results.append(
                    f"图片生成: {image_result['success_count']}/{image_result['total_scenes']} 成功"
                )
            except Exception as e:
                image_results.append(f"图片生成失败: {str(e)}")

        async def run_audio_generation():
            """音频生成任务"""

            async def generate_scene_audio(scene_id):
                """为单个场景生成音频"""
                try:
                    deps = TalkAgentDeps(scene_id=scene_id)
                    await talk_agent.run("请生成场景音频和字幕", deps=deps)
                    return f"场景 {scene_id}: ✅ 音频生成成功"
                except Exception as e:
                    return f"场景 {scene_id}: ❌ 音频生成失败 - {str(e)}"

            # 顺序执行音频生成
            for scene in scenes_scripts:
                scene_id = scene["scene_id"]
                try:
                    result = await generate_scene_audio(scene_id)
                    audio_results.append(result)
                except Exception as e:
                    audio_results.append(f"场景 {scene_id}: ❌ 音频处理异常 - {str(e)}")

        # 并行执行视频和音频生成
        video_task = asyncio.create_task(run_video_generation())
        audio_task = asyncio.create_task(run_audio_generation())
        await asyncio.gather(video_task, audio_task)

        # 统计结果
        audio_success_count = len([r for r in audio_results if "✅" in r])
        audio_failed_count = len([r for r in audio_results if "❌" in r])

        return f"""🎬 场景处理完成:

📊 总体统计:
- 总场景数: {total_scenes}

�️ 图片生成结果:
{chr(10).join(image_results)}

� 音频生成结果:
- 成功: {audio_success_count} 个场景
- 失败: {audio_failed_count} 个场景

📝 详细结果:
{chr(10).join(audio_results)}

✅ 所有场景的图片和音频文件已生成到 output/ 目录"""

    except Exception as e:
        return f"生成图片和音频失败: {str(e)}"
