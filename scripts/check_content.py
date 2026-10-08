#!/usr/bin/env python3
"""拾级 · 内容自检脚本（零依赖，Python 3 标准库）

维护者工具：每次大更新后跑一遍，检查：
  1. 必需文件是否齐全
  2. 全书交叉引用（`NN-篇名` 形式）是否都指向真实存在的文件
  3. AI 腔/模板句式（一方面…另一方面、综上所述 等）
  4. 占位符残留（待补充 / TODO / TBD）
  5. SKILL.md 的 frontmatter 完好（name / description）

用法：python3 scripts/check_content.py
返回码：0 = 通过；1 = 有问题（明细打印在终端）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"
LINES = ["life", "study", "thesis", "kaoyan", "job", "grad", "workplace", "liuxue",
         "daxue", "gongkao", "gaokao", "tebie"]

REQUIRED = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "自测题.md",
    "references/00-红线清单.md",
    "references/01-档案与相处守则.md",
    "references/02-升学与就业地图.md",
    "references/03-依据与参考体系.md",
    "references/04-信息与信源.md",
    "references/daxue/00-大学的规则.md",
    "references/gongkao/00-考公考编全流程.md",
    "references/gaokao/00-高考全流程与时间轴.md",
    "references/tebie/00-入伍与兵役登记.md",
]

# AI 腔词表（命中即报；注意：讲解"不要这样写"的篇目可能合法出现，人工复核）
AI_PATTERNS = [
    "一方面", "综上所述", "值得注意的是", "总而言之",
    "[待补充]", "TODO", "TBD",
]

# 允许出现 AI 腔词的白名单（讲反面案例的地方）
WHITELIST = {
    "references/thesis/03-结构与写作.md",   # 讲解"不要写目录腔"
    "references/job/26-JD逆向法.md",        # 含 "JTBD" 字样（TBD 子串误报）
}


def check_required(errors: list[str]) -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"[必需文件缺失] {rel}")


def check_cross_refs(errors: list[str], warnings: list[str]) -> None:
    """收集全书 `line/NN-篇名` 引用，逐条核对目标存在。"""
    have: dict[str, set[str]] = {}
    for line in LINES:
        d = REFS / line
        if d.is_dir():
            have[line] = {p.stem for p in d.glob("*.md")}
        else:
            # 新线建到一半时目录还不存在——报提醒不报错，免得挡了别的检查
            warnings.append(f"[线目录未建] references/{line}/（建线中，成线后应为错误）")

    ref_re = re.compile(r"`([a-z]+)/([0-9]{2}-[^`\s]+)`")
    seen: set[str] = set()
    for md in list(REFS.rglob("*.md")) + [ROOT / "SKILL.md"]:
        text = md.read_text(encoding="utf-8")
        for m in ref_re.finditer(text):
            line, name = m.group(1), m.group(2)
            if line not in have:
                continue
            key = f"{line}/{name}"
            if key in seen:
                continue
            seen.add(key)
            if name not in have[line]:
                errors.append(f"[引用断链] {md.relative_to(ROOT)} → {key}")


def check_ai_patterns(errors: list[str], warnings: list[str]) -> None:
    for md in sorted(REFS.rglob("*.md")) + [ROOT / "SKILL.md", ROOT / "README.md"]:
        rel = str(md.relative_to(ROOT))
        text = md.read_text(encoding="utf-8")
        for pat in AI_PATTERNS:
            for i, line in enumerate(text.splitlines(), 1):
                if pat in line:
                    msg = f"[AI腔/占位符] {rel}:{i} 命中「{pat}」"
                    if rel in WHITELIST:
                        warnings.append("(白名单跳过) " + msg)
                    else:
                        errors.append(msg)


def check_frontmatter(errors: list[str]) -> None:
    skill = ROOT / "SKILL.md"
    if not skill.exists():
        return
    m = re.match(r"^---\n(.*?)\n---\n", skill.read_text(encoding="utf-8"), re.DOTALL)
    if not m:
        errors.append("[frontmatter] SKILL.md 缺少 YAML frontmatter")
        return
    fm = m.group(1)
    for key in ("name:", "description:"):
        if key not in fm:
            errors.append(f"[frontmatter] SKILL.md 缺少 {key}")


# 红线风险短语（只会以"提供此类服务"的口吻出现才危险；讲解禁忌的语境已被白名单放过）
RED_FLAG_PATTERNS = [
    "帮你代写", "代写服务", "有偿代写", "代降重服务", "帮你写论文",
    "帮你做作业", "代考", "心理诊断结论", "帮你查一下他", "查人服务",
]
# 合法讲解这些概念的文件（红线清单/方法篇在"禁止"语境中提及它们）
RED_FLAG_WHITELIST = {
    "references/00-红线清单.md",
    "references/thesis/05-查重与降重.md",
    "references/study/04-用AI学习.md",
    "references/job/26-JD逆向法.md",
    "references/job/30-笔试怎么准备.md",
    "CONTRIBUTING.md",
    "README.md",
    "自测题.md",
}


def check_red_flags(errors: list[str], warnings: list[str]) -> None:
    for md in sorted(REFS.rglob("*.md")) + [ROOT / "SKILL.md"]:
        rel = str(md.relative_to(ROOT))
        text = md.read_text(encoding="utf-8")
        for pat in RED_FLAG_PATTERNS:
            if pat in text:
                msg = f"[红线风险短语] {rel} 命中「{pat}」——请人工复核语境"
                if rel in RED_FLAG_WHITELIST:
                    warnings.append("(白名单跳过) " + msg)
                else:
                    warnings.append(msg)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    check_required(errors)
    check_cross_refs(errors, warnings)
    check_ai_patterns(errors, warnings)
    check_frontmatter(errors)
    check_red_flags(errors, warnings)

    total_md = len(list(REFS.rglob("*.md")))
    print(f"拾级内容自检：共 {total_md} 篇 references + SKILL/README")
    for w in warnings:
        print("  ⚠ " + w)
    if errors:
        print(f"\n发现 {len(errors)} 个问题：")
        for e in errors:
            print("  ✗ " + e)
        return 1
    tail = f"（另有 {len(warnings)} 条提示，见上方）" if warnings else ""
    print("✓ 全部通过（必需文件齐 / 引用无断链 / 无 AI 腔残留 / 红线无风险短语 / "
          f"frontmatter 完好）{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
