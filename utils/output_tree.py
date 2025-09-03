from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def build_output_tree(base: Path) -> Dict[str, Any]:
    """构建指定目录的树结构（目录优先排序）。

    返回示例:
    {
        "name": "output",
        "type": "directory",
        "path": "",
        "children": [
            {"name": "images", "type": "directory", "path": "images", "children": [...]},
            {"name": "final_video.mp4", "type": "file", "path": "final_video.mp4", "size": 123, "mtime": "...", "ext": ".mp4"}
        ]
    }
    """

    def list_dir(d: Path) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if not d.exists():
            return items
        try:
            children = sorted(
                list(d.iterdir()),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except Exception:
            return items

        for p in children:
            # 过滤隐藏文件夹和常见临时目录
            if p.name.startswith('.') or p.name in {"__pycache__", ".cache"}:
                continue
            rel = str(p.relative_to(base)) if p != base else ""
            if p.is_dir():
                items.append(
                    {
                        "name": p.name,
                        "type": "directory",
                        "path": rel,
                        "children": list_dir(p),
                    }
                )
            else:
                try:
                    st = p.stat()
                    size = st.st_size
                    mtime = datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()
                except Exception:
                    size = None
                    mtime = None
                items.append(
                    {
                        "name": p.name,
                        "type": "file",
                        "path": rel,
                        "size": size,
                        "mtime": mtime,
                        "ext": p.suffix,
                    }
                )
        return items

    return {
        "name": base.name,
        "type": "directory",
        "path": "",
        "children": list_dir(base) if base.exists() else [],
    }
