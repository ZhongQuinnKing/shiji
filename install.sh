#!/usr/bin/env bash
# 拾级一键安装（适用于 Claude Code / Codex / DSH / Cursor 等命令行 AI 环境）
#
# 用户用法（把这句话给支持命令行的 AI）：
#   "运行 https://github.com/ZhongQuinnKing/shiji 的 install.sh，把拾级装为技能"
# 或手动：
#   curl -fsSL https://raw.githubusercontent.com/ZhongQuinnKing/shiji/main/install.sh | bash
#
# 自定义安装目录：SHIJI_DIR=/path/to/skills/shiji bash install.sh
set -euo pipefail

REPO="https://github.com/ZhongQuinnKing/shiji"
DEST="${SHIJI_DIR:-$HOME/.claude/skills/shiji}"

echo "== 拾级安装 =="
echo "目标目录：$DEST"
mkdir -p "$(dirname "$DEST")"

if [ -d "$DEST/.git" ]; then
  echo "检测到已有安装，尝试更新……"
  (cd "$DEST" && git pull --ff-only 2>/dev/null) || echo "（更新失败，保留现有版本）"
else
  rm -rf "$DEST"
  if git clone --depth 1 "$REPO" "$DEST" 2>/dev/null; then
    echo "✓ 已通过 git clone 安装"
  else
    echo "git 直连不通，改用 tarball 下载……"
    TMP="$(mktemp -d)"
    if curl -fsSL --max-time 120 -o "$TMP/repo.tar.gz" \
        "https://api.github.com/repos/ZhongQuinnKing/shiji/tarball/main"; then
      mkdir -p "$DEST"
      tar -xzf "$TMP/repo.tar.gz" -C "$DEST" --strip-components=1
      rm -rf "$TMP"
      echo "✓ 已通过 tarball 安装"
    else
      echo "✗ 下载失败——请检查网络，或到 GitHub 页面 Code → Download ZIP 手动解压"
      exit 1
    fi
  fi
fi

# 验证
if [ -f "$DEST/SKILL.md" ]; then
  echo "✓ 验证通过：SKILL.md 就位"
  PARTS=$(find "$DEST/references" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "✓ 内容文件：$PARTS 篇"
  python3 "$DEST/scripts/check_content.py" 2>/dev/null | tail -1 || true
else
  echo "✗ 安装不完整（缺 SKILL.md），请重试或提 issue"
  exit 1
fi

echo ""
echo "装好了——现在直接提问即可：宿舍矛盾 / 简历 / 考研 / 论文 / 职场……"
echo "（豆包等上传制平台：请到 GitHub 下载 ZIP 后按《安装指南.md》上传。）"
