#!/usr/bin/env python3
"""
通用 OCR 提取脚本 —— 适用于 bilingual-markdown-translator skill。

功能：
- 对任意图片运行 EasyOCR 双方向提取（0° + 90° 旋转）
- 支持单张图片或批量处理
- 输出结构化 JSON，每项包含文本、置信度、坐标

用法：
  python run_ocr.py <image_path> [image_path ...]
  python run_ocr.py <image_path> --save-json   # 额外保存 .ocr.json 到同目录

输出格式（JSON）：
  {
    "images": {
      "<filename>": {
        "items_0deg": [{"text": "...", "conf": 0.99, "bbox": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]}],
        "items_90deg": [...],
        "all_unique_texts": ["item1", "item2", ...],
        "all_unique_items": [{"text": "...", "conf": 0.99}, ...]
      }
    }
  }
"""

import sys
import json
import os
from itertools import groupby

# ---------- OCR engine ----------

def _get_reader():
    """延迟初始化 EasyOCR reader（首次调用时创建）。"""
    import easyocr
    return easyocr.Reader(["en", "ch_sim"], gpu=False)

def rotate_img_90(img):
    """将图片顺时针旋转 90°。"""
    from PIL import Image
    return img.rotate(-90, expand=True)

def run_ocr(image_path: str) -> dict:
    """对单张图片执行双方向 OCR，返回结构化结果。"""
    reader = _get_reader()

    # 0° 方向
    items_0deg = reader.readtext(image_path)
    parsed_0 = [
        {"text": item[1], "conf": round(float(item[2]), 4), "bbox": item[0]}
        for item in items_0deg
    ]

    # 90° 方向（旋转后再识别）
    from PIL import Image
    img = Image.open(image_path).convert("RGB")
    img_rotated = rotate_img_90(img)

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        img_rotated.save(tmp_path)

    items_90deg = reader.readtext(tmp_path)
    os.unlink(tmp_path)

    # 修正坐标：顺时针旋转90°后的坐标还原到原图
    # 旋转后宽高互换，坐标 (x,y) → (orig_h - y, x)
    w, h = img.size
    fixed_90 = []
    for item in items_90deg:
        fixed_bbox = [[h - pt[1], pt[0]] for pt in item[0]]
        fixed_90.append({
            "text": item[1],
            "conf": round(float(item[2]), 4),
            "bbox": fixed_bbox
        })

    # 合并去重（按文本去重，保留置信度最高的）
    all_items = parsed_0 + fixed_90
    all_items.sort(key=lambda x: x["text"])
    merged = []
    for text, group in groupby(all_items, key=lambda x: x["text"]):
        items = list(group)
        best = max(items, key=lambda x: x["conf"])
        merged.append(best)

    return {
        "items_0deg": parsed_0,
        "items_90deg": fixed_90,
        "all_unique_items": merged,
        "all_unique_texts": [item["text"] for item in merged],
    }


# ---------- CLI ----------

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    save_json = "--save-json" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]

    result = {"images": {}}

    for path in paths:
        if not os.path.isfile(path):
            print(f"[WARN] 文件不存在，跳过: {path}", file=sys.stderr)
            continue
        print(f"[OCR] 正在处理: {path}", file=sys.stderr)
        try:
            data = run_ocr(path)
            fname = os.path.basename(path)
            result["images"][fname] = data

            print(f"[OCR] 完成: {fname} — 识别到 {len(data['all_unique_texts'])} 个文本项",
                  file=sys.stderr)
            for item in data["all_unique_items"]:
                print(f"       [{item['conf']:.2f}] {item['text']}", file=sys.stderr)

            if save_json:
                json_path = path + ".ocr.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump({fname: data}, f, ensure_ascii=False, indent=2)
                print(f"[OCR] 已保存 JSON: {json_path}", file=sys.stderr)

        except Exception as e:
            print(f"[ERROR] {path}: {e}", file=sys.stderr)

    # stdout 只输出 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
