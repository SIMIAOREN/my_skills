# 常见问题与踩坑记录

---

## 网页爬取

### Cloudflare 绕过
某些站点（如 openai.com）使用 Cloudflare 质询，`requests` 直接访问返回 403。
- `fetch_url.py` 会自动尝试 `cloudscraper` 绕过
- 如果失败，确保 `cloudscraper` 已安装（`pip install cloudscraper`）

### 页面结构探测
某些站点（如 martinfowler.com）HTML 结构特殊，通用 selector（`article`, `main`）可能不命中。
- 先用 `--probe` 探测准确的 CSS selector
- 再用 `--selector` 指定探测到的 selector

---

## OCR

### EasyOCR CPU 模式慢
- 无 GPU 时每张图 0° + 90° 两遍 OCR 约 30-60 秒
- **关键优化**：一次传入所有图片路径，模型只加载一次

### OCR 置信度
- 即使置信度低的文字也可能是有意义的，不要跳过
- 看图确认的目的是**发现遗漏**，不是删减已有结果

---

## 标注块 HTML

### div 闭合
标注块的 `<div>` 缺少 `</div>` 会导致后续正文字体变小。
- 已通过 `generate_annotation.py` 脚本自动化解决
- 如果手写，务必检查 div 开闭数量一致

### 渲染兼容
- 使用具体色值 `#f0f0f0`，不要用 CSS 变量（PyCharm 不支持）
- 行间距用 `gap:6px`，不用 `line-height`
- 列间距用 `gap:24px`
