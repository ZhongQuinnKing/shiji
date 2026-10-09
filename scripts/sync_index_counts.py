#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预览页卡片计数同步：从 references/ 统计各线实际篇数，重写 docs/index.html。

用法：
    python3 scripts/sync_index_counts.py          # 自动对齐（有改动会报告）
    python3 scripts/sync_index_counts.py --check   # 只查不改（CI 用；不一致退出 1）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
INDEX = ROOT / "docs" / "index.html"

# 卡片名 → 目录、数字后的固定尾巴
LINES = [
    ("高考", "gaokao", " 篇"),
    ("大学", "daxue", " 篇"),
    ("考研", "kaoyan", " 篇 + 推免"),
    ("考公考编", "gongkao", " 篇"),
    ("求职", "job", " 篇 + 工具"),
    ("职场", "workplace", " 篇"),
    ("论文", "thesis", " 篇"),
    ("研究生", "grad", " 篇"),
    ("留学", "liuxue", " 篇"),
    ("学习", "study", " 篇"),
    ("人际与生活", "life", " 篇"),
    ("特殊通道", "tebie", " 篇"),
]


def count(d):
    return len(list((REFS / d).glob("*.md")))


def main():
    check = "--check" in sys.argv
    text = INDEX.read_text(encoding="utf-8")
    changes = []
    for name, d, suffix in LINES:
        want = f"{count(d)}{suffix}"
        pat = re.compile(rf"(<h3>{name} <span>)([^<]*)(</span></h3>)")
        m = pat.search(text)
        if not m:
            print(f"[未匹配] 卡片「{name}」——预览页模板变了，脚本要跟着改")
            sys.exit(1)
        if m.group(2) != want:
            changes.append(f"{name}: {m.group(2)} → {want}")
            text = text[:m.start()] + m.group(1) + want + m.group(3) + text[m.end():]

    if not changes:
        print("预览页计数与实际一致（12 线）")
        return
    if check:
        print("预览页计数与实际不一致：")
        for c in changes:
            print("  " + c)
        sys.exit(1)
    INDEX.write_text(text, encoding="utf-8")
    print("已对齐：")
    for c in changes:
        print("  " + c)


if __name__ == "__main__":
    main()
