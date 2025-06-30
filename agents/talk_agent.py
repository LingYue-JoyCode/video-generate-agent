import os
import json
import re
from dataclasses import dataclass
from typing import List, Literal, Optional
from pydantic_ai import Agent, RunContext
from utils.llm import chat_model
from utils.tts import (
    generate_sentence_audio_and_srt, 
    merge_audio_files, 
    merge_srt_files
)


@dataclass
class TalkAgentDeps:
    scene_id: int = 1  # 场景ID


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
    return """
请你按照以下的流程进行工作。

1. 调用 parse_script_sentences 工具
2. 根据工具返回的数组，遍历句子数组，为每个句子分配音色

音色分配规则：
- **male**: 男性角色对话、男性内心独白、以男性视角的内容
- **female**: 女性角色对话、女性内心独白、以女性视角的内容  
- **narrator**: 环境描述、叙述文字、无明确性别的内容、客观描述

请为每个句子分配合适的音色类型，然后调用 generate_audio_and_srt 工具生成音频文件。
"""


@talk_agent.tool
def parse_script_sentences(ctx: RunContext[TalkAgentDeps]) -> str:
    """读取场景脚本并切分成句子数组"""
    scene_id = ctx.deps.scene_id
    scenes_file = "output/scenes.json"
    
    if not os.path.exists(scenes_file):
        return f"❌ 场景文件不存在: {scenes_file}"
    
    try:
        with open(scenes_file, "r", encoding="utf-8") as f:
            scenes_data = json.load(f)
        
        # 查找指定场景
        for scene in scenes_data:
            if scene.get("scene_id") == scene_id:
                script = scene.get("script", "")
                if not script:
                    return f"❌ 场景 {scene_id} 的脚本内容为空"
                
                # 使用智能切分函数切分句子
                sentences = _smart_split_sentences(script)
                
                # 更新 deps 中的句子列表
                ctx.deps.sentences = sentences
                
                return f"""✅ 场景 {scene_id} 脚本切分完成:

原文字符数: {len(script)}
切分句子数: {len(sentences)}

句子列表:
{chr(10).join([f"{i+1}. {sentence}" for i, sentence in enumerate(sentences)])}

请为每个句子分配合适的音色类型（male/female/narrator），然后调用 generate_audio_and_srt 工具。"""
        
        return f"❌ 未找到场景 {scene_id} 的数据"
        
    except Exception as e:
        return f"❌ 读取和切分场景文件失败: {str(e)}"


def _smart_split_sentences(text: str) -> List[str]:
    """智能切分句子，识别对话、内心独白和叙述"""
    sentences = []
    
    # 预处理：处理引号内的内容
    parts = re.split(r'([""『』「」][^""『』「」]*[""『』「」])', text)
    
    current_text = ""
    
    for part in parts:
        if not part.strip():
            continue
            
        # 如果是引号内容，作为一个整体处理
        if re.match(r'^[""『』「」].*[""『』「」]$', part.strip()):
            if current_text.strip():
                # 先处理之前积累的文本
                temp_sentences = _split_by_punctuation(current_text)
                sentences.extend(temp_sentences)
                current_text = ""
            
            # 引号内容作为独立句子
            quote_content = part.strip()
            if quote_content:
                sentences.append(quote_content)
        else:
            current_text += part
    
    # 处理剩余的文本
    if current_text.strip():
        temp_sentences = _split_by_punctuation(current_text)
        sentences.extend(temp_sentences)
    
    # 清理和优化句子
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 1:  # 过滤掉单字符和空句子
            # 如果句子太长（超过60字），尝试进一步切分
            if len(sentence) > 60:
                sub_sentences = _split_long_sentence(sentence)
                cleaned_sentences.extend(sub_sentences)
            else:
                cleaned_sentences.append(sentence)
    
    return cleaned_sentences


def _split_by_punctuation(text: str) -> List[str]:
    """按标点符号切分文本"""
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if char in '。！？':
            if current.strip():
                sentences.append(current.strip())
            current = ""
    
    # 处理最后没有标点的部分
    if current.strip():
        sentences.append(current.strip())
    
    return sentences


def _split_long_sentence(sentence: str) -> List[str]:
    """切分过长的句子"""
    if len(sentence) <= 60:
        return [sentence]
    
    # 尝试在逗号、分号处切分
    parts = re.split(r'([，；、])', sentence)
    
    result = []
    current = ""
    
    for part in parts:
        if current and len(current + part) > 50:
            if current.strip():
                result.append(current.strip())
            current = part
        else:
            current += part
    
    if current.strip():
        result.append(current.strip())
    
    return result if result else [sentence]


@talk_agent.tool
def generate_audio_and_srt(ctx: RunContext[TalkAgentDeps], segments: List[TalkAgentOutput]) -> str:
    """为分析后的句子生成音频和字幕文件"""
    scene_id = ctx.deps.scene_id
    
    if not segments:
        return f"❌ 场景 {scene_id} 没有有效的语句段落"
    
    # 验证数据
    valid_segments = []
    for seg in segments:
        if seg.text.strip():
            valid_segments.append((seg.text.strip(), seg.voice_type))
    
    if not valid_segments:
        return f"❌ 场景 {scene_id} 没有有效的文本内容"
    
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