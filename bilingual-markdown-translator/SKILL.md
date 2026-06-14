---
name: bilingual-markdown-translator
title: "双语逐段对照翻译（通用场景）"
description: "将任意来源的外语 Markdown 文档翻译为逐段对照的双语版本（源语言自动识别，目标语言固定为中文），自动处理图片下载与路径适配，支持可选的图片 OCR 翻译。支持本地文件、GitHub 仓库、网络 URL 等多种来源。当用户需要将技术文档、博客文章、README、或任何外文 Markdown 内容翻译为中文时，务必使用本 skill。"
agent_created: true
version: "5.2"
tags: ["translation", "markdown", "chinese", "bilingual", "github", "images", "ocr"]
---

# 双语逐段对照翻译（通用场景）

将任意来源的外语 Markdown 文档翻译为逐段对照的双语版本（源语言自动识别，目标语言固定为中文），自动处理图片获取与路径适配，支持可选的图片 OCR 翻译。

## 内置脚本

本 skill 的脚本位于 `scripts/` 目录。所有可复用的操作都应调用已有脚本，严禁现场新建 .py 文件：

> **环境要求**：Python 3.10+，依赖见 `scripts/requirements.txt`。
>
> **首次使用**：运行 `python scripts/setup.py` 自动创建独立虚拟环境。
> 也可以手动安装：`pip install -r scripts/requirements.txt`。
>
> 本 skill 使用两个占位符：
> - `<PYTHON>` — Python 可执行文件路径（setup 后为 `scripts/.venv/Scripts/python.exe`）
> - `<SKILL_DIR>` — skill 根目录（与 `SKILL.md` 同级）

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `scripts/run_ocr.py` | 对图片执行双方向 OCR 提取文字 | `<PYTHON> <SKILL_DIR>/scripts/run_ocr.py <image_path> [image_path ...]` |
| `scripts/generate_annotation.py` | 从结构化 JSON 生成标注块 HTML | `<PYTHON> <SKILL_DIR>/scripts/generate_annotation.py < input.json` |
| `scripts/fetch_url.py` | 将网页 URL 抓取并转为 Markdown | `<PYTHON> <SKILL_DIR>/scripts/fetch_url.py <url> [--selector ...]` |
| `scripts/requirements.txt` | 全部依赖清单 | `<PYTHON> -m pip install -r <SKILL_DIR>/scripts/requirements.txt` |

## 参考文档

| 文件 | 内容 |
|------|------|
| `references/format-examples.md` | 各章节的完整格式示例（标题/图片/列表/表格/JSON 标注） |
| `references/troubleshooting.md` | 常见问题与踩坑记录（爬虫/OCR/渲染兼容性） |

## 适用场景

| 场景 | 源文件来源 | 图片来源 | 处理方式 |
|------|-----------|----------|----------|
| A | 本地 .md 文件 | 本地 img/ 目录 | 直接翻译，调整图片路径 |
| B | GitHub 仓库 content/ 目录 | GitHub raw 图片 URL | WebFetch 列表 + curl 原文 + 下载图片 |
| C | 任意网络 URL | 网络图片 URL | scripts/fetch_url.py 爬取 + 下载图片 |
| D | 本地 .md 文件 | 网络图片 URL | 下载远程图片，转换引用 |

## 可选功能：图片标注翻译

默认启用。如果用户明确指定**不翻译图片**或**只翻译文本**，则跳过图片翻译步骤。

- 默认：翻译正文 + 所有图片标注
- 指令 "不翻译图片" / "只翻译文本" → 只翻译正文，跳过图片

---

## 阶段一：资源准备

### 1.1 确定输出目录

创建目标目录结构：
```
<output-dir>/
├── README.md          ← 索引导航页
├── content/           ← 翻译后的 md 文件
└── img/
    └── <article-slug>/ ← 每篇文章独立子目录，避免跨文章图片命名冲突
```

子目录命名规则：`<作者或来源>-<年月>`，例如 `vivek-trivedi-2026.03`、`openai-2026.02`。

### 1.2 获取源文件内容

**本地文件**：
- 直接 Read 读取

