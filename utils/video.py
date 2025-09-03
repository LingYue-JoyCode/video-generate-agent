from moviepy import (
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    vfx,
    afx
)
from moviepy.video.VideoClip import VideoClip
import os
import random
from moviepy.video.tools.subtitles import SubtitlesClip
from typing import cast, Optional
import dotenv

dotenv.load_dotenv()

FONT_PATH = os.getenv("FONT_PATH") or 'assets/font/MapleMono-NF-CN-Regular.ttf'


def _find_with_exts(base_dir: str, base_name: str, exts: list[str]) -> Optional[str]:
    """在 base_dir 下按给定扩展名顺序查找文件，返回首个存在的路径。"""
    for ext in exts:
        path = os.path.join(base_dir, f"{base_name}{ext}")
        if os.path.exists(path):
            return path
    return None


def generate_video() -> str:
    """
    根据最新的 output 目录结构（无需 scenes.json）生成最终视频：
    - 扫描 output/audio 下的 scene_*.{mp3,wav,ogg,m4a}
    - 匹配 output/images 下对应 scene_*.{png,jpg,jpeg,webp}
    - 匹配 output/subtitles 下对应 scene_*.srt（可选）
    
    Returns:
        str: 生成结果描述
    """
    try:
        # 检查必要的目录
        audio_dir = "output/audio"
        image_dir = "output/images"
        srt_dir = "output/subtitles"

        if not os.path.isdir(audio_dir):
            return f"❌ 音频目录不存在: {audio_dir}"
        if not os.path.isdir(image_dir):
            return f"❌ 图片目录不存在: {image_dir}"

        # 收集所有场景的媒体文件（以音频为基准）
        clips = []
        missing_files = []

        # 支持的扩展名
        audio_exts = [".mp3", ".wav", ".ogg", ".m4a"]
        image_exts = [".png", ".jpg", ".jpeg", ".webp"]

        # 从音频目录提取 scene_id
        candidates = []
        for fname in os.listdir(audio_dir):
            name_lower = fname.lower()
            if not any(name_lower.endswith(ext) for ext in audio_exts):
                continue
            # 匹配 scene_{id}.ext
            if name_lower.startswith("scene_"):
                stem = os.path.splitext(fname)[0]  # scene_{id}
                parts = stem.split("_")
                if len(parts) == 2 and parts[1].isdigit():
                    candidates.append(int(parts[1]))

        if not candidates:
            return "❌ 未在 output/audio 下找到任何场景音频文件"

        for scene_id in sorted(candidates):
            base = f"scene_{scene_id}"
            audio_file = _find_with_exts(audio_dir, base, audio_exts)
            image_file = _find_with_exts(image_dir, base, image_exts)
            srt_file = os.path.join(srt_dir, f"{base}.srt") if os.path.isdir(srt_dir) else None
            if srt_file and not os.path.exists(srt_file):
                srt_file = None

            if not audio_file:
                missing_files.append(f"音频缺失: {os.path.join(audio_dir, base)}.*")
                continue
            if not image_file:
                missing_files.append(f"图片缺失: {os.path.join(image_dir, base)}.*")
                continue

            # 创建视频片段
            try:
                clip = create_video_clip(audio_file, image_file, srt_file)
                clips.append(clip)
            except Exception as e:
                missing_files.append(f"场景 {scene_id} 处理失败: {str(e)}")
        
        if missing_files:
            return "❌ 以下文件缺失或处理失败:\n" + "\n".join(missing_files)
        
        if not clips:
            return "❌ 没有可用的视频片段"
        
        # 合成最终视频
        final_video_path = compose_final_video(clips)
        
        return f"✅ 视频生成成功: {final_video_path}\n共包含 {len(clips)} 个场景"
        
    except Exception as e:
        return f"❌ 视频生成失败: {str(e)}"


