---
layout: page
permalink: /blogs/paper-translation-2607/index.html
title: 论文中文化流水线：从源 PDF 到可校对中文阅读版
description: 将 arXiv 论文转成带页级坐标的 Markdown、中文阅读版 PDF 和可复核 QA 记录，公开两篇 2607 论文的完整工程资料。
---

## 论文中文化流水线：从源 PDF 到可校对中文阅读版

把一篇论文“翻成中文”并不难，难的是让译文仍然能够被研究者验证、检索和持续修订。这个项目公开了一条完整的科研阅读流水线：

```text
PDF → 原始文本 → 页级 Markdown → 中文翻译 → 中文 PDF → 源文件回溯 → QA
```

项目目录：[`research/paper-translation-2607`](https://github.com/chaoyu-fan/chaoyu-fan.github.io/tree/main/research/paper-translation-2607)

### 这套工程真正解决了什么

- **可逆校对**：源文、中文译文和中英对照共享“原文第 N 页”坐标，公式、算法和表格可以直接回溯。
- **双形态阅读**：Markdown 便于搜索、版本管理和局部修订；PDF 便于连续阅读，并保留可检索文本。
- **对象保真**：变量、LaTeX 符号、模型名、数据集名、引用键和代码标识尽量不被翻译器改坏。
- **排版可验证**：针对 CJK 字体、数学符号和长代码行做回退与换行，并用 `pdfinfo`、`pdftotext`、`pdftoppm` 留下检查证据。
- **长文可管理**：319 页论文按页段分块翻译，明确记录不同译文来源，不把混合机器稿包装成人工定稿。

### 当前交付

| 论文 | 交付状态 |
|---|---|
| [Recursive Harness Self-Improvement](https://arxiv.org/abs/2607.15524) | 88 页中文译文；源文、译文和中英对照页标记一致；包含公式、附录和代码样式内容。 |
| [Reinforcement Learning: From Algorithms To Foundation Models](https://arxiv.org/abs/2607.17560) | 319 页页级结构化资料；中文混合阅读稿；参考文献页保留英文。 |

### 如何使用

先打开项目中的中文 PDF，搜索“原文第 N 页”定位，再打开同目录的 `*_source.md` 或 arXiv 原文逐页核对。项目 README、QA 记录、统计 JSON 和 PDF 生成工具都随仓库提供。

### 诚实的边界

这不是作者或出版社的官方译本。图表没有逐图重绘，部分公式依赖 PDF 文本抽取；第二篇论文仍是机器/混合译稿，需要人工学术校对。源 PDF 不随仓库分发，版权与再分发权限以原作者和 arXiv 页面为准。
