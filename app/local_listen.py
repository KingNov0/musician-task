"""本地互助歌曲 ID 的解析与规范化。"""

from __future__ import annotations

import re


def parse_item_ids(value: str | None) -> list[str]:
    """支持逗号、中文逗号、分号、空白和换行分隔，并保持去重后的原顺序。"""
    parts = re.split(r"[,，;；\s]+", str(value or "").strip())
    result: list[str] = []
    for part in parts:
        item_id = part.strip()
        if not item_id:
            continue
        raw_id = item_id[6:] if item_id.startswith("album:") else item_id
        if not raw_id.isdigit():
            raise ValueError(f"无效的歌曲/专辑 ID：{item_id}")
        if item_id not in result:
            result.append(item_id)
    return result


def normalize_item_ids(value: str | None) -> str:
    return ",".join(parse_item_ids(value))