**GitHub 仓库**：
- 页面文件列表：WebFetch 获取 README 了解项目结构
- 原文 .md 内容：`curl` 到 raw URL 直接下载（比 WebFetch 更可靠、完整）

  ```
  # 获取文件列表
  WebFetch https://github.com/<owner>/<repo>/tree/main/content/

  # 下载具体文件
  curl -L -o "<output-dir>/content/<filename>" "https://raw.githubusercontent.com/<owner>/<repo>/main/<path>"
  ```

**网络 URL**：
- 始终使用 `scripts/fetch_url.py` 程序化爬取（`WebFetch` 会截断/摘要内容，不够完整）：

```bash
# 安装依赖（首次使用，幂等可重复）
<PYTHON> -m pip install -r "<SKILL_DIR>/scripts/requirements.txt"

# 基本用法：爬取 URL 并输出 Markdown
<PYTHON> "<SKILL_DIR>/scripts/fetch_url.py" "<url>"

# 指定 CSS selector（页面结构复杂时）
<PYTHON> "<SKILL_DIR>/scripts/fetch_url.py" "<url>" --selector "article"

# 先探测页面结构（获取建议的 CSS selector）
<PYTHON> "<SKILL_DIR>/scripts/fetch_url.py" "<url>" --probe

# 保存到文件
<PYTHON> "<SKILL_DIR>/scripts/fetch_url.py" "<url>" --output content/article.md
```

- 常见网络问题见 `references/troubleshooting.md`（Cloudflare 绕过、页面结构探测等）

### 1.3 获取图片

**场景判断表格**：

| 图片链接格式 | 处理方式 |
|-------------|----------|
| GitHub blob URL: `https://github.com/.../img/xxx.png` | 转换为 `https://raw.githubusercontent.com/.../img/xxx.png` 后下载 |
| GitHub raw URL: `https://raw.githubusercontent.com/.../img/xxx.png` | 直接下载 |
| 其他 HTTP/HTTPS URL | 直接用 curl 下载 |
| 本地相对路径: `./img/xxx.png` | 已在本地，无需下载 |

**下载方式**：
```bash
curl -L -o "<output-dir>/img/<filename>" "<remote-url>"
```

### 1.4 路径转换规则

翻译后的文档中，图片统一使用**相对于 md 文件的相对路径**，并按文章分入子目录：

| md 文件位置 | 图片引用格式 |
|------------|-------------|
| `content/<md-file>.md` | `../img/<article-slug>/xxx.png` |
| 根目录 README.md | `./img/<article-slug>/xxx.png` |

将原文中的各种图片链接统一替换：
- GitHub blob URL → `../img/<article-slug>/xxx.png`
- GitHub raw URL → `../img/<article-slug>/xxx.png`
- 绝对 URL → `../img/<article-slug>/xxx.png`
- `./img/xxx.png` → `../img/<article-slug>/xxx.png`（如果输出到 content/ 子目录）

---

## 阶段二：翻译规则

逐段对照翻译，严格遵循以下规则：

### 2.0 源语言自动识别

- 无需手动指定源语言
- 自动检测文本语种（英文/日文/韩文/法文/俄文等），原文段落保持源语言
- 所有翻译段落**统一输出为中文**
- 专有名词、品牌名、代码标识符保留原文不翻译

### 2.1 段落切分
- 以**回车空行**作为段落边界
- 每个原文段落后紧跟中文翻译段落

### 2.2 标题对照（必须翻译标题内容）

格式示例见 `references/format-examples.md`（2.2 节）。

注意：中文标题行**不能**只把英文引号换成中文书名号，必须实际翻译标题内容。

### 2.3 图片处理
- 图片 `![...](../img/xxx.png)` 放在中文翻译段落**之后**，不允许插在原文与翻译之间
- **原文段落与中文翻译段落必须紧邻**（铁律），中间不能插入任何图片、引用块或其它元素
- 中文部分**删除**重复的图片引用
- 图片下方的描述文字如果是正文段落，应作为**独立段落**翻译（原文 + 中文对照），而不是只塞进 alt text
- 图片 alt 文本保留原文不翻译，用于无障碍描述

结构示例见 `references/format-examples.md`（2.3 节）。

