---
layout: page
permalink: /blogs/terminal-bench-2/index.html
title: Terminal-Bench 2.0 完全导读
description: 从评分方式、89 个任务分类到 agent 提分路径，系统拆解 Terminal-Bench 2.0 到底在测什么，以及该怎么用它评估自己的 coding agent。
---

## Terminal-Bench 2.0 完全导读

> 更新时间：2026/04/12  
> 文章定位：技术基准拆解与 agent engineering 实战笔记。

如果你正在做类似 Codex、Claude Code、Aider、OpenHands 这一类可以直接操作终端的 coding agent，那么 **Terminal-Bench 2.0** 基本已经变成绕不过去的一套 benchmark。

它最值得重视的地方，不是“题很多”，也不是“榜单很热”，而是它测的不是局部代码补全，而是一个 agent 能不能在真实终端环境里完成完整工作流：先探索环境，再理解任务，再调用工具、修代码、跑服务、验证结果，最后把产物正确交付出去。

这篇文章想把四件事讲清楚：

- Terminal-Bench 到底是什么，和常见 coding benchmark 有什么根本区别？
- 每道题通常在测什么，分数又是怎么来的？
- Terminal-Bench 2.0 的 89 个任务，分别偏向哪些能力？
- 如果你在做自己的 coding agent，最该优先优化什么？

<div class="blk-v2">
  <div class="sh-v2">先给结论</div>
  <div class="ri-grid">
    <div class="ri-card c-blue">
      <div class="ri-title">它不是 89 道刷题</div>
      <p>它更像 89 个缩微版真实工作流：部署、调试、训练、恢复、分析、交付，很多题的重点甚至不在“写代码”。</p>
    </div>
    <div class="ri-card c-violet">
      <div class="ri-title">核心看的是任务解决率</div>
      <p>官方榜单关注最终任务是否完成；单题内部可能是正确率、延迟、文件格式、端口状态、模型大小等更细指标。</p>
    </div>
    <div class="ri-card c-teal">
      <div class="ri-title">高分靠 agent 工程</div>
      <p>只换更强模型通常不够。更可靠的无头 CLI、更强的环境发现、更严格的自验证循环，往往更直接涨分。</p>
    </div>
  </div>
</div>

