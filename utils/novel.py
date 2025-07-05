"""
小说处理工具模块
提供文件读取和分句功能
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import chardet

@dataclass
class NovelChunk:
    content: str
    continue_read: bool


def detect_encoding(file_path: str) -> str:
    """检测文件编码"""
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(1000)
            result = chardet.detect(raw_data)
            encoding = result.get("encoding", "utf-8")
            
            # 简化编码处理
            if encoding and encoding.lower() in ["gb2312", "gbk"]:
                return "gbk"
            elif encoding and encoding.lower() == "big5":
                return "big5"
            else:
                return "utf-8"
    except Exception:
        return "utf-8"


def split_sentences(text: str) -> list:
    """简单分句处理"""
    if not text:
        return []
    
    import re
    # 按段落分割
    paragraphs = text.split("\n")
    sentences = []
    pattern = re.compile(r'([。！？!?])')
    quote_pattern = re.compile(r'"[^"]+"|“[^”]+”')

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # 先提取引号内的内容
        quotes = []
        def quote_replacer(match):
            quotes.append(match.group())
            return f'[[QUOTE_{len(quotes)-1}]]'
        temp = quote_pattern.sub(quote_replacer, paragraph)

        # 按标点分割
        parts = []
        start = 0
        for m in pattern.finditer(temp):
            end = m.end()
            part = temp[start:end].strip()
            if part:
                parts.append(part)
            start = end
        if start < len(temp):
            last = temp[start:].strip()
            if last:
                parts.append(last)

        # 恢复引号内容并按长度过滤
        for part in parts:
            # 恢复引号
            def restore_quote(m):
                idx = int(m.group(1))
                return quotes[idx] if idx < len(quotes) else m.group(0)
            part = re.sub(r'\[\[QUOTE_(\d+)\]\]', restore_quote, part)
            # 如果是完整引号句子，直接加入
            if quote_pattern.fullmatch(part):
                sentences.append(part)
            elif part and len(part) > 3:
                sentences.append(part)

    return sentences


def read_novel_content(
    novel_file_path: str,
    chunk_size: int = 500,
    chapter_regex: str = r"第[一二三四五六七八九十百千0-9]+章"
) -> NovelChunk:
    """
    读取小说内容，返回内容和是否需要继续读取
    """
    if not Path(novel_file_path).exists():
        raise FileNotFoundError(f"小说文件不存在: {novel_file_path}")
    
    # 生成缓存文件路径
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    file_hash = hashlib.md5(novel_file_path.encode("utf-8")).hexdigest()
    cache_path = cache_dir / f"novel_{file_hash}.json"
    
    # 读取缓存
    offset = 0
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
                offset = cache.get("offset", 0)
        except Exception:
            offset = 0
    
    # 检测编码并读取文件
    encoding = detect_encoding(novel_file_path)
    
    try:
        with open(novel_file_path, "r", encoding=encoding) as f:
            # 使用字符偏移量，先读取到指定位置
            if offset > 0:
                f.read(offset)
            raw_text = f.read(chunk_size)
    except Exception:
        raise RuntimeError("无法读取文件")
    
    if not raw_text:
        return NovelChunk(content="", continue_read=False)

    # 如果读取到的内容包含章节标题，则在章节前截断
    chapter_match = re.search(chapter_regex, raw_text)
    if chapter_match and chapter_match.start() > 0:
        raw_text = raw_text[:chapter_match.start()]
        if not raw_text:
            return NovelChunk(content="", continue_read=False)
        continue_read = False
    else:
        continue_read = True
    
    # 分句处理
    sentences = split_sentences(raw_text)
    
    # 选择合适长度的内容
    selected_text = ""
    for sentence in sentences:
        if len(selected_text + sentence) > chunk_size and selected_text:
            break
        selected_text += sentence
    
    if not selected_text:
        selected_text = raw_text[:chunk_size]
    
    # 更新缓存 - 使用字符偏移量而不是字节偏移量
    # 计算已读取的字符数
    chars_read = len(selected_text)
    new_offset = offset + chars_read
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"offset": new_offset}, f)
    except Exception:
        pass

    return NovelChunk(content=selected_text, continue_read=continue_read)