### 2.4 代码块处理
- 代码块只出现一次（紧跟英文段落）
- 中文翻译段落**不重复**代码块
- 代码块内的英文 `# comment` 行下方，加一行 `# 中文注释翻译`
- JSON/YAML 数据内容不翻译，只翻译外层自然语言说明

### 2.5 引用块逐条对照

格式示例见 `references/format-examples.md`（2.5 节）。

### 2.6 列表作为整段翻译（最重要规则之一）

**列表项不逐条穿插对照**，而是将整个列表视为一个段落块：

- 所有英文列表项**整体输出**，整体放在一个引用块 `>` 内，使用真实 Markdown 列表语法
- 中文翻译列表项**整体输出**，保持普通 Markdown 列表格式

格式示例见 `references/format-examples.md`（2.6 节），包含无序列表和有序列表的完整对照。

注意：
- 原文列表：`-` / `1.` 在 `<span>` **外面**，渲染器识别为真实列表；内容在 `<span>` 内，文字灰显
- 中文列表项使用普通 Markdown 列表，无 `>` 无 `<span>`，默认黑色
- 保持列表原有的缩进层级（嵌套子项同理整组输出）
- 数字列表**保持原文的数字序列**

### 2.7 技术术语
- 专有名词保留原文或中英并用：LLM、DAG、RAG、Agent
- 产品/API 名称不翻译：Airflow、Stripe、Slack

### 2.8 颜色与引用块双保险（阅读体验优化）

为了跨渲染器兼容，采用**引用块 `>` + 灰色 `<span>` 颜色**双保险方案：

- 原文段落：用 `> <span style="color: #999;">` 包裹，左侧竖线 + 浅灰色双重后退
- 中文翻译段落：无前缀无颜色，使用 Markdown 默认样式，自然成为视觉重心
- 标题（heading）不做格式区分，保持原有样式
- 引用块内的原文仍用 `<span style="color: #999;">` 包裹灰色

注意：
- **只有纯文本段落才加 `>` + span**，代码块、图片引用、表格不做处理
- 行内代码 `` `code` `` 如果出现在原文段落内，随外层变为浅色，这是预期的行为
- 表格内的原文段落保持 `<span style="color: #999;">` 但不加 `>`（表格不支持引用块语法）
- 中文段落永远不加 `>` 前缀，确保黑白两色对比鲜明

渲染效果：原文左侧有竖线 + 灰色文字 → 视觉上自动后退，中文段落无前缀 + 默认黑色 → 阅读时自动聚焦。具体效果示例见 `references/format-examples.md`（2.8 节）。

### 2.9 表格翻译（单元格级双语）

表格不在表级别分中英两份，而是在**每个单元格内**同时保留原文和中文翻译，用换行 `<br>` 分隔。

要求：
- 每个单元格内的原文用 `<span style="color: #999;">` 包裹，中文保持默认颜色
- `<br>` 放在 span 闭合之后，即：`<span style="color: #999;">原文</span><br>翻译`

完整示例见 `references/format-examples.md`（2.9 节）。

注意：
- 表头行：原文在上，中文在下
- 数据行：原文在上，中文在下
- 表格不做颜色处理（span 不作用在表格内容上）
- 如果原文是代码或纯标识符（如 `passes: false`），只在中文行翻译外层的自然语言描述

### 2.10 其他
- **不用 `---` 分隔线**
- **完整翻译**，不省略内容
- **不自行发挥**，不添加原文没有的信息

### 2.11 图片标注翻译（可选，默认启用）

正文翻译完成后，对每张图片执行 OCR 提取 → 翻译 → 生成标注块。

> **💡 性能要点**：下文所有步骤都按**批处理**设计。一次 OCR 跑完所有图、一次翻译所有条目、一次写文件。不要一张图一张图地串行做——串行每张图都要加载一次 EasyOCR 模型（浪费 ~15秒/张）。

#### 2.11.1 OCR 提取（批量）

step 1 — 将 **所有图片路径** 一次性传入脚本，一次批处理全部图片：

