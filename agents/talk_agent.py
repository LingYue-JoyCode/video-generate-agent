import os
from dataclasses import dataclass
from typing import List, Literal
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from utils.novel import split_sentences
from utils.tts import (
    generate_sentence_audio_and_srt, 
    merge_audio_files, 
    merge_srt_files
)


@dataclass
class TalkAgentDeps:
    script: str
    scene_id: int
    novel_content: str


@dataclass
class TalkAgentOutput:
    text: str = ""
    voice_type: Literal["male", "female", "narrator"] = "narrator"


talk_agent = Agent(
    model=chat_model,
    deps_type=TalkAgentDeps,
    output_type=List[TalkAgentOutput],
)


@talk_agent.instructions
def analyze_voice_assignment(ctx: RunContext[TalkAgentDeps]) -> str:
    """为已经切分好的句子分配音色"""
    scripts = ctx.deps.script
    novel_content = ctx.deps.novel_content
    scene_id = ctx.deps.scene_id
    sentences = '\n'.join(split_sentences(scripts))
    return f"""
你是一个小说配音生成agent，你需要根据用户提供的语句，分析每一句话应该用什么音色配音。

以下是当前的小说原文：
{novel_content}

以下是当前的需要配音的所有语句：
{sentences}

当前的场景id为：
{scene_id}

你的工作流程如下：
1. 根据小说原文梳理主要人物的性别
2. 根据语句内容和角色性别，为每个句子分配音色

音色分配规则：
- **male**: 男性角色对话、男性内心独白、以男性视角的内容
- **female**: 女性角色对话、女性内心独白、以女性视角的内容  
- **narrator**: 环境描述、叙述文字、无明确性别的内容、客观描述

请为每个句子分配合适的音色类型，然后调用 generate_audio_and_srt 工具生成音频文件。
"""


@talk_agent.tool
def generate_audio_and_srt(ctx: RunContext[TalkAgentDeps], segments: List[TalkAgentOutput]) -> str:
    """为分析后的句子生成音频和字幕文件"""
    scene_id = ctx.deps.scene_id

    # 验证数据
    valid_segments = []
    for seg in segments:
        if seg.text.strip():
            valid_segments.append((seg.text.strip(), seg.voice_type))
    
    try:
        # 确保输出目录存在
        audio_dir = "output/audio"
        srt_dir = "output/srt"
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(srt_dir, exist_ok=True)
        
        # 生成每个句子的音频和字幕
        audio_files, srt_files = generate_sentence_audio_and_srt(
            valid_segments, 
            "output", 
            scene_id
        )
        
        if not audio_files:
            return f"❌ 场景 {scene_id} 音频生成失败"
        
        # 合并音频文件
        merged_audio_path = os.path.join(audio_dir, f"scene_{scene_id}.wav")
        audio_result = merge_audio_files(audio_files, merged_audio_path)
        
        # 合并SRT文件
        merged_srt_path = os.path.join(srt_dir, f"scene_{scene_id}.srt")
        srt_result = merge_srt_files(srt_files, merged_srt_path)
        
        # 清理临时文件
        for temp_file in audio_files + srt_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        
        # 统计音色使用情况
        voice_stats = {}
        for _, voice_type in valid_segments:
            voice_stats[voice_type] = voice_stats.get(voice_type, 0) + 1
        
        stats_str = ", ".join([f"{voice}: {count}句" for voice, count in voice_stats.items()])
        
        return f"""✅ 场景 {scene_id} 音频和字幕生成完成:

📊 统计信息:
- 句子总数: {len(valid_segments)}
- 音色分布: {stats_str}

📁 输出文件:
- 音频: {merged_audio_path}
- 字幕: {merged_srt_path}

🔧 处理结果:
- {audio_result}
- {srt_result}"""
        
    except Exception as e:
        return f"❌ 生成音频和字幕失败: {str(e)}"