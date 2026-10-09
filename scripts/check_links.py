#!/usr/bin/env python3
"""拾级 · 外部链接探测（零依赖）

扫技能包内的 Markdown 与 HTML，抽出全部 http(s) 链接逐个探测——
发现死链（404 / 域名失效），提醒维护者核实更换。

分类（结果只是提醒，逐条人工复核——网络波动与反爬都会造成误报）：
  [死链]  重试后仍失败（4xx／5xx／连不上／DNS 失败）——优先核实
  [待核]  403 / 429（反爬、限流）——多半正常，人工打开看一眼
  [超时]  重试后仍超时——网络波动可能误报，隔段时间再看

探测策略：先 HEAD 再 GET（有的站不支持 HEAD），两次都失败才记；
正文以"指路"为主、很少放深链——链接集中在 README / 安装指南 / FAQ
等对外文档，本脚本主要盯这些。CHANGELOG 不扫——历史条目的链接失效
属正常，改历史条目反而破坏记录。

用法：
  python3 scripts/check_links.py                 # 默认：并发 8，超时 6 秒
  python3 scripts/check_links.py --timeout 10    # 网络慢时放宽
退出码：有 [死链] 时退出 1（CI 中为提醒式步骤，不阻断合并）。
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent

MD_TARGETS = (
    sorted(ROOT.glob("references/**/*.md"))
    + sorted(ROOT.glob("references/**/*.html"))
    + [
        p
        for p in [
            ROOT / "README.md",
            ROOT / "README_EN.md",
            ROOT / "SKILL.md",
            ROOT / "AGENTS.md",
            ROOT / "MAINTAINING.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / "安装指南.md",
            ROOT / "自测题.md",
            ROOT / "docs" / "index.html",
            ROOT / "docs" / "FAQ.md",
        ]
        if p.exists()
    ]
)

URL_RE = re.compile(r"https?://[^\s<>\"'（）【】《》」\)\],，。；、]+")
TRAIL = ".,;:!?，。；：！？、*`"  # 含 markdown 强调符（** 与反引号）
UA = "Mozilla/5.0 (compatible; shiji-link-check/1.0)"


def extract_urls(text: str) -> set[str]:
    return {m.rstrip(TRAIL) for m in URL_RE.findall(text)}


def _safe_url(url: str) -> str:
    """非 ASCII（中文路径等）做 percent-encode——urllib 不认未编码的中文"""
    parts = urlsplit(url)
    netloc = parts.netloc
    if any(ord(ch) > 127 for ch in netloc):
        netloc = netloc.encode("idna").decode("ascii")
    return urlunsplit(
        (
            parts.scheme,
            netloc,
            quote(parts.path, safe="/%"),
            quote(parts.query, safe="=&%"),
            quote(parts.fragment, safe="%"),
        )
    )


def _fetch(url: str, method: str, timeout: float) -> int:
    req = urllib.request.Request(
        _safe_url(url), method=method, headers={"User-Agent": UA}
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    status = resp.status
    resp.read(64)
    resp.close()
    return status


def _attempt(url: str, method: str, timeout: float) -> tuple[str, str]:
    """单次探测。返回 (kind, detail)，kind ∈ ok / check / dead / timeout"""
    try:
        status = _fetch(url, method, timeout)
        if status < 400:
            return "ok", str(status)
        if status in (403, 429):
            return "check", f"HTTP {status}（反爬/限流）"
        return "dead", f"HTTP {status}"
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return "check", f"HTTP {e.code}（反爬/限流）"
        return "dead", f"HTTP {e.code}"
    except TimeoutError:
        return "timeout", "超时"
    except urllib.error.URLError as e:
        if isinstance(e.reason, TimeoutError):
            return "timeout", "超时"
        return "dead", f"连接失败（{e.reason}）"
    except Exception as e:  # SSL 等杂错兜底
        return "dead", f"{type(e).__name__}: {e}"


def probe(url: str, timeout: float) -> tuple[str, str]:
    k1 = _attempt(url, "HEAD", timeout)
    if k1[0] == "ok":
        return k1
    k2 = _attempt(url, "GET", timeout)
    if k2[0] == "ok":
        return k2
    if k1[0] == "check" or k2[0] == "check":
        return "check", (k2[1] if k2[0] == "check" else k1[1])
    if k1[0] == "timeout" or k2[0] == "timeout":
        return "timeout", "超时（两次）"
    return "dead", k2[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=6.0)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    url_to_files: dict[str, set[str]] = {}
    files = [p for p in MD_TARGETS if p.exists()]
    for p in files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        rel = str(p.relative_to(ROOT))
        for u in extract_urls(text):
            url_to_files.setdefault(u, set()).add(rel)

    urls = sorted(url_to_files)
    print(
        f"拾级外链探测：{len(urls)} 个唯一链接（来自 {len(files)} 个文件），"
        f"并发 {args.jobs}，超时 {args.timeout:g}s"
    )
    if not urls:
        return 0

    results: dict[str, tuple[str, str]] = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(probe, u, args.timeout): u for u in urls}
        for fut in as_completed(futs):
            results[futs[fut]] = fut.result()

    label = {"dead": "[死链]", "check": "[待核]", "timeout": "[超时]"}
    by_kind: dict[str, list[str]] = {}
    for u, (k, _) in results.items():
        by_kind.setdefault(k, []).append(u)

    for kind in ("dead", "check", "timeout"):
        items = sorted(by_kind.get(kind, []))
        if not items:
            continue
        print(f"\n== {label[kind]}（{len(items)}）==")
        for u in items:
            srcs = "、".join(sorted(url_to_files[u])[:3])
            print(f"  {u}\n      {results[u][1]}  ← {srcs}")

    n = {k: len(by_kind.get(k, [])) for k in ("ok", "dead", "check", "timeout")}
    print(
        f"\n===== 汇总：正常 {n['ok']} / 死链 {n['dead']} / "
        f"待核 {n['check']} / 超时 {n['timeout']} ====="
    )
    print("说明：结果为提醒项——反爬、限流、网络波动都会误报，逐条人工复核后再改。")
    return 1 if n["dead"] else 0


if __name__ == "__main__":
    sys.exit(main())