def create_video_clip(audio_file: str, image_file: str, srt_file: Optional[str]) -> VideoClip:
    """
    创建单个视频片段
    
    Args:
        audio_file: 音频文件路径
        image_file: 图片文件路径
        srt_file: 字幕文件路径（可为 None 表示无字幕）
        
    Returns:
        VideoClip: 视频片段
    """
    # 加载音频
    audio_clip = AudioFileClip(audio_file)
    
    # 加载图片并设置持续时间
    image_clip = ImageClip(image_file, duration=audio_clip.duration)

    # 创建字幕（可选）
    srt_clip = None
    if srt_file:
        srt_clip = SubtitlesClip(
            subtitles=srt_file,
            encoding="utf-8",
            make_textclip=lambda text: TextClip(
                font=FONT_PATH if os.path.exists(FONT_PATH) else "Arial",
                text=text,
                font_size=48,
                color="white",
                stroke_color="black",
                stroke_width=2,
                vertical_align="center",
                margin=(10, 10, 10, 48 * 3),
                method="caption",
                text_align="center",
                size=(image_clip.w, None),
            ),
        )
    
    # 应用特效到图片
    image_with_effects = cast(
        VideoClip,
        image_clip.with_effects([
            vfx.FadeIn(0.5),
            vfx.FadeOut(0.5),
        ])
    )
    
    # 合成视频片段
    layers = [image_with_effects.with_audio(audio_clip)]
    if srt_clip is not None:
        layers.append(srt_clip.with_position(("center", "bottom")))

    video_clip = CompositeVideoClip(layers)
    
    return video_clip


def compose_final_video(clips: list) -> str:
    """
    合成最终视频
    
    Args:
        clips: 视频片段列表
        
    Returns:
        str: 输出视频文件路径
    """
    if not clips:
        raise ValueError("没有视频片段可合成")
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 合并所有视频片段
    final_clip = concatenate_videoclips(clips=clips, method="compose")
    
    # 添加背景音乐
    final_clip = add_background_music(final_clip)
    
    # 输出文件路径
    output_path = "output/final_video.mp4"
    
    # 渲染视频
    final_clip.write_videofile(
        output_path,
        fps=24
    )
    
    return output_path


def add_background_music(video_clip: VideoClip) -> VideoClip:
    """
    为视频添加背景音乐
    
    Args:
        video_clip: 原视频片段
        
    Returns:
        VideoClip: 添加背景音乐后的视频
    """
    bgm_path = "assets/bgm"
    
    if not os.path.exists(bgm_path) or not os.path.isdir(bgm_path):
        return video_clip
    
    # 查找背景音乐文件
    bgm_files = [
        f for f in os.listdir(bgm_path) 
        if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))
    ]
    
    if not bgm_files:
        return video_clip
    
    try:
        # 随机选择一个背景音乐
        selected_bgm = random.choice(bgm_files)
        bgm_clip = AudioFileClip(os.path.join(bgm_path, selected_bgm))
        
        # 调整BGM音量为原声的10%
        bgm_clip = bgm_clip.with_volume_scaled(0.1).with_effects([afx.AudioLoop(duration=video_clip.duration)])

        # 混合音频
        original_audio = video_clip.audio
        if original_audio:
            mixed_audio = CompositeAudioClip([original_audio, bgm_clip])
            return video_clip.with_audio(mixed_audio)
        else:
            return video_clip.with_audio(bgm_clip)
            
    except Exception as e:
        print(f"警告：添加背景音乐失败: {e}")
        return video_clip
    
    return video_clip


# 保持向后兼容的旧函数（废弃）
def generate_video_legacy(current_chapter: int) -> None:
    """
    废弃的旧版本generate_video函数，仅保持向后兼容
    请使用新的generate_video()函数
    """
    print("警告：此函数已废弃，请使用新的generate_video()函数")
    result = generate_video()
    print(result)


if __name__ == "__main__":
    result = generate_video()
    print(result)