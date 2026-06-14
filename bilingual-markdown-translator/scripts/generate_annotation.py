#!/usr/bin/env python3
"""
标注块 HTML 生成器 —— 适用于 bilingual-markdown-translator skill。

功能：
- 输入结构化 JSON（层级/翻译对照），输出完整的标注块 HTML
- 自动处理：长标题独立行、多列 flex 布局、bold/normal 层级、div 平衡
- 支持单张图片或多张图片批量输出

用法：
  cat annotation.json | python generate_annotation.py
  python generate_annotation.py annotation.json       # 从文件读
  python generate_annotation.py                        # 从 stdin 读

输入 JSON 格式：

  {
    "annotations": [
      {
        "title": ["The limits of agent knowledge", "Agent 知识的边界"],
        "columns": [
          [
            {"en": "CODEX", "cn": "CODEX", "bold": true},
            {"en": "Google doc", "cn": "Google 文档"}
          ],
          [
            {"en": "Slack message", "cn": "Slack 消息", "bold": true},
            {"en": "Tacit knowledge", "cn": "隐性知识"}
          ]
        ]
      }
    ]
  }

字段说明：
- annotations: 数组，每项对应一张图片的标注块
  - title (可选): [英文, 中文]。>5个英文单词时自动独立一行
  - columns: 列数组，每列是一个 item 数组
    - en: 英文标签
    - cn: 中文翻译
    - bold (可选, 默认 false): 灰底内是否加粗

输出：多个标注块 HTML，用 <!-- divider --> 注释分隔，可直接粘贴到 md 文件。

HTML 规范：
- 字号 0.7em，行高 1.5
- 灰底 #f0f0f0，圆角 4px
- 行间距 gap:6px，列间距 gap:24px
- 每行 flex + gap:12px + align-items:baseline
- 中文 <strong> 加粗
- 所有 div 闭合平衡
"""

import json
import sys


def render_item(item: dict) -> str:
    """渲染单行条目。"""
    en = item["en"]
    cn = item["cn"]
    bold = item.get("bold", False)

    if bold:
        en_tag = f'<span style="background:#f0f0f0;padding:2px 6px;border-radius:4px;white-space:nowrap;"><strong>{en}</strong></span>'
    else:
        en_tag = f'<span style="background:#f0f0f0;padding:2px 6px;border-radius:4px;white-space:nowrap;">{en}</span>'

    return f'      <div style="display:flex;gap:12px;align-items:baseline;">\n        {en_tag}\n        <strong>{cn}</strong>\n      </div>'


def render_column(items: list) -> str:
    """渲染一列。"""
    item_htmls = "\n".join(render_item(it) for it in items)
    return f'    <div style="flex:1;display:flex;flex-direction:column;gap:6px;">\n{item_htmls}\n    </div>'


def render_annotation(anno: dict) -> str:
    """渲染一张图片的完整标注块。"""
    title = anno.get("title")
    columns = anno.get("columns", [])

    parts = ['<div style="font-size:0.7em;line-height:1.5;">']

    # 长标题：独立一行
    if title:
        en_title, cn_title = title[0], title[1]
        parts.append('  <!-- 长标题 -->')
        parts.append(f'  <div style="margin-bottom:8px;">')
        parts.append(f'    <span style="background:#f0f0f0;padding:2px 6px;border-radius:4px;">{en_title}</span> <strong>{cn_title}</strong>')
        parts.append(f'  </div>')

    # 短条目：多列
    if columns:
        parts.append('  <!-- 条目列 -->')
        parts.append('  <div style="display:flex;gap:24px;">')
        for col in columns:
            parts.append(render_column(col))
        parts.append('  </div>')

    parts.append('</div>')
    return "\n".join(parts)


def main():
    # 读取输入
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    # 支持直接传 annotations 数组或嵌套对象
    if "annotations" in data:
        annotations = data["annotations"]
    elif isinstance(data, list):
        annotations = data
    else:
        annotations = [data]

    # 生成 HTML
    outputs = []
    for i, anno in enumerate(annotations):
        html = render_annotation(anno)
        outputs.append(html)

    sys.stdout.write("\n\n<!-- divider -->\n\n".join(outputs))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
