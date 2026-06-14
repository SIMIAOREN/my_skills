#!/usr/bin/env python3
"""
通用网页内容抓取脚本 —— 适用于 bilingual-markdown-translator skill。

功能：
- 将任意 URL 的 HTML 内容转换为 Markdown
- 支持 html2text 主方案 + beautifulsoup4 回退方案
- 支持 Cloudflare 绕过 (cloudscraper)
- 支持页面结构探测 (WebFetch 辅助选定 CSS selector)

用法：
  python fetch_url.py <url>                               # 自动爬取，输出 Markdown
  python fetch_url.py <url> --selector "article"          # 指定 CSS selector
  python fetch_url.py <url> --probe                       # 先探测页面结构（返回建议的 selector）
  python fetch_url.py <url> --output output.md            # 保存到文件

输出：stdout 直接输出 Markdown 文本。错误信息走 stderr。
"""

import sys
import argparse
import requests
from html2text import HTML2Text


def fetch_url_to_markdown(url: str, timeout: int = 30, selector: str = None) -> str:
    """爬取网页 URL 并转换为完整 Markdown。

    支持 requests 直连（默认）和 cloudscraper（Cloudflare 回退）。
    支持通过 CSS selector 限定提取范围（回退方案）。
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }

    # 尝试 cloudscraper（应对 Cloudflare）
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper()
    except ImportError:
        scraper = requests

    resp = scraper.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"

    if selector:
        # 回退方案：用 bs4 提取指定容器
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        container = soup.select_one(selector) or soup.find("body")
        html_source = str(container)
    else:
        html_source = resp.text

    h = HTML2Text()
    h.body_width = 0          # 不自动折行
    h.ignore_links = False
    h.ignore_images = False
    h.images_to_alt = True
    h.mark_code = True

    return h.handle(html_source)


def probe_structure(url: str, timeout: int = 15) -> str:
    """快速探测页面结构，返回建议的 CSS selector。"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")

    candidates = []
    for sel in ["article", "main", ".markdown-body", ".post-content", ".entry-content", ".content"]:
        el = soup.select_one(sel)
        if el:
            text_len = len(el.get_text(strip=True))
            candidates.append((sel, text_len))

    if not candidates:
        # 找含文本最多的 div 容器
        divs = soup.find_all("div", class_=True)
        if divs:
            best = max(divs, key=lambda d: len(d.get_text(strip=True)))
            candidates.append((f".{'.'.join(best.get('class', []))}", len(best.get_text(strip=True))))

    candidates.sort(key=lambda x: -x[1])
    return candidates[0][0] if candidates else "body"


def main():
    parser = argparse.ArgumentParser(description="通用网页内容抓取工具")
    parser.add_argument("url", help="要抓取的网页 URL")
    parser.add_argument("--selector", "-s", help="CSS selector 限定提取范围")
    parser.add_argument("--probe", "-p", action="store_true", help="先探测页面结构，输出建议的 selector")
    parser.add_argument("--output", "-o", help="输出到文件（默认 stdout）")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="超时秒数")

    args = parser.parse_args()

    if args.probe:
        sel = probe_structure(args.url, args.timeout)
        print(sel)
        print(f"建议 selector: {sel}", file=sys.stderr)
        sys.exit(0)

    print(f"[fetch_url] 正在抓取: {args.url}", file=sys.stderr)
    try:
        markdown = fetch_url_to_markdown(args.url, args.timeout, args.selector)
    except requests.exceptions.HTTPError as e:
        if "403" in str(e):
            print(f"[fetch_url] 403 错误，尝试 cloudscraper 绕过...", file=sys.stderr)
            try:
                import cloudscraper
                markdown = fetch_url_to_markdown(args.url, args.timeout, args.selector)
            except ImportError:
                print(f"[fetch_url] cloudscraper 未安装，请执行: pip install cloudscraper", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"[fetch_url] HTTP 错误: {e}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[fetch_url] 失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 用一个分隔线标记正文开始（去掉 html2text 的标题噪音）
    lines = markdown.split("\n")
    # 找到第一个空行后的内容作为正文
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "" and i > 0:
            body_start = i
            break

    output = "\n".join(lines[body_start:]).strip()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[fetch_url] 已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
