# 论文中文化流水线：从源 PDF 到可校对中文阅读版

这是一个面向科研阅读的开放工程：把两篇 arXiv 论文从源 PDF 转成带页码坐标的 Markdown，生成中文阅读版 PDF，并留下可复核的 QA 证据。

它的核心卖点不是“把英文换成中文”这么简单，而是把一次性翻译变成可追溯、可检索、可复现的研究资料管线：

> **PDF → 原文转录 → 中文翻译 → 中文 PDF → 页级回溯 → 结构/文本/视觉 QA**

## 为什么值得复用

- **页级可逆校对**：源文、译文和中英对照共享“原文第 N 页”坐标；看到一个公式或结论，可以直接回到源 PDF。
- **双形态交付**：Markdown 适合 `rg`、版本管理和局部修订；PDF 适合连续阅读，并保留可检索文本。
- **学术对象不乱翻**：公式、变量、算法名、模型名、数据集名、引用键和代码标识尽量原样保留。
- **中文字体与缺字处理**：使用 macOS CJK 字体和 Unicode 数学回退字体，代码长行自动换行，减少方框、裁切和重叠。
- **证据化 QA**：记录页数、页标记集合、公式/代码块统计，并用 `pdfinfo`、`pdftotext`、`pdftoppm` 做结构、文本和视觉抽样检查。
- **长文分块策略**：319 页论文采用分块翻译与合并，明确记录不同翻译引擎和页段，不把混合稿伪装成统一人工译本。

## 收录论文

| arXiv | 论文 | 源页数 | 当前状态 |
|---|---|---:|---|
| [2607.15524](https://arxiv.org/abs/2607.15524) | *Recursive Harness Self-Improvement* | 88 | 中文译文、中英逐页对照；88/88 页标记一致 |
| [2607.17560](https://arxiv.org/abs/2607.17560) | *Reinforcement Learning: From Algorithms To Foundation Models* | 319 | 混合机器译稿：1--64 页 Google，65--289 页摘录翻译，290--319 页参考文献保留英文 |

## 直接阅读与复核

- [15524 中文阅读版 PDF](./pdf/2607.15524v1_中文阅读版.pdf) · [中文译文 Markdown](./15524/2607.15524v1_zh.md) · [中英逐页对照](./15524/2607.15524v1_bilingual.md)
- [17560 中文阅读版 PDF](./pdf/2607.17560v1_中文阅读版.pdf) · [混合中文稿 Markdown](./17560/2607.17560v1_zh_hybrid.md) · [源 Markdown](./17560/2607.17560v1_source.md)
- [个人站点项目介绍](https://chaoyu-fan.github.io/blogs/paper-translation-2607/)

## 目录

```text
research/paper-translation-2607/
├── README.md
├── NOTICE.md                         # 版权、许可与使用边界
├── .gitignore                        # 本地源 PDF 与中间产物不入库
├── 15524/
│   ├── 2607.15524v1_source.md       # 英文结构化转录
│   ├── 2607.15524v1_source_raw.txt  # 原始 pdftotext 文本
│   ├── 2607.15524v1_zh.md            # 中文译文
│   ├── 2607.15524v1_bilingual.md     # 中英逐页对照
│   ├── 2607.15524v1_translation_QA.md
│   └── 2607.15524v1_translation_stats.json
├── 17560/
│   ├── 2607.17560v1_source.md
│   ├── 2607.17560v1_source.txt
│   ├── 2607.17560v1_zh_hybrid.md     # 推荐阅读稿
│   ├── 2607.17560v1_zh_machine_safe.md
│   └── 2607.17560v1_translation_QA.md
├── pdf/
│   ├── 2607.15524v1_中文阅读版.pdf
│   └── 2607.17560v1_中文阅读版.pdf
└── tools/
    ├── pdf_to_markdown.py
    ├── markdown_to_pdf.py
    ├── build_reading_pdf.py
    └── requirements.txt
```

源 PDF 不随仓库分发：请从上表的 arXiv 页面下载到本地，并按 `NOTICE.md` 检查再分发许可。这样可以避免把第三方源文件误纳入个人站点的 MIT 许可范围，也避免大文件拖慢网站仓库。

## 快速开始

在本目录执行：

```bash
python3 -m pip install -r tools/requirements.txt

# 1. 下载原 PDF 到 sources/（目录已被 .gitignore 排除）
mkdir -p sources
curl -L https://arxiv.org/pdf/2607.15524 -o sources/2607.15524v1.pdf
curl -L https://arxiv.org/pdf/2607.17560 -o sources/2607.17560v1.pdf

# 2. PDF -> 原始文本 -> 逐页结构化 Markdown
pdftotext -layout sources/2607.15524v1.pdf sources/2607.15524v1_source.txt
python3 tools/pdf_to_markdown.py \
  sources/2607.15524v1_source.txt 15524/2607.15524v1_source.md

# 3. 生成中文阅读 PDF（15524）
python3 tools/markdown_to_pdf.py \
  15524/2607.15524v1_zh.md pdf/2607.15524v1_中文阅读版.pdf \
  --title '递归式 Harness 自改进（中文阅读版）'

# 4. 生成中文阅读 PDF（17560，默认使用混合中文稿）
python3 tools/build_reading_pdf.py
```

生成后建议执行：

```bash
pdfinfo pdf/2607.15524v1_中文阅读版.pdf
pdftotext -layout pdf/2607.15524v1_中文阅读版.pdf /tmp/15524.txt
pdftoppm -f 1 -l 3 -png -r 120 pdf/2607.15524v1_中文阅读版.pdf /tmp/15524-page
```

## 校对方法

1. 在中文 PDF 中搜索“原文第 N 页”。
2. 打开同编号的 `*_source.md` 或 arXiv 原 PDF。
3. 优先复核公式、算法伪代码、表格数字、图内标签、引用和专有名词。
4. 将修改回写到对应 Markdown，再重新生成 PDF，并更新 QA 记录。

## 重要限制

- 这是中文阅读辅助材料，不是作者、出版社或 arXiv 官方译本。
- 15524 的图表主要来自文本抽取，未做逐图视觉重绘。
- 17560 的公式来自 `pdftotext` 转录，290--319 页参考文献保留英文；混合译文尚未完成逐句人工学术校对。
- 机器翻译可能存在术语、公式和上下文错误；正式引用、教学或发表前必须回看英文源 PDF。

## 贡献方式

欢迎提交针对具体页码的修订：请在 Issue 或 PR 中注明论文 ID、原文页码、原文片段、修改理由和验证方式。不要提交 API 密钥、个人路径、未获授权的源 PDF 或其他受限材料。