```bash
# ✅ 正确：一次批处理全部图片（模型只加载一次）
<PYTHON> "<SKILL_DIR>/scripts/run_ocr.py" <img1> <img2> <img3> ... > ocr_result.json 2>/dev/null

# ❌ 错误：逐张跑 —— 每张图都要加载 EasyOCR 模型（浪费 ~15秒/张）
```

其中：
- `<PYTHON>` — 见"内置脚本"节的环境说明（首次使用运行 `scripts/setup.py` 自动配置）
- `<SKILL_DIR>` — skill 根目录（`SKILL.md` 所在目录）

输出为一个 JSON 文件，每张图片包含以下字段：
- `all_unique_texts`：去重后的纯文本列表（字符串数组），用于快速浏览
- `all_unique_items`：去重后的完整记录（含文本 `text`、置信度 `conf`、坐标 `bbox`），用于取用
- `items_0deg` / `items_90deg`：原始 OCR 输出（0° 和 90° 方向），极少需要访问

#### 2.11.2 看图确认（批量看，不需要每张图停一次）

step 2 — **一次性读取所有图片**进行"看图确认"，补充 OCR 遗漏的文字：

- 并行 Read 所有图片
- 只关注 **每张图上有没有 OCR 明显漏掉的大标题/关键文字**，不需要逐项核对高置信度条目

> 规则不变：OCR 出的每一条都要翻译。看图是为了**发现遗漏**，不是逐项审核。

#### 2.11.3 核心原则：全盘信任 OCR

> 核心规则只有一条：**OCR 检出的每一条文本都要保留并翻译**。不做任何过滤或跳过。
>
> 常见陷阱：置信度低就跳过、看起来重复就合并、文字太小就忽略、注释副标题就不管——这些都不做。<br>
> OCR 输出 + 看图补充 = 完整文字列表。看图永远是为了**发现遗漏**，不是删减已有结果。

#### 2.11.4 层级判断与翻译（批量）

step 3 — **一次翻译所有图片的所有条目**：

通过看图判断层级关系：
- **高级别**（分组标题/阶段名）：灰底内加粗
- **子项**：灰底内普通字体
- **顶级标题**（>5个英文单词）：独立一行，不参与多列

建立结构化的 JSON 对照表作为 `generate_annotation.py` 的输入。JSON 格式见 `references/format-examples.md`（2.11.4 节）。

#### 2.11.5 生成标注块（调用脚本，一次性写文件）

step 4 — **将 JSON 传给 `generate_annotation.py`，拿到 HTML 一次性 Edit 写入 md 文件**。

```bash
# JSON 存在文件里
<PYTHON> "<SKILL_DIR>/scripts/generate_annotation.py" input.json > annotations.html

# 或通过管道传 stdin
echo '<json>' | <PYTHON> "<SKILL_DIR>/scripts/generate_annotation.py"
```

使用 `generate_annotation.py` 生成标注块 HTML——脚本自动处理 flex 布局、div 闭合、字体间距等所有细节。输出是平衡的、可直接粘贴的标注块。

#### 2.11.6 插入位置

标注块紧跟在图片 `![](path)` 行之后，图片与正文之间。

---

## 阶段三：生成 README 索引

在输出根目录生成 `README.md`：
- 列出所有文件的导航表
- 每条包含原文标题 + 中文翻译 + 文件链接
- 标注来源仓库和许可证

---

## 执行顺序总结

```
0. 首次准备 → python scripts/setup.py（创建环境 + 安装依赖）
1. 解析来源 → 判断是本地/GitHub/URL
2. 创建目录 → content/ + img/
3. 获取原文 → Read 本地 / curl GitHub raw / <SKILL_DIR>/scripts/fetch_url.py 网络URL
4. 下载图片 → 识别图片链接类型 → curl 下载 → 统一到 img/
5. 翻译正文 → 逐段对照，转换图片路径为相对路径
6. [可选] 翻译图片标注
   → <PYTHON> <SKILL_DIR>/scripts/run_ocr.py 批量OCR所有图片 → 一次性Read所有图片看图确认
   → 批量翻译所有条目 → <PYTHON> <SKILL_DIR>/scripts/generate_annotation.py 生成 HTML
   → 一次性Edit写入所有标注块
7. 生成 README → 导航索引
8. 交付 → 汇报文件清单
```
