# 格式模板参考

本文件包含 bilingual-markdown-translator 所有翻译格式的完整示例。

---

## 2.2 标题对照

```
# English Title

# 中文标题（不能只保留原文加书名号，必须翻译内容）

### English subtitle

### 中文小标题
```

**注意**：中文标题行不能只把英文引号换成中文书名号，必须实际翻译标题内容。

- ❌ `# 《Effective Harnesses for Long-Running Agents》`
- ✅ `# 《长周期 Agent 的有效 Harness 设计》`

---

## 2.3 图片位置

```
> <span style="color: #999;">English paragraph describing something.</span>

中文段落翻译。

![Alt text for accessibility](../img/xxx.png)

> <span style="color: #999;">Image caption in English (if it was originally a paragraph, not just alt text).</span>

图片说明中文翻译。
```

要求：
- 图片 `![...]` 放在中文翻译段落**之后**，不允许插在原文与翻译之间
- **原文段落与中文翻译段落必须紧邻**（铁律），中间不能插入图片、引用块或其它元素
- 中文部分**删除**重复的图片引用
- 图片下方的描述文字如果是正文段落，应作为**独立段落**翻译
- 图片 alt 文本保留原文不翻译

---

## 2.5 引用块逐条对照

```
> English quote line 1

> 中文引用第1行

> English quote line 2

> 中文引用第2行
```

---

## 2.6 列表作为整段翻译

**列表项不逐条穿插对照**，而是将整个列表视为一个段落块。

### 无序列表

```
> - <span style="color: #999;">System Prompts</span>
> - <span style="color: #999;">Custom Instructions</span>
> - <span style="color: #999;">Working Directory</span>
> - <span style="color: #999;">SOUL.md</span>

- 系统提示词
- 自定义指令
- 工作目录
- SOUL.md
```

### 有序列表

```
> 1. <span style="color: #999;">Navigate to the project directory</span>
> 2. <span style="color: #999;">Run `npm install`</span>
> 3. <span style="color: #999;">Start the development server</span>

1. 导航到项目目录
2. 运行 `npm install`
3. 启动开发服务器
```

**格式要点**：
- 原文列表：`-` / `1.` 在 `<span>` **外面**，渲染器识别为真实列表；内容在 `<span>` 内，文字灰显
- 中文列表项使用普通 Markdown 列表，无 `>` 无 `<span>`，默认黑色
- 保持列表原有的缩进层级
- 数字列表**保持原文的数字序列**

---

## 2.9 表格翻译（单元格级双语）

表格不在表级别分中英两份，而是在**每个单元格内**同时保留原文和中文翻译，用 `<br>` 分隔。

### 格式规范

```
| Column 1 Header | Column 2 Header |
| 列 1 表头 | 列 2 表头 |
| <span style="color: #999;">Original text in cell</span><br>单元格原文翻译 | <span style="color: #999;">Another original text</span><br>另一格原文翻译 |
```

### 完整示例

```
| Problem | Init Agent Behavior |
| 问题 | 初始化 Agent 行为 |
| <span style="color: #999;">Claude prematurely declares the entire project done</span><br>Claude 过早宣布整个项目完成 | <span style="color: #999;">Builds a feature list file</span><br>建立功能列表文件 |
```

**格式要点**：
- 每个单元格内的原文用 `<span style="color: #999;">` 包裹，中文保持默认颜色
- `<br>` 放在 span 闭合之后：`<span style="color: #999;">原文</span><br>翻译`
- 表头行：原文在上，中文在下
- 数据行：原文在上，中文在下
- 表格不做颜色处理（span 不作用在表格内容上）
- 如果原文是代码或纯标识符（如 `passes: false`），只在中文行翻译外层的自然语言描述

---

## 2.11.4 标注 JSON 输入格式

`generate_annotation.py` 接受的 JSON 结构：

```json
{
  "annotations": [
    {
      "title": ["The limits of agent knowledge", "Agent 知识的边界"],
      "columns": [
        [{"en": "CODEX", "cn": "CODEX", "bold": true},
         {"en": "Google doc", "cn": "Google 文档"}],
        [{"en": "Slack message", "cn": "Slack 消息", "bold": true},
         {"en": "Tacit knowledge", "cn": "隐性知识"}]
      ]
    },
    {
      "title": ["The Observability Stack", "可观测性栈"],
      "columns": []
    }
  ]
}
```

字段说明：
- `annotations`：数组，每项对应一张图片
  - `title`（可选）：[英文, 中文]；>5 个英文单词自动独立一行
  - `columns`：列数组，每列是 item 数组
    - `en`：英文标签
    - `cn`：中文翻译
    - `bold`（可选，默认 false）：高级别加粗

---

## 2.8 颜色效果示例

```
> <span style="color: #999;">One of the most common patterns in agent building is to convert natural language to structured tool calls.</span>

在构建 Agent 时，最常见的模式之一是将自然语言转换为结构化的工具调用。
```

渲染效果：
- 原文左侧有竖线 + 灰色文字 → 视觉上双重后退
- 中文段落无前缀 + 默认黑色 → 阅读时自然聚焦