<style>
.tb-lead p{color:#3d5060;line-height:1.8}
.tb-table{width:100%;border-collapse:collapse;margin:1rem 0 1.2rem;font-size:.96rem}
.tb-table th,.tb-table td{border-bottom:1px solid #dde4ea;padding:.75rem .55rem;text-align:left;vertical-align:top}
.tb-table th{color:#405361}
.tb-note{color:#596977;font-size:.92rem;line-height:1.75}
.tb-callout{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1rem .9rem;border-radius:10px;margin:1rem 0}
.tb-card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.25rem}
.tb-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem 1rem .9rem}
.tb-card h3{margin:.1rem 0 .5rem;font-size:1rem;line-height:1.45;color:#304552}
.tb-card p{margin:0;color:#556674;font-size:.92rem;line-height:1.72}
.tb-task-group{margin:1.1rem 0 1.35rem}
.tb-task-group h4{margin:0 0 .7rem;color:#2f4756}
.tb-task-group ul{margin:.3rem 0 0 1.1rem}
.tb-task-group li{margin:.38rem 0;line-height:1.72;color:#42586a}
.tb-task-group code{font-size:.92em}
.tb-mini{font-size:.9rem;color:#61707d}
@media (max-width: 720px){
  .tb-card-grid{grid-template-columns:1fr}
}
</style>

<div class="blk-v2 tb-lead">
  <div class="sh-v2">Terminal-Bench 到底是什么？</div>
  <p><strong>一句话概括：</strong>它是“终端里的真实任务 benchmark”，不是“编辑器里的局部代码题 benchmark”。</p>
  <p>从官方 benchmark 页面、Harbor 文档和任务结构来看，一道 Terminal-Bench 题通常包含任务说明、可运行环境、自动 verifier、oracle / reference solution，以及时间与资源限制。真正被检查的不是你中间说了什么，而是最终容器状态有没有满足验收条件。</p>
  <p>这就是它和常见代码 benchmark 最大的差别。很多 benchmark 更像是在问“你会不会补这一段代码”，而 Terminal-Bench 更像是在问“你能不能像一个靠谱工程师一样，在终端里把事情做完”。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">它为什么更难？</div>
  <div class="tb-card-grid">
    <div class="tb-card">
      <h3>环境发现</h3>
      <p>你得先看懂目录、服务、日志、配置、测试脚本和交付路径，很多题的第一步不是写代码，而是找对入口。</p>
    </div>
    <div class="tb-card">
      <h3>多步规划</h3>
      <p>大量题目需要十几步甚至几十步串起来做。中间只要目标漂移、重复操作或漏掉收尾，最后都会被 verifier 记成失败。</p>
    </div>
    <div class="tb-card">
      <h3>调试修复</h3>
      <p>读报错、装依赖、修 lockfile、重启服务、对照测试、迭代修改，这些真实工程动作在这里都是主菜，不是配菜。</p>
    </div>
    <div class="tb-card">
      <h3>终态交付</h3>
      <p>不是“看起来差不多”就行。文件路径、输出格式、端口状态、模型大小、精度阈值，最后都要落到可验证的终态上。</p>
    </div>
  </div>
</div>

<div class="blk-v2">
  <div class="sh-v2">分数怎么看？</div>
  <table class="tb-table">
    <thead>
      <tr>
        <th>指标</th>
        <th>代表什么</th>
        <th>实战里怎么理解</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>Accuracy</code> / <code>Resolution Rate</code></td>
        <td>任务解决率</td>
        <td>最核心总分，本质上就是“最后有多少题真的做成了”。</td>
      </tr>
      <tr>
        <td><code>Passed / Total</code></td>
        <td>通过数 / 总题数</td>
        <td>本地跑分时最直观，特别适合工程迭代阶段。</td>
      </tr>
      <tr>
        <td><code>Trials</code> / <code>k</code></td>
        <td>每题跑多少次</td>
        <td>单次命中不等于稳定；重复试验更接近真实 agent 可靠性。</td>
      </tr>
      <tr>
        <td><code>95% CI</code></td>
        <td>统计区间</td>
        <td>区间越窄，说明这套 agent 的表现越稳，不太靠运气。</td>
      </tr>
    </tbody>
  </table>
  <p class="tb-note">我的理解是：公开 leaderboard 更接近“多次运行后的任务解决率”，而不是单次 pass@1。你自己在本地先跑一遍全量 <code>k=1</code>，更适合看工程接入和失败簇；如果想更接近榜单口径，再考虑更高试验次数。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">单题内部到底在测什么？</div>
  <div class="tb-callout">
    Terminal-Bench 表面上常被看成“过 / 不过”，但每道题内部真正被 verifier 检查的东西可能差异很大。
  </div>
  <p>有的题要求你把正确文件放到正确路径；有的题看的是服务能否正常监听；有的题卡模型准确率、模型大小、延迟或成本；有的题会检查图像、视频、文本输出是否达到阈值。也就是说，榜单上看的是统一结果，题目内部其实是在测非常具体的工程指标。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">89 个任务中文分类清单</div>
  <p class="tb-mini">下面这份分类是我为了帮助理解而做的主题重组，不是官方 taxonomy。任务名基于 Terminal-Bench 2.0 官方列表整理，介绍则是面向 agent engineering 视角的中文解读。</p>

  <div class="tb-task-group">
    <h4>A. 软件工程、编程语言与算法实现（31题）</h4>
    <ul>
      <li><code>2048-game</code>：实现一个可交互的 2048 克隆，重点看规则、状态更新和交互闭环。</li>
      <li><code>basic-calculator</code>：做一个离线计算器，在受限环境里安全求值 Python 表达式。</li>
      <li><code>calc-bench-hard</code>：从截图与残缺代码中重建受损 benchmark，考逆向理解和功能复原。</li>
      <li><code>click-cell</code>：实现一个 Click Cell 小游戏，考状态逻辑与可玩性验证。</li>
      <li><code>cobol-python</code>：把 COBOL 银行模块翻译成 Python，并尽量保持行为精确一致。</li>
      <li><code>conway</code>：从零实现生命游戏，考规则边界和离散模拟。</li>
      <li><code>corewars</code>：在虚拟 CPU 游戏里写 AI 程序，偏底层规则与对抗式编程。</li>
      <li><code>debug-react-window</code>：根据 issue 与复现测试修 React 虚拟列表 bug，很像真实前端排障。</li>
      <li><code>decode-morse</code>：实现自然语言与摩斯电码双向转换，考 I/O 规范和边界处理。</li>
      <li><code>doom-mips</code>：写性能足够的 MIPS CPU 模拟器去跑 Doom，兼具系统实现和性能压力。</li>
      <li><code>embed-python</code>：不改目标文件的前提下执行 Python 脚本并捕获全局变量。</li>
      <li><code>extract-code</code>：从 Git patch 里还原被隐藏代码，考 diff 与版本信息理解。</li>
      <li><code>git-rebase-plot</code>：做复杂 rebase 让一棵伪造家谱数值自洽，考 Git 历史手术能力。</li>
      <li><code>gpt2-code-golf</code>：在不改行为前提下把 GPT-2 实现压得更短，考语言特性掌握。</li>
      <li><code>group-anagrams</code>：做字母异位词分组，属于经典算法与数据处理题。</li>
      <li><code>karnaugh-map</code>：用卡诺图简化逻辑表达式，考布尔代数与规则化推理。</li>
      <li><code>knn-regression</code>：不依赖 NumPy 实现 KNN 回归，考基础 ML 算法落地能力。</li>
      <li><code>lcs-dp</code>：实现最长公共子序列动态规划，考算法正确性与复杂度意识。</li>
      <li><code>letters</code>：通过重建未知映射破解自定义字节加密，考程序化试探与抽象推理。</li>
      <li><code>mips-fp</code>：为 MIPS 模拟器补 IEEE 754 浮点单元，考底层表示与舍入规则。</li>
      <li><code>polyglot</code>：写一个在多种语言里都合法的程序，考语法边界与语言交集。</li>
      <li><code>regex-chess</code>：求解正则表达式描述的将死棋题，考规则解释与搜索。</li>
      <li><code>remove-duplicates</code>：在严苛内存约束下原地去重，考空间复杂度与实现细节。</li>
      <li><code>ruff-mypy</code>：同时修掉 Ruff 与 MyPy 报错，属于 Python 工程里的静态质量修复题。</li>
      <li><code>shoulda-validate</code>：借助 shoulda-matchers 修复 Rails 测试，考框架语义与约定。</li>
      <li><code>sudoku</code>：求解并验证数独，典型搜索与约束传播问题。</li>
      <li><code>swap-letters</code>：在受限交换规则下恢复文本，考字符串操作与约束满足。</li>
      <li><code>tauri-painter</code>：做一个对齐参考界面的 Tauri 画板，兼顾桌面 UI 与功能正确性。</li>
      <li><code>templating-ruby</code>：修复 Ruby 模板流程但不改变可见输出，考最小修改意识。</li>
      <li><code>terminal-mode</code>：恢复损坏的终端会话与行规状态，考 shell / TTY 基础。</li>
      <li><code>tetris</code>：实现俄罗斯方块，考长状态机、碰撞规则与交互逻辑。</li>
    </ul>
  </div>

  <div class="tb-task-group">
    <h4>B. 系统、网络、DevOps 与基础设施（12题）</h4>
    <ul>
      <li><code>cisco-network-configuration</code>：配置小型 Cisco 网络，考设备配置与连通性验证。</li>
      <li><code>disk-usage</code>：找出大目录并生成磁盘占用报告，偏典型运维诊断。</li>
      <li><code>git-server</code>：搭建自托管 Git server 并接通 Web 部署 hook，考服务与自动化链路。</li>
      <li><code>hf-inference</code>：把 Hugging Face 模型暴露成 OpenAI 兼容推理服务，考模型服务工程化。</li>
      <li><code>mailman3</code>：配置 Mailman 3 邮件列表系统，属于多服务集成排障题。</li>
      <li><code>nginx-log-analyzer</code>：从 Nginx 日志中诊断异常或可疑行为，兼顾运维与安全。</li>
      <li><code>package-lock</code>：处理 Node.js 项目复杂的依赖与 lockfile 问题。</li>
      <li><code>simple-git-s3</code>：通过 Git 触发部署并把文件发到 S3，考 CI/CD 风格自动化。</li>
      <li><code>sqlite-gcov</code>：构建带 gcov 的 SQLite，并从 SQL 测试生成覆盖率。</li>
      <li><code>synchronize-system</code>：排查系统间时钟漂移并同步，考基础但高价值的系统能力。</li>
      <li><code>upload-image</code>：上传图片到远程服务同时保留元数据，考协议与流程细节。</li>
      <li><code>vivaldi</code>：恢复错误配置的 Vivaldi profile，考桌面应用配置与用户态排障。</li>
    </ul>
  </div>

  <div class="tb-task-group">
    <h4>C. 安全、密码学与数字取证（11题）</h4>
    <ul>
      <li><code>bottle-vulnerabilities</code>：识别并修复 Bottle Web 应用漏洞，考 Web 安全基本功。</li>
      <li><code>clean-js</code>：写可靠的 HTML sanitizer，清理 JavaScript 执行路径，考 XSS 防护。</li>
      <li><code>decrypt-blob</code>：搜集 AES / RSA 线索恢复并解密 blob，偏取证式密码任务。</li>
      <li><code>escape-rooms</code>：连续解“密室逃脱”谜题拿到最终 flag，考综合探索与线索串联。</li>
      <li><code>mips-defuse</code>：分析并修改 MIPS 二进制，拆除隐藏陷阱。</li>
      <li><code>patching-ml-kem</code>：修正 ML-KEM 参考实现，使其通过 known-answer tests。</li>
      <li><code>recover-privatekey</code>：从多层损坏线索中恢复 RSA 私钥，强取证导向。</li>
      <li><code>rescue-data</code>：从损坏 tar 包里抢救数据，考文件格式与恢复策略。</li>
      <li><code>restore-git-history</code>：从 Git 历史中恢复文件并清理意外提交的敏感信息。</li>
      <li><code>self-replicating-file</code>：写满足长度约束的 quine，让程序输出自己的源码。</li>
      <li><code>ssh-puzzle</code>：在受限 SSH 环境中层层突破并恢复隐藏 flag，考系统探索与权限边界。</li>
    </ul>
  </div>

  <div class="tb-task-group">
    <h4>D. 数据处理、信息抽取与业务分析（11题）</h4>
    <ul>
      <li><code>beancount-liabilities</code>：理解 Beancount 台账里的负债报告编码方式，考结构化财务数据解析。</li>
      <li><code>create-ics</code>：根据多重约束生成 ICS 日历文件，考时间规则与格式规范。</li>
      <li><code>fix-unicode</code>：修复多语言网页里的 mojibake，同时不破坏正确字符。</li>
      <li><code>gaming-chair-analysis</code>：分析电竞椅数据，识别产品与售后趋势。</li>
      <li><code>gear-ratios</code>：在制造流程数据里追踪正确齿轮比，考关系推断。</li>
      <li><code>image-curation</code>：从候选中挑最适合作为封面的图片，考视觉筛选与规则执行。</li>
      <li><code>parse-image</code>：根据原始像素值与尺寸重建图片，考数据格式理解。</li>
      <li><code>recreate-issues</code>：从仓库历史与交叉引用中重建缺失的 GitHub issues。</li>
      <li><code>social-media-post</code>：基于历史互动数据生成一条社交媒体文案。</li>
      <li><code>travel-planning</code>：在时间、预算与偏好约束下做旅行规划。</li>
      <li><code>web-scraping</code>：从结构不稳定的网页归档中提取信息，考鲁棒抓取与脏数据处理。</li>
    </ul>
  </div>

  <div class="tb-task-group">
    <h4>E. 机器学习、LLM 服务与模型工程（9题）</h4>
    <ul>
      <li><code>color-matching</code>：把真实场景照片匹配到正确色板，考视觉误差控制。</li>
      <li><code>llm-inference-batching-scheduler</code>：设计 LLM 批处理调度器，在成本、padding 与延迟之间做平衡。</li>
      <li><code>model-upload</code>：修复模型并上传到 Hugging Face Hub，考模型工件管理。</li>
      <li><code>sam-cell-segmentation</code>：用 SAM 做显微图细胞分割，考实验可重复性。</li>
      <li><code>train-caffe</code>：训练 Caffe 模型做灰度图分类，偏传统深度学习工具链。</li>
      <li><code>train-fasttext</code>：训练 FastText 模型，同时满足大小和精度约束。</li>
      <li><code>vision-gpt-parser</code>：借助视觉语言模型解析图像内容并结构化输出。</li>
      <li><code>word-press</code>：训练一个简单 bag-of-words WordPress 分类器。</li>
      <li><code>word2vec</code>：训练词向量并评估类比关系，考表示学习闭环。</li>
    </ul>
  </div>

  <div class="tb-task-group">
    <h4>F. 科学计算、生物信息与数理建模（9题）</h4>
    <ul>
      <li><code>adaptive-rejection-sampling</code>：用自适应拒绝采样从目标分布中采样，考统计计算。</li>
      <li><code>backtesting</code>：在股票市场模拟中评估并优化回测策略。</li>
      <li><code>bayesian-network-fit-and-intervention</code>：在生态数据上拟合贝叶斯网络并做干预分析。</li>
      <li><code>chemical-formula-balancing</code>：解析并配平带嵌套、结晶水与电荷的化学方程式。</li>
      <li><code>molecular-reconstruction</code>：根据图结构和几何约束重建分子。</li>
      <li><code>neuro-imaging</code>：处理神经影像并做 voxel 级分析。</li>
      <li><code>rna-folding</code>：在能量和结构约束下优化 RNA 折叠。</li>
      <li><code>simpleqc</code>：对简化基因组数据做质量控制并输出发现。</li>
      <li><code>stan-model-parameter-estimation</code>：在 Stan 中拟合参数以匹配目标后验行为。</li>
    </ul>
  </div>

  <div class="tb-task-group">
    <h4>G. 多模态、图像、视频与内容制作（6题）</h4>
    <ul>
      <li><code>alter-ego</code>：把一个已注册域名塑造成可运行的“替身人格”，偏内容、站点与系统的综合构建。</li>
      <li><code>dream-analysis</code>：设计 prompt，让 LLM 扮演荣格式梦境分析师，考角色稳定性。</li>
      <li><code>find-best-move</code>：从棋盘图片中读出局面并计算最佳着法，结合视觉解析与棋类推理。</li>
      <li><code>media-editing</code>：编辑多种媒体资产并同步成最终内容包，考多格式素材处理。</li>
      <li><code>video-bout</code>：根据击剑视频时序剪辑并标注片段，考视频理解与事件定位。</li>
      <li><code>video-hurdles</code>：从跨栏比赛视频中检测起跳与落地帧，考时序视觉识别。</li>
    </ul>
  </div>
</div>

<div class="blk-v2">
  <div class="sh-v2">这些题最常见的失败点</div>
  <div class="tb-card-grid">
    <div class="tb-card">
      <h3>没有先摸清环境</h3>
      <p>目录、依赖、测试入口、输出路径没搞明白就开始改，最后往往是方向错了还越做越深。</p>
    </div>
    <div class="tb-card">
      <h3>只会修改，不会自验证</h3>
      <p>看见命令不报错就停，但 verifier 真正检查的是终态，不是“我觉得差不多”。</p>
    </div>
    <div class="tb-card">
      <h3>长任务里目标漂移</h3>
      <p>重复跑同样命令、忘了原始要求、改错文件、漏掉最后收尾，这是 terminal agent 最常见的崩点。</p>
    </div>
    <div class="tb-card">
      <h3>系统工具不熟</h3>
      <p>不会读日志、不会判断 lockfile 冲突、不会处理服务状态或 Git 历史，很多题就会卡死在工程细节上。</p>
    </div>
  </div>
</div>

<div class="blk-v2">
  <div class="sh-v2">如果你在做自己的 coding agent，该怎么提分？</div>
  <div class="tb-callout">
    对 Terminal-Bench 来说，最有效的涨分路线通常不是“让模型更会说”，而是“让 agent 更像一个会交付的工程系统”。  
  </div>
  <p>如果只能优先做几件事，我会按下面这个顺序来：</p>
  <ul>
    <li>先把 agent 做成真正可无头运行的 CLI，支持单次执行、非交互模式和完整日志输出。</li>
    <li>把“先看环境”做成默认动作：目录、README、测试脚本、verifier 入口、产物路径先摸清楚。</li>
    <li>强制把验证做成最后一步：改完先跑最小测试，再跑更完整验证，最后核对交付路径和格式。</li>
    <li>让 agent 学会根据错误重试，而不是机械重复同一条命令。</li>
    <li>把任务目标结构化成 checklist，减少长任务中的上下文漂移。</li>
    <li>先做 staged eval：oracle / smoke → 1 题 → 3 到 5 题 → 全量 <code>k=1</code> → 更接近 leaderboard 口径的重复试验。</li>
  </ul>
  <p>很多团队一开始会直觉地把希望寄托在更大模型上，但 Terminal-Bench 经常提醒我们：<strong>agent system 的可靠性、工具使用和收尾能力，和模型能力同样重要，甚至更重要。</strong></p>
</div>

<div class="blk-v2">
  <div class="sh-v2">怎么用它来分析一套 agent？</div>
  <p>如果我在评估一套新的 coding tool，我不会只看总分，还会额外看四个问题：</p>
  <ul>
    <li>它更像“代码生成器”，还是更像“真正的终端代理”？</li>
    <li>它是偶尔会做，还是做得稳？</li>
    <li>它最怕哪类环境：系统题、安全题、多服务题还是多模态题？</li>
    <li>它输在知识、执行还是收尾？</li>
  </ul>
  <p>这也是 Terminal-Bench 很有价值的地方。它不只给你一个分数，还会逼着你去理解：你的 agent 到底卡在了哪里。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">写在最后</div>
  <p>我对 Terminal-Bench 最喜欢的一点，是它把大家从“模型像不像专家”拉回到“代理最后有没有把活干完”。</p>
  <p>对于做 coding agent 的人来说，这个视角特别重要。真实上线的工具几乎都不是靠一轮漂亮回答取胜，而是靠：探索环境、调用工具、逐步修改、反复验证、正确交付。</p>
  <p><strong>所以我更愿意把 Terminal-Bench 2.0 看成 89 个缩微版真实工程工作流，而不是 89 道题。</strong></p>
</div>

<div class="blk-v2">
  <div class="sh-v2">来源与说明</div>
  <ul>
    <li>主要来源：<a href="https://www.tbench.ai/">Terminal-Bench 官网</a>、<a href="https://www.tbench.ai/benchmarks/terminal-bench-2">Terminal-Bench 2.0 页面</a>、<a href="https://www.tbench.ai/leaderboard/terminal-bench/2.0">Terminal-Bench 2.0 Leaderboard</a>。</li>
    <li>运行与结果相关：<a href="https://www.harborframework.com/docs/tutorials/running-terminal-bench">Harbor: Running Terminal-Bench</a>、<a href="https://www.harborframework.com/docs/agents">Harbor Agents</a>、<a href="https://www.harborframework.com/docs/run-jobs/run-evals">Harbor Evals / Jobs / Results</a>。</li>
    <li>研究背景：<a href="https://arxiv.org/abs/2601.11868">Terminal-Bench 论文（arXiv）</a>。</li>
    <li>说明：文中的任务分组与工程解读是我为了方便理解所做的二次整理，不是官方 taxonomy；关于 leaderboard 更接近多次运行解决率的判断，是结合公开页面展示方式做出的工程性解释。</li>
  </ul>
</div>
