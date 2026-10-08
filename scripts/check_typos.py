#!/usr/bin/env python3
"""拾级 · 全文校对扫描（零依赖）

查什么（逐条人工复核后再改，避免误伤）：
  1. 重复字（的的/了了/是是……非叠词的错误重复）
  2. 重复标点（。。/，，/！！/、、……）
  3. 半角标点混入中文（中文旁的 , ; : ! ? 和句尾 .）
  4. 全角字母数字（Ａ１ 之类）
  5. 空格异常（中文间多空格 / 标点前空格 / 行尾空格）
  6. 引号与括号配对（“”「」（）《》** 数量不符）
  7. 常见错别字词表（登陆/帐号/按耐……；只列不改）

用法：
  python3 scripts/check_typos.py            # 全量扫描（含 styles 提示）
  python3 scripts/check_typos.py --strict   # 不显示 styles 类提示
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- 1. 重复字（只列"大概率是错"的，不含叠词如 谢谢/刚刚/慢慢）----
DUP_CHARS = "的了是我你他地得着过就都很和与也都这那"
DUP_RE = re.compile("([" + DUP_CHARS + "])\\1")

# ---- 2. 重复标点 ----
DUP_PUNCT_RE = re.compile(r"(。。|，，|；；|：：|？？|！！|、、|\.\.\.\.)")

# ---- 3. 半角标点混中文 ----
HALF_PUNCT_RE = re.compile(r"[一-鿿][,;:!?]|[,;:!?][一-鿿]|[一-鿿]\.(?![0-9])")

# ---- 4. 全角字母数字 ----
FULLWIDTH_RE = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")

# ---- 5. 空格异常 ----
CJK_GAP_RE = re.compile(r"[一-鿿][ \t]{2,}[一-鿿]")
TRAIL_RE = re.compile(r"[ \t]+$")
PUNCT_GAP_RE = re.compile(r"[ \t]+[，。；：！？、）】》」”]")

# ---- 6. 配对 ----
PAIRS = [("“", "”"), ("「", "」"), ("（", "）"), ("《", "》"), ("【", "】")]

# ---- 7. 常见错别字（只列不改，人工定夺）----
TYPO_TABLE = [
    ("登陆", "登录（账号语境）"),
    ("帐号", "账号"),
    ("按耐", "按捺"),
    ("寒喧", "寒暄"),
    ("迫不急待", "迫不及待"),
    ("一如继往", "一如既往"),
    ("有持无恐", "有恃无恐"),
    ("再接再励", "再接再厉"),
    ("相辅相承", "相辅相成"),
    ("走头无路", "走投无路"),
    ("莫明其妙", "莫名其妙"),
    ("直捷了当", "直截了当"),
    ("必竟", "毕竟"),
    ("部份", "部分"),
    ("做为", "作为"),
    ("影象", "影像"),
    ("决对", "绝对"),
    ("陷井", "陷阱"),
    ("幅射", "辐射"),
    ("精采", "精彩"),
    ("出奇不意", "出其不意"),
    ("一诺千斤", "一诺千金"),
    ("报歉", "抱歉"),
    ("迫在眉稍", "迫在眉睫"),
    ("老俩口", "老两口"),
    ("好高鹜远", "好高骛远"),
]

# ---- 8. 样式提示：中英文之间缺空格（只统计+抽样）----
CJK_LATIN_RE = re.compile(r"[一-鿿][A-Za-z0-9]|[A-Za-z0-9][一-鿿]")


def scan_file(path: Path, show_style: bool):
    issues: list[tuple[str, int, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    for i, line in enumerate(lines, 1):
        for m in DUP_RE.finditer(line):
            issues.append(("重复字", i, f"{m.group(0)} ← {line.strip()[:60]}"))
        for m in DUP_PUNCT_RE.finditer(line):
            issues.append(("重复标点", i, f"{m.group(0)} ← {line.strip()[:60]}"))
        for m in HALF_PUNCT_RE.finditer(line):
            s = max(0, m.start() - 12)
            issues.append(("半角标点", i, f"…{line[s:m.end() + 12].strip()}…"))
        for m in FULLWIDTH_RE.finditer(line):
            issues.append(("全角字母数字", i, f"{m.group(0)} ← {line.strip()[:60]}"))
        for m in CJK_GAP_RE.finditer(line):
            issues.append(("中文间多空格", i, f"…{line[m.start():m.end()].strip()}…"))
        if TRAIL_RE.search(line):
            issues.append(("行尾空格", i, f"({len(TRAIL_RE.search(line).group(0))} 个)"))
        for m in PUNCT_GAP_RE.finditer(line):
            issues.append(("标点前空格", i, f"…{line[max(0, m.start() - 10):m.end()].strip()}…"))
        for wrong, right in TYPO_TABLE:
            if wrong in line:
                issues.append(("错别字?", i, f"{wrong} → 应为 {right}；{line.strip()[:50]}"))

    for left, right in PAIRS:
        if text.count(left) != text.count(right):
            issues.append(("配对异常", 0, f"{left}={text.count(left)} vs {right}={text.count(right)}"))
    if text.count("**") % 2 != 0:
        issues.append(("配对异常", 0, f"** 为奇数（{text.count('**')}）"))

    style_hits = CJK_LATIN_RE.findall(text) if show_style else []
    return issues, len(style_hits)


def main():
    show_style = "--strict" not in sys.argv
    targets = sorted(ROOT.glob("references/**/*.md")) + [
        p for p in [ROOT / "README.md", ROOT / "SKILL.md", ROOT / "安装指南.md",
                    ROOT / "自测题.md", ROOT / "README_EN.md"]
        if p.exists()
    ]
    total = 0
    style_total = 0
    by_file: list[tuple[str, list]] = []
    for p in targets:
        issues, style_n = scan_file(p, show_style)
        style_total += style_n
        if issues:
            total += len(issues)
            by_file.append((str(p.relative_to(ROOT)), issues))

    for name, issues in by_file:
        print(f"\n== {name} ==")
        shown: dict[str, int] = {}
        for cat, ln, detail in issues:
            shown[cat] = shown.get(cat, 0) + 1
            if shown[cat] <= 12:  # 每类每文件最多列 12 条
                loc = f"L{ln}" if ln else "文件级"
                print(f"  [{cat}] {loc}: {detail}")
        for cat, n in shown.items():
            if n > 12:
                print(f"  [{cat}] …… 其余 {n - 12} 条同类省略")

    print(f"\n===== 汇总：{len(targets)} 个文件，{total} 条待复核 =====")
    if show_style:
        print(f"（样式提示：中英文紧贴 {style_total} 处——未必是错，按需看）")
    print("说明：全部为提醒项，逐条人工复核后修改，勿批量盲改。")


if __name__ == "__main__":
    main()
