---
layout: page
permalink: /blogs/harness-engineering-self-improving-agents/index.html
title: Harness Engineering：自我改进智能体的工程与边界
description: 从 Lilian Weng 的 Harness Engineering 出发，讲清楚上下文工程、工作流搜索、harness 自我修改与进化搜索各自如何工作，现有证据支持到哪一步，以及距离真正的递归自我改进还差什么。
---

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},{left:'\$',right:'\$',display:false},{left:'\\[',right:'\\]',display:true}],throwOnError:false,ignoredTags:['script','noscript','style','textarea','pre','code']});"></script>

<style>
.he-lead{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1.05rem;border-radius:10px;margin:1rem 0 1.25rem}
.he-lead p{margin:.35rem 0;color:#405160;line-height:1.85}
.he-callout{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem 1.05rem;margin:1.1rem 0 1.3rem}
.he-callout p{margin:.15rem 0;color:#405160;line-height:1.8}
.he-toc{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:.9rem 1.15rem;margin:1.1rem 0 1.5rem;font-size:.93rem}
.he-toc ol{margin:.3rem 0 .2rem 1.2rem;padding:0}
.he-toc li{margin:.28rem 0;line-height:1.7}
.he-toc a{color:#2e4f63;text-decoration:none}
.he-wrap{overflow-x:auto;margin:1rem 0 1.3rem}
.he-table{width:100%;border-collapse:collapse;min-width:640px;font-size:.93rem}
.he-table th,.he-table td{border-bottom:1px solid #dde4ea;padding:.7rem .58rem;text-align:left;vertical-align:top}
.he-table th{color:#34495a;background:#f8fafc}
.he-table td{color:#4b5c69;line-height:1.7}
.he-eq{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:.85rem 1rem;margin:1rem 0 1.25rem;overflow-x:auto;text-align:center}
.he-eq .katex{font-size:1.05em}
.he-figure{margin:1.4rem 0 1.5rem}
.he-figure img{display:block;width:100%;height:auto;border-radius:10px;border:1px solid #dce5ec;background:#050507}
.he-figure figcaption{color:#667784;font-size:.86rem;line-height:1.65;margin-top:.55rem;text-align:center}
.he-refs{font-size:.9rem;line-height:1.72;color:#56636f}
.he-refs li{margin:.48rem 0}
.he-source{margin-top:1.4rem;padding:1rem 1.1rem;border:1px solid #dce5ec;border-radius:10px;background:#fbfcfe;color:#56636f;font-size:.92rem;line-height:1.8}
.weather-widget-container{display:none!important}
@media (max-width:840px){.he-figure{overflow-x:auto;-webkit-overflow-scrolling:touch}.he-figure img{width:760px;max-width:none}}
</style>

## Harness Engineering：自我改进智能体的工程与边界

> 更新时间：2026/07/10
> 关键词：agent harness, recursive self-improvement, context engineering, workflow search, evolutionary search, auto-research

<div class="he-source">
本文基于 Lilian Weng 于 2026 年 7 月 4 日发表的 <a href="https://lilianweng.github.io/posts/2026-07-04-harness/">Harness Engineering for Self-Improvement</a>，沿其框架用中文重新展开，机制解读与原文一致的部分归功于原作者。在此之上，本文补充了发表状态核验（区分同行评审论文与预印本 [P3]/[P1]）、J/Q 判别框架、可证伪的研究问题与安全边界设计；这些扩展由本文负责，不代表原作者观点。
</div>

"递归自我改进"（recursive self-improvement, RSI）这个想法可以追溯到 I. J. Good 在 1965 年对"超智能机器"的设想：一台机器如果能设计出比自己更好的机器，改进就会滚雪球 <a href="#ref-1">[1]</a>。Yudkowsky 在 2008 年把 RSI 具体化为一个反馈环：AI 用当前智能去改进产生智能的认知机制本身。在今天的 AI 语境里，这个循环有一个务实得多的近期形态——模型不需要先学会改写自己的权重，它可以先改进围绕自己的那套系统：训练流水线、部署系统，以及本文的主角，**harness**。

Harness 是包裹在基础模型外面的执行系统。它决定模型看到什么上下文、能调用哪些工具、怎样规划和行动、把中间产物存在哪里、如何验证结果，以及失败之后是重试、回滚还是停止。Claude Code、Codex 这类编程智能体的成功很大程度上是 harness 的成功：同一个模型，换一套 harness，行为和成绩会差出一截。前沿实验室的研究节奏也在加速，但"部署系统"这一层——模型预训练评测之后、真实任务之前——的重要性，正被越来越多的证据单独拎出来讨论。

<div class="he-lead">
  <p><strong>本文想讲清楚三件事：</strong>第一，harness 里反复出现的设计模式是什么，为什么它们长这样；第二，"优化 harness"这条路线上每一层——上下文、工作流、harness 代码、优化器本身——的代表方法具体如何工作，证据支持到哪一步；第三，这些进展距离严格意义上的递归自我改进还差什么，差距应该怎么用实验去测量。</p>
</div>

<div class="he-toc">
<strong>目录</strong>
<ol>
  <li><a href="#sec-what">Harness 是什么：从 prompt 模板到运行时</a></li>
  <li><a href="#sec-patterns">三个反复出现的设计模式</a></li>
  <li><a href="#sec-vs-core">Harness 与核心智能：互补还是替代</a></li>
  <li><a href="#sec-ladder">优化的阶梯：从上下文到优化器本身</a></li>
  <li><a href="#sec-rsi">这算递归自我改进吗</a></li>
  <li><a href="#sec-questions">值得做的实验，而不只是叙事</a></li>
  <li><a href="#sec-science">自动科研：最严苛的压力测试</a></li>
  <li><a href="#sec-challenges">走向 RSI 的七个开放挑战</a></li>
  <li><a href="#sec-practice">给构建者的最小清单</a></li>
  <li><a href="#sec-appendix">附录：代表性 Benchmark</a></li>
</ol>
</div>

### 一、Harness 是什么：从 prompt 模板到运行时 {#sec-what}

早期的 agent 框架常被概括为一个加法公式：

<div class="he-eq">$$\text{Agent} = \text{LLM} + \text{Memory} + \text{Tools} + \text{Planning} + \text{Action}$$</div>

这个公式解释了组件，但没有解释系统。现代 harness 更像一个运行时，甚至像一个操作系统：它封装复杂逻辑、暴露简单接口，规定模型如何观察、如何行动、如何记忆、如何自检。和操作系统一样，它的配置格式、工具协议正在跨行业逐渐标准化（MCP 就是一个例子）。对任务 $x$，一次执行可以写成：

<div class="he-eq">$$\tau \sim p\!\left(\tau \mid x,\, M_\theta,\, H_\phi,\, K_\kappa,\, B\right)$$</div>

其中 $M_\theta$ 是冻结的基础模型；$H_\phi$ 是可以被优化的一切——上下文逻辑、编排、工具执行、验证与元优化；$K_\kappa$ 是权限、沙箱、预算、审计这些不应该被系统自己修改的部分；$\tau$ 不只是最终回答，而是包含每次工具调用、状态变化和验证证据的完整轨迹；$B$ 是 token、工具调用、时间等预算约束。

<figure class="he-figure">
  <img src="/assets/images/harness-engineering/layered-harness-boundary.svg" alt="分层 Agent Harness 与不可变安全边界">
  <figcaption>图 1｜分层 harness：L1–L5 是可优化区域，安全内核位于系统外部。分层框架为本文提出，用于统一后文各方法的讨论。</figcaption>
</figure>

Harness 重要到什么程度？最干净的证据来自 SWE-agent（NeurIPS 2024）：作者专门为语言模型设计了一套 Agent-Computer Interface——文件查看器一屏只显示 100 行、编辑命令内置语法检查、搜索结果强制精简——仅凭接口设计，就把 SWE-bench 解题率从此前最好的检索增强方法的 3.8% 提高到 12.5%（GPT-4 Turbo）<a href="#ref-3">[3]</a>。模型层面没有任何改动，变的只是它"手里的工具顺不顺手"。

但也要克制。这类研究是在固定模型、固定任务上比较少量接口，它支持"harness 设计影响很大"，还不足以支持"harness 与模型智能同等重要"。后者需要真正的模型 × harness × 预算 × 任务析因实验，目前还没有人系统做过——这是本文第六节的主题之一。

### 二、三个反复出现的设计模式 {#sec-patterns}

看足够多的 harness 之后会发现，好的设计在收敛。Weng 的原文归纳了三个模式，每一个背后都有可查的研究支撑。

**模式一：目标导向的工作循环。** 核心是一个显式的 plan → execute → observe/test → improve 循环，直到达成目标或触发停止条件，中途可以主动向用户澄清任务。这不是新想法——ReAct 在 2023 年就证明了让模型交错生成推理和动作、并根据环境反馈更新计划，能显著减少幻觉和错误传播 <a href="#ref-2">[2]</a>；Reflexion 进一步展示了不更新任何权重、只把失败的语言反思写进情景记忆，就能让下一次尝试变好 <a href="#ref-4">[4]</a>。Karpathy 的 autoresearch 仓库是这种工作流在科研场景里的干净实例：模型在可测试的循环里自己改代码、跑实验、读日志、再改。Harness 把这个循环从 prompt 技巧变成了带停止条件、预算和失败出口的运行时结构。关键要求是循环可观测：如果"反思"只存在于转瞬即逝的对话上下文里，它既无法审计，也无法在中断后恢复。

**模式二：文件系统作为持久记忆。** 长程任务的产物——实验日志、代码 diff、论文摘要、错误堆栈、历史轨迹——很快就会超出任何上下文窗口。与其把一切塞进 context，不如把持久状态放进文件，需要时再读。这个选择有两重依据。一是长上下文本身不可靠：Lost in the Middle 表明关键信息位于长上下文中部时模型性能显著下降 <a href="#ref-5">[5]</a>；LongMemEval 发现商业助手在持续多轮交互记忆任务上准确率下降约 30%，并主张把记忆拆解为索引、检索、阅读三个阶段分别优化 <a href="#ref-6">[6]</a>。二是读写文件（通常经由 bash）是模型的基础能力，随预训练持续变强，文件记忆能"免费"搭上模型进步的便车。不过要诚实地说：现有研究支持"外置持久状态 + 选择性检索"，并没有证明普通文件系统优于数据库、向量检索或事件日志——文件的真正优势是简单、透明、可版本化。Agent Workflow Memory 还提示了更进一步的方向：与其堆积原始日志，不如从历史轨迹中提炼可复用的程序性工作流，这在长程网页任务上带来了跨任务的泛化收益 <a href="#ref-7">[7]</a>。

**模式三：子代理与后台任务。** 当主 agent 需要并行探索多个假设、同时跑几组实验，或者把隔离的子任务委托出去而不污染主上下文时，harness 需要扮演一个小型进程管理器：启动任务、查看日志、取消失败的运行、把结果合并回主线程。这里的关键设计是让并行显式、可检查——子代理的输出如果只活在临时对话里，很快就会失效和不可见；落成文件、日志和状态记录，主 agent 才能在中断后恢复，并对自己的执行历史做推理。

把这三个模式落到最成熟的场景——coding agent——工具面已经高度趋同：

<div class="he-wrap">
<table class="he-table">
  <thead><tr><th>类别</th><th>典型工具</th></tr></thead>
  <tbody>
    <tr><td>文件系统</td><td>glob / grep / read / write / edit / apply_patch</td></tr>
    <tr><td>命令执行</td><td>bash、后台任务、定时任务</td></tr>
    <tr><td>外部上下文</td><td>web search / fetch、MCP 工具、skills</td></tr>
    <tr><td>产物</td><td>读写文档与图像、git 操作、生成报告</td></tr>
    <tr><td>子代理</td><td>spawn / resume / wait / interrupt / close</td></tr>
  </tbody>
</table>
</div>

在这三个模式之外，我认为还有两个板块必须补进设计清单，它们在原文中着墨较少，但有独立的证据支撑。**其一是独立验证器**：优先用测试、schema、数据库状态这类确定性证据判断成败，LLM 自评只做补充——同一个模型基于同一条轨迹给自己打分，容易继承同一个盲点。**其二是位于优化循环之外的安全内核**：ToolEmu 用 LM 模拟的沙箱系统测量了 agent 使用高风险工具的失败率，即便当时最安全的 agent，也在 23.9% 的场景中出现了潜在严重后果的失败（人工校验显示其中约七成会构成真实世界的有效失败）<a href="#ref-8">[8]</a>；AI Sandbagging 则证明模型可以被诱导在能力评测上选择性放水 <a href="#ref-9">[9]</a>。这两个结果指向同一个结论：权限、预算、审计日志和最终计分器，不能交给被优化的系统自己管理。这正是图 1 中 L4 和 $K_\kappa$ 存在的理由。

### 三、Harness 与核心智能：互补还是替代 {#sec-vs-core}

一个经常被问到、但很少被实证回答的问题是：未来 RSI 到底靠 harness 还是靠模型本身？Weng 的原文给了一个务实的预测，我把它展开成三条可检验的命题。

**近期路径不会从"模型直接改写权重"起步。** 更现实的顺序是：先让 harness 承担可搜索、可验证、可回滚的改进；等这套机制稳定之后，再把其中反复出现的模式内化进训练流水线或权重更新。Self-Harness、DGM、STOP 都在走这条路——它们固定 $M_\theta$，只动 $H_\phi$ 或优化器 $\psi$。

**Harness 会朝"元方法论"演化。** 被优化的对象从"这一次任务的答案"变成"产生更好答案的机制"：上下文管理规则、工作流拓扑、harness 源码、变异算子本身。MCE 的双层优化、Meta-Harness 的 Pareto 前沿搜索、STOP 的 $I_t = I_{t-1}(\hat{u}, I_{t-1}; M)$ 都是这个方向的实例。这不是抽象预测——每一层阶梯上都已经有了可引用的论文。

**成熟的 harness 与更强的模型是互相喂养的。** 更好的 harness 让同一模型在真实任务上释放更多能力，从而支撑 auto-research 和数据合成；更强的模型又降低 harness 过度工程化的压力——prompt engineering 的历史已经演示过软版本：手工技巧随 instruction tuning 和 reasoning 能力提升而边缘化，但目标、约束、上下文和评估的需求从未消失。对外部工具和环境的接口层，大概率会长期存在。

因此，"harness vs 核心智能"更准确的表述是**互补而非替代**。STOP 的警示性结果已经给出了边界条件：递归结构本身不产生改进，基座模型必须强到能理解并改进那个机制；弱基座下 $Q(\psi)$ 可以为负。真正缺的是析因实验——在固定任务上同时扫描模型能力、harness 复杂度和预算，画出等效前沿——而不是再写一篇"我们又改进了 harness"的叙事。

### 四、优化的阶梯：从上下文到优化器本身 {#sec-ladder}

Harness 系统中被优化的对象有一条清晰的演进线：

<div class="he-eq">$$\text{指令 prompt} \;\to\; \text{结构化上下文} \;\to\; \text{工作流} \;\to\; \text{harness 代码} \;\to\; \text{优化器代码}$$</div>

越往右，表达能力越强，搜索空间、评测成本和安全攻击面也越大。下面按层拆开，每一层讲清楚代表方法的机制和证据边界。

#### 4.1 上下文工程：把 context 当作可进化的资产

Prompt 优化的系统化始于 DSPy：把 LM 流水线抽象成声明式模块组成的计算图，用编译器自动生成和筛选示例来最大化指定指标，几分钟内就能超过人工少样本提示（ICLR 2024）<a href="#ref-10">[10]</a>。GEPA 走得更远：它读取完整执行轨迹做自然语言反思来提出 prompt 更新，并用 Pareto 前沿合并互补经验，在 ICLR 2026 的口头报告版本中以远少于 GRPO 的 rollout 数量取得了更好的结果 <a href="#ref-12">[12]</a>——这个结果值得记住，因为它说明轨迹中的语言信息比标量 reward 更有诊断价值。

但 agent 的上下文不只是 prompt。**ACE**（Agentic Context Engineering，ICLR 2026）把上下文当作一本持续进化的"作战手册"而非越写越长的提示词 <a href="#ref-13">[13]</a>。它用三个角色维护一份由条目组成的结构化 context：Generator 参照现有条目产生任务轨迹；Reflector 从成功和失败的轨迹中提炼洞见；Curator 把洞见写成带标识符的增量条目，用确定性逻辑合并进手册，并定期去重。这里最重要的设计是 Curator 从不重写整个 prompt——迭代式整段重写会导致"context collapse"（信息在反复压缩中丢失）和简洁性偏置，增量条目 + 确定性合并避开了这两个坑。

ACE 的更新规则仍是手工设计的。**MCE**（Meta Context Engineering，预印本）把"怎么管理上下文"这件事本身也变成了优化对象 <a href="#ref-14">[14]</a>。它定义 skill $s \in \mathcal{S}$ 为一组静态组件 $\rho_s = \{\rho_1,\dots,\rho_m\}$（prompt、知识库、代码库）加一组动态算子 $F_s = \{F_1,\dots,F_k\}$（搜索、筛选、格式化），上下文函数 $c_s = (\rho_s, F_s)$ 把输入 $x$ 映射为 $c = F_s(x; \rho_s)$。双层优化写成：

<div class="he-eq">$$\text{内层：}\; c_s^* = \arg\max_{c_s} J_{\text{train}}(c_s; s) \qquad \text{外层：}\; s^* = \arg\max_{s \in \mathcal{S}} J_{\text{val}}(c_s^*)$$</div>

skill 数据库记录历史 $\mathcal{H}_{k-1} = \{(s_i, c_i, J_i^{\text{train}}, J_i^{\text{val}})\}_{i=1}^{k-1}$；元级 agent 对既有 skill 做代理式杂交产生新 skill $s_k = \text{crossover}(\tau, \mathcal{H}_{k-1})$，基级 context engineer 在标准工具集

<div class="he-eq">$$\mathcal{T} = \{\texttt{Read}, \texttt{Write}, \texttt{Edit}, \texttt{Bash}, \texttt{Glob}, \texttt{Grep}, \texttt{TodoWrite}\}$$</div>

上执行 skill 并从 rollout 反馈 $\mathcal{R}_k$ 学习 $c_k = \text{engineer}(\tau, s_k; c_{k-1}^*, \mathcal{R}_k)$。实现上一个 skill 就是一个目录：`skill.md` 加数据和轨迹文件——"一切皆文件、一切皆代码"的自然延伸。

#### 4.2 工作流搜索：把编排变成可搜索的程序

工作流可以由专家手工设计。AI Scientist 的选题、实验、写作、评审流水线是一个例子（后文详谈）<a href="#ref-27">[27]</a>；ScientistOne 则把**可验证性**做成中心约束——每条论断（引用、数值、方法、结论）必须追溯到证据源，并由 Chain-of-Evidence 审计 <a href="#ref-36">[36]</a>。但设计空间太大，自然的想法是让算法来搜。

**Autodata** 是数据合成方向的代表作：主 agent 管理 challenger（出题）、弱 solver、强 solver 和 verifier，专门合成"强模型做得出、弱模型做不出"的恰好难度数据 <a href="#ref-35">[35]</a>。challenger 的 prompt 根据 solver 和 verifier 的反馈迭代更新。这里有一个原文强调的局限，值得单独记住：**合成任务主要用于微调弱 solver，而不是强 solver**。如果循环不能迭代改进强模型，它更像是在生成 prompt 分布上的间接蒸馏，RSI 味道较淡——强模型始终是固定的"教师"，而不是被改进的对象。这和第三节的预测一致：近期 RSI 更可能从 harness 和数据流水线起步，而不是从强模型自举起步。

**ADAS**（ICLR 2025）把 agent 设计本身表述为"元 agent 搜索"：维护一个工作流档案，初始只有 CoT、self-refine 这类简单 agent；让一个元 agent 阅读档案，先写出新工作流的自然语言描述，再实现成代码，经过两轮自我改进检查后评估，表现好的加回档案，如此循环 <a href="#ref-15">[15]</a>。**AFlow**（ICLR 2025 Oral）则把工作流表示成图——节点是 LLM 调用，边是代码实现的逻辑——用蒙特卡洛树搜索优化：从模板 $W_0$ 出发，按得分与探索的软混合选节点，让 LLM 基于评测反馈生成修改后的工作流，执行评估后有提升才回填进树，直到 top-$k$ 平均分收敛 <a href="#ref-16">[16]</a>。在 QA、代码、数学六个数据集上，AFlow 比手工设计的工作流平均高约 5.7%，比 ADAS 等既有自动方法平均高约 19.5%。

这两项工作的共同启示是：**代码是工作流的通用表示，一个会写代码的模型就能探索人类工程师的设计空间**。但证据边界也清楚——提升发生在受控 benchmark 上，跨领域稳定性尚未验证。

#### 4.3 Harness 代码：系统开始修改自己

再往上一层，被优化的就是 harness 代码本身。

**Meta-Harness**（预印本）的优化对象是"决定信息如何被存储、检索、呈现给模型"的那部分代码——名字里的 meta 指它是一个用来优化 harness 的 harness <a href="#ref-17">[17]</a>。提案者本身是个 coding agent：全部执行历史放在文件系统里，它用 grep 和 cat 去翻，而不是把一切塞进一个 prompt；每个候选 harness 是文件系统中的一个字典，装着自己的源码、得分、轨迹和状态更新；循环不断生成新候选，只留下合格的，最终输出 Pareto 前沿上的一组 harness。需要注意的是，它在 TerminalBench-2 上的搜索是从 Terminus 这类很强的手工 harness 初始化的——说明这套方法目前更像"精修"而非"从零发明"。

**Self-Harness**（预印本）给出了这一层迄今最完整的闭环设计 <a href="#ref-18">[18]</a>，值得展开它的三个阶段：

1. **弱点挖掘。** 用当前 harness $h_t$ 跑评测、收集执行轨迹，把失败聚类成有验证器依据的失败模式。难点在于两次运行可能在错误日志上看起来一样（都是超时、都缺产物），但因果机制完全不同，所以失败记录必须足够富：终端的验证器级原因、相关 agent 行为的因果状态、轨迹暴露的抽象机制。
2. **有界提案。** 同一个模型被调用为提案者，但它拿到的是一个精心限定的上下文：当前 harness 的可编辑表面、挖掘出的失败模式、必须保留的通过行为、历史修改尝试的摘要。提案被引导向"反复出现、可以用小改动解决"的错误，而不是任务本身太难的情况，且候选之间要求多样。
3. **回归验证。** 每个候选修改要同时通过 held-in 集 $D_{\text{in}}$（确认弱点被解决）和 held-out 集 $D_{\text{out}}$（确认没引入新问题），两边都无回归才被合并进 $h_{t+1}$；被拒绝的候选留档但不生效。

在 Terminal-Bench-2 上，这套循环为 MiniMax M2.5、Qwen3.5-35B-A3B、GLM-5 三个不同的开源模型分别学出了针对各自弱点的 harness 指令，并提升了 held-out 通过率——**harness 修改是模型特定的**，这一点对"换模型要不要重调 harness"这个工程问题很有信息量。Self-Harness 也直接提出了安全担忧：如果程序被允许编辑"操作系统"层，抽象边界就被打破——可编辑表面和安全层必须外置设计。

**DGM**（Darwin Gödel Machine，ICLR 2026）是这一层被引用最多的结果 <a href="#ref-19">[19]</a>。它显式地进化一个可编辑的 harness 代码仓库：从一个 coding agent 起步；每轮按"性能越高越优先、子代越多越降权"的概率挑一个父代；被选中的 agent 阅读自己的 benchmark 评测日志，对自己的 harness 代码库提出改进（代码编辑只靠 bash 和一个查看/创建/编辑文件的 editor 两个工具），生成新版本的自己；新 agent 评测合格才进池。以 Claude 3.5 Sonnet 为固定基座、从极简初始配置出发，DGM 发现的 agent 把 SWE-bench Verified 从 20% 推到 50%，Polyglot 从 14.2% 推到 30.7%，接近或超过同期手工 agent 的水平。

**Hyperagents**（预印本）是 DGM 的后续：引入元 agent 来控制**如何修改现有 task agent 以创造新 agent** <a href="#ref-37">[37]</a>。如果说 DGM 让单个 agent 在固定规则下变异自己的 harness，Hyperagents 把"变异策略"也交给了另一个 agent——搜索空间从"改自己的代码"扩展到"决定怎么改别人的代码"。这更接近开放式 agent 生态的进化，但同样受限于评测器和可编辑表面的设计；预印本阶段，证据仍待同行评审确认。

#### 4.4 进化搜索：当评估又快又客观时

进化方法特别适配这个领域：搜索空间离散、组合、非可微，梯度拿不到，但候选解容易评估。

Promptbreeder 是早期代表：不仅进化任务 prompt，连"指导变异的 mutation prompt"也一起进化——优化器的组件本身进入了搜索空间（ICML 2024）<a href="#ref-11">[11]</a>。**AlphaEvolve**（DeepMind 技术报告）把这个思路做成了完整的代码进化系统：维护一个候选程序池，用冻结的 LLM 生成改进 diff，反复评估子代、保留优胜者 <a href="#ref-20">[20]</a>。几个设计细节值得记：prompt 里带着父代程序、结果和元信息；agent 能访问完整仓库，但可进化区域用 `EVOLVE-BLOCK-START/END` 显式标出；元 prompt 与解程序共同进化。消融实验确认进化过程、上下文、元 prompt、全文件进化和更强的 LLM 各自都有贡献。

**ThetaEvolve**（预印本）把进化搜索与 RL、上下文学习结合起来，面向开放问题的 test-time learning <a href="#ref-38">[38]</a>——在 AlphaEvolve 的"纯进化"之外，尝试让系统在测试时从反馈中学习，而不只依赖种群变异。ShinkaEvolve（ICLR 2026）则在采样效率上更进一步：父代采样平衡性能与后代数、用 embedding 相似度拒绝与现有种群过近的候选、用元便签沉淀成功模式引导后续变异 <a href="#ref-21">[21]</a>。而 FunSearch 登上 Nature 的结果证明了这条路线的上限：程序搜索可以产生真正的数学新发现 <a href="#ref-22">[22]</a>。

边界同样明确：这一族方法在矩阵乘法、GPU kernel、算法竞赛这类**评估快速、客观、可自动化**的领域表现出色；KernelBench 用 fast_p（正确且快于基线的 kernel 占比）量化这一点，当时最好的系统仍有大量 room to grow <a href="#ref-40">[40]</a>。评估一旦缓慢、模糊或依赖人的判断，进化循环就转不动。科学品味、因果解释、长期研究价值——这些恰好都在后一类里。

#### 4.5 优化器与权重：递归的最深处

**STOP**（Self-Taught Optimizer，COLM 2024）是"改进改进者"的最早正式实验 <a href="#ref-23">[23]</a>。定义一个改进器 $I$：输入初始解 $s$、效用函数 $u$ 和黑盒模型 $M$，输出更好的解 $s' = I(u, s; M)$。STOP 的目标不是改进 $s$，而是改进 $I$ 本身。定义元效用为改进器在一批下游任务 $\mathcal{D}$ 上的平均表现：

<div class="he-eq">$$\hat{u}(I) \triangleq \frac{1}{|\mathcal{D}|}\,\mathbb{E}_{(u,s)\sim\mathcal{D}}\bigl[u(I(u,s; M))\bigr]$$</div>

于是改进器可以拿自己当输入，递归更新：

<div class="he-eq">$$I_t = I_{t-1}(\hat{u},\, I_{t-1};\, M)$$</div>

被改进后的改进器自己发现了遗传算法、分解-改进、多臂 prompt 老虎机、模拟退火、beam search 等策略。但 STOP 最有价值的发现是一个警示：用 GPT-4 时下游性能随迭代上升，换成 GPT-3.5 或 Mixtral 则随迭代**退化**。递归结构本身不产生改进——基础模型必须强到能理解并改进那个机制。这解释了为什么 harness 工程和模型智能是互补而非替代关系。

最后是把 harness 修改和权重更新放进同一个循环的尝试。SIA（预印本）用三个角色：Meta-Agent 提出初始 harness，任务 agent 执行，Feedback-Agent 根据近期轨迹决定下一轮更新 harness 还是更新权重 <a href="#ref-24">[24]</a>。方向有意思，但目前的实验难以解读——任务 agent 用的是 gpt-oss-120b，而 Meta 和 Feedback 角色用的是强得多的 Claude Sonnet 4.6，提升究竟来自"自我改进"还是来自外部强模型的持续注入，无法区分；基线也偏弱。我把它记为"值得关注、证据暂缺"。

### 五、这算递归自我改进吗 {#sec-rsi}

上面每一层都有"系统变好了"的结果，很多论文也都自称 self-improvement。工程上无妨，但科学上需要更严格的判别——**以下 J/Q 框架是本文的扩展，不是原文内容**。

先承认结果是多维的。一个 harness 的表现至少包含能力、可靠性、成本、泛化、安全风险、人工介入六个维度，它们构成一个向量，向量之间没有天然的大小关系。主分析应该报告 Pareto 前沿；如果必须选出单一候选，就在看到结果之前预注册好标准化方法和权重，压成一个标量效用 $J$，并附带硬约束（严重安全违规率不超过上限、成本不超预算）。

拿到 $J$ 之后，可以区分两个完全不同的命题：

<div class="he-eq">$$J(\phi_{r+1}) > J(\phi_r) \quad\text{——}\quad \text{当前 harness 变好了}$$</div>

<div class="he-eq">$$Q(\psi) = \mathbb{E}\!\left[\frac{J\!\left(\Pi_{\mathcal{E}}\bigl(U_\psi(\phi, \tau)\bigr)\right) - J(\phi)}{\text{搜索成本}}\right] \quad\text{——}\quad \text{优化器 } U_\psi \text{ 有多会改进}$$</div>

其中 $\Pi_{\mathcal{E}}$ 是投影到可编辑表面 $\mathcal{E}$ 上的算子。第一个命题是**有界 harness 优化**：DGM、Self-Harness、Meta-Harness 都属于这一级——系统在预定义的代码表面、benchmark 和验证器内，生成并接受了提高 held-out 表现的自身修改。这是真实且重要的进展，但它不涉及"改进能力本身在增长"。第二个命题才是**递归自我改进**的核心：优化器 $\psi$ 在系统自己产生的改变之后，在全新元任务上、固定搜索预算下，单位成本产出的改进 $Q$ 持续上升。目前没有任何公开工作满足这个标准——STOP 是最接近的尝试，而它恰恰展示了弱基座下 $Q$ 为负。

<figure class="he-figure">
  <img src="/assets/images/harness-engineering/optimization-vs-rsi.svg" alt="Harness 优化与递归自我改进的判别">
  <figcaption>图 2｜J 上升只说明当前系统被优化；只有优化器的改进能力 Q 也在全新元任务上跨轮上升，且通过安全门，才称得上递归自我改进。本文原创图。</figcaption>
</figure>

用这个框架回看文献，准确的表述是：我们已经有了**有边界、可评测的经验性自我改进**（bounded empirical self-improvement），距离 Good 设想的那种开放式递归，中间隔着"优化器自身是否变强"这个还没人回答的实证问题。这不是悲观——把一个宏大叙事拆成可测量的命题，恰恰是它开始成为科学的标志。

### 六、值得做的实验，而不只是叙事 {#sec-questions}

现在这个领域的典型论文叙事是"让 agent 修改自己的 harness，benchmark 上升了"。这个叙事几乎不可能失败，所以它的信息量有限。以下五个问题的共同点是允许实验给出否定答案——它们是本文提出的研究方案。

**收益来自架构，还是来自更多计算？** 把结构化上下文（L1）、规划编排（L2）、独立验证（L4）做成 $2 \times 2 \times 2$ 析因设计，所有条件固定 token、工具调用和时间预算，再加一个关键对照：消耗同等预算但不改变任何决策的"sham 计算组"。如果 harness 的收益在预算对齐后消失，那它卖的其实是算力，不是设计。

**独立验证器是否真的减少静默错误？** 比较无验证、同 agent 自评、独立同模型验证、独立异模型验证四组，指标除了通过率，必须包含错误接受率（把坏结果当好结果放行）和错误拒绝率——一个靠拒绝一切来"保安全"的验证器毫无价值。

**公开 benchmark 上的提分能保留多少？** 在公开开发集上优化，再在新仓库、新任务族、时间外数据上盲测，比较两边的标准化效应。如果 OOD 增益系统性地远小于开发集增益，"自我改进"更准确的名字是自适应 benchmark 工程。

**任务分数上升时，优化器变强了吗？** 每轮用全新的开发批次和盲测元任务，把 $J$ 和 $Q$ 分开追踪。固定优化器 + 任务分数持续上升，是完全正常的现象，不构成 $Q$ 上升的证据；只有允许在安全范围内修改优化器的条件出现显著为正的 $Q$ 斜率，第五节的强命题才开始有支撑。

**不可变安全内核的代价是什么？** 在无外网、合成凭据的一次性沙箱里，对比不可变内核、仅日志监控、完全可修改三组，同时测严重违规率和良性任务性能损失。如果内核能把违规压到预注册上限之下、性能损失在两个百分点以内，"安全边界外置"就从原则变成了可以引用的工程结论。

<figure class="he-figure">
  <img src="/assets/images/harness-engineering/causal-evaluation-matrix.svg" alt="Harness 研究的因果评测设计">
  <figcaption>图 3｜因果评测设计：随机析因、sham 对照、冻结的数据切分、多维结果向量。要识别的是架构效应，而不是更多 token 带来的表面收益。本文原创图。</figcaption>
</figure>

统计上有一个共同的坑值得点名：实际消耗的 token 和工具调用数是**处理的中介变量**——harness 正是通过改变它们起作用的——事后把它们当协变量"控制掉"会把真实效应也切掉。正确做法是预算随机化加 sham 对照。其余是标准配方：任务级配对运行、混合效应模型、多重校正、预注册最小实用效应。

### 七、自动科研：最严苛的压力测试 {#sec-science}

如果说 coding agent 是 harness 的主场，自动科研就是它的极限测试：文献、选题、实现、实验、验证、写作、评审，每一环都在考验第二节的全部模式。

2026 年有两个标志性结果发表在 Nature 上。AI Scientist 证明专家设计的 harness 可以把从提出研究想法到写出论文、通过自动评审的全流程跑通 <a href="#ref-27">[27]</a>——但细节必须说准：三篇 workshop 投稿中有一篇评审得分超过了接收线，研究团队按预先声明的方案在正式接收前撤稿，所以准确的说法是"达到过接收线"而非"已被接收"；论文同时如实记录了实现错误、想法偏浅和虚构引用的问题。Robin 则在真实生物医学问题上把文献检索、假设生成和数据分析连成实验反馈循环，在眼科药物再利用上产生了可验证的候选，但实验执行和精确 protocol 仍由人类完成 <a href="#ref-28">[28]</a>。**论文生产已经自动化了很多，科学发现没有。**

Benchmark 的刻度更冷静，附录有完整表格。几个数字值得在这里记住：PaperBench 上当时最好的 agent 得分约 21%，低于 ML 博士基线 <a href="#ref-29">[29]</a>；CORE-Bench 最难级别上当时最好的 agent 准确率仅约 21% <a href="#ref-39">[39]</a>；ScienceAgentBench 上最好的系统只能独立完成约三分之一任务 <a href="#ref-30">[30]</a>；RE-Bench 在 2 小时预算下 AI agent 的得分是人类专家的四倍，但 8 小时和 32 小时预算下人类反超 <a href="#ref-31">[31]</a>；MLE-bench 上最好的配置也只在 16.9% 的 Kaggle 竞赛中达到铜牌线 <a href="#ref-32">[32]</a>。

#### Trehan & Chopra 的六类失败模式

Trehan 与 Chopra 让 LLM 在最小脚手架下从研究想法走向论文：只有 `read_file`、`write_file`、`llm_search`、`list_files` 等基本工具，每个想法有独立工作区，agent 可以生成和读取文档作为上下文 <a href="#ref-33">[33]</a>。他们在三个领域（世界模型、多智能体 RL、AI 安全与对齐）各准备了 45–50 份高质量种子文档，由人类专家选出 4 个想法跑完整流水线，**四次尝试里只有一次执行到底**。他们归纳出六类反复出现的失败——下面逐类展开，因为每一类都对应 harness 设计的具体补丁：

**1. 偏向训练数据默认做法（bias toward training-data defaults）。** Agent 倾向使用旧库、过时命令、标准格式，或做出与当前仓库/数据集无关的假设。这不是"不会写代码"，而是**先验分布压过了现场证据**——harness 需要强制"先读仓库再行动"的 gate，并把依赖版本、数据 schema 写成可检索的结构化元数据，而不是指望模型从预训练里猜对。

**2. 执行压力下的实现漂移（implementation drift）。** 当提出的方法在技术上变复杂时，模型会悄悄退回更简单的常见方案，而不是坚持原提案。表面看实验"跑通了"，实际验证的是另一个假设。这需要 harness 在关键分支点做**方案-实现一致性检查**：把 proposal 文档和最终代码 diff 做自动对齐审计，而不只检查测试是否绿灯。

**3. 长程记忆退化（memory degradation）。** 长程项目会丢失关键细节，除非日志被写成持久文件。这正是第二节模式二存在的理由，但在科研场景里还不够——需要**分层的实验笔记本**：假设、protocol、超参、中间结果、负结果各自有固定槽位，检索时按任务阶段而不是按时间平铺。

**4. 过度乐观（over-optimism）。** 模型在噪声结果上宣布成功，与 Bubeck 等人观察到的"数值胶带"（numerical duct tape：给对不上的结果打补丁然后宣布胜利）如出一辙 <a href="#ref-34">[34]</a>。Harness 需要把"统计显著性/效应量/重复次数"写成发布前的硬门槛，并把 p-hacking 模式（反复调参直到显著）列入自动审计规则。

**5. 领域直觉不足（insufficient domain intelligence）。** 模型缺乏默会知识：预测实现复杂度、判断实验结果是否合理、知道该和哪些 baseline 比。这类失败不能单靠 prompt 解决，需要 harness 接入**领域工具链**（文献检索、标准数据集、领域特定的 linter）和外部检索，而不是让模型在封闭上下文里硬猜。

**6. 科学品味薄弱（weak scientific taste）。** 实验能跑通，但答的不是对的问题——新颖性、问题 framing、该追哪个意外结果、哪个失败值得重试，这些都属于"品味"。目前没有快速客观的验证器，这正是第八节第一个挑战的核心。

注意这是 $n=4$ 的定性案例研究，适合生成假设，不适合估计频率。但它把"自动科研失败在哪里"从笼统抱怨变成了可针对性设计的清单。

综合这些证据，"自动科研"应该拆成四级来谈：文档生产（已经相当强）、可复现实验（受控任务里部分做到）、可靠发现（个案，且离不开人）、方法学自我改进（尚无证据）。

### 八、走向 RSI 的七个开放挑战 {#sec-challenges}

Weng 原文在 Future Challenges 里列了七个瓶颈。我把它们展开成 harness 设计层面的具体问题——**本节机制梳理来自原文，具体工程化解读为本文扩展**。

**1. 弱而模糊的评估器。** 许多研究主张没有快速、精确的验证器；自我改进循环在评测可测量、客观的任务上最有效，就像 RL 需要清晰 reward 一样。研究品味、新颖性、长期科学价值难量化——它们混合了问题 framing、实验设计、以及对"哪个意外结果值得追、哪个失败值得重试"的判断。Harness 不能把最终计分器放在可优化环内；需要 held-out 测试、轨迹审计、关键节点的人工审查，以及**多验证器投票**（单元测试 + 静态分析 + 异模型评审）来降低单点博弈。

**2. 上下文与记忆生命周期。** Agent 越自主，记忆越膨胀。有用的 harness 要在长上下文局限之外管理记忆，同时最大化长程任务成功率。Weng 的类比是：人类终生维持记忆，上下文工程未来可能内化为智能的一部分，而不永远停留在"软件层技巧"。工程上这意味着**记忆要有遗忘、压缩、索引和权限策略**——不是无限 append，而是带生命周期的资产管理系统。

**3. 负结果。** 文献偏向成功案例，模型可能因此不擅长放弃假设、报告负结果、承认失败。研究 harness 应该让失败尝试易于保存——因为**从失败中收缩搜索空间，是最便宜的信息**。具体做法：每次实验无论成败都写入结构化日志，负结果进入可检索库，并在选题阶段主动检索"类似假设曾失败的原因"。

**4. 多样性坍缩。** 进化和 RL 循环倾向于利用已知高分模式，种群会塌缩成同一套路的变体。对开放式研究尤其危险——最好的路径在现有评估器下可能初期更差。需要**显式的多样性维护**：嵌入距离拒绝采样（ShinkaEvolve 已在代码进化里使用）、多目标 Pareto 保留、以及定期注入"探索性"候选。

**5. Reward hacking。** 自我改进循环优化的是给定信号。reward 来自单元测试就会过拟合测试；来自 judge 模型就会学会讨好 judge；来自 benchmark 分数就会挖掘 benchmark 漏洞。Gao 等人量化了 reward model 的 overoptimization <a href="#ref-25">[25]</a>；Skalse 等人则从理论上表明，对足够广泛的策略集合，构造完全不可博弈的代理奖励近乎不可能 <a href="#ref-26">[26]</a>。评估器和权限控制应位于进化环**之外**。

**6. 长期成功。** 外在优化环针对的是 rollout 之外、难以在训练沙盒里模拟的回报。Coding agent 已经提高了日常生产力，但许多优化目标仍太短视：能完成手边任务，却不一定保护由数百人共同维护的代码库的长期健康——可维护性、所有权边界、迁移成本、向后兼容、未来调试负担，标准 RLVR 式沙盒训练很少捕捉这些。Harness 需要**多时间尺度目标**：即时任务 reward + 仓库健康度指标（测试覆盖率趋势、依赖陈旧度、API 破坏风险）的加权或约束。

**7. 人的位置。** 人应该上移到栈的更高层，而不是被移出循环——在正确的时间、正确的抽象层提供监督，系统设计必须明确何时、如何设置人工触点。很多上述挑战都需要人类反馈和转向；我们是在为人类更好的未来构建技术，而不是反过来。可操作的含义是：**把人的时间花在验证器覆盖不了的判断上**（研究品味、安全红线、跨团队协调），把可自动化的检查下沉到 harness。

### 九、给构建者的最小清单 {#sec-practice}

把前面的内容压缩成可以直接落地的三条。

**每个工具调用都留下结构化事件**，至少包含：

<div class="he-eq">$$\{\texttt{task\_id}, \texttt{step\_id}, \texttt{role}, \texttt{tool}, \texttt{args}, \texttt{risk}, \texttt{result\_id}, \texttt{state\_delta}, \texttt{verifier\_result}, \texttt{cost}, \texttt{timestamp}\}$$</div>

后续步骤引用 `result_id` 而不是上一轮的口头转述——这是失败归因、回放和回归测试的全部基础。

**四道门控**：调用前查 schema、权限、预算；执行中限沙箱、超时、写锁；调用后记状态差和错误分类；发布前过 held-in 回归、held-out 盲测和安全攻击集。

**自我改进的候选永远不直接上生产**：offline replay → shadow mode → canary → champion/challenger → 自动回滚。严重安全违规是一票否决，不是可以被更高通过率抵消的扣分项。

### 结语 {#sec-end}

Harness engineering 正在把 agent 从"会生成文本的模型"变成"在约束下运行的可执行系统"，而这个系统的每一层——上下文、工作流、harness 代码、优化器——都已经被证明可以自动搜索。ACE 和 MCE 让上下文进化，ADAS 和 AFlow 搜索工作流，DGM、Self-Harness 和 Hyperagents 让系统修改自己或彼此，AlphaEvolve、ThetaEvolve 和 FunSearch 在可验证的领域摸到了真实发现。

但今天所有这些结果都停在同一条线之内：固定的模型、预定义的可编辑表面、给定的评估器。线的另一边——优化器自身随迭代变强、评估器覆盖模糊而重要的目标、安全边界在开放环境中依然守得住——每一项都还是开放问题。最可信的现状描述是一句话：**我们已经造出了会改进自己工具的系统，还没有造出会改进"改进过程"的系统。**

对研究者，这意味着最有价值的工作不是再刷高一个 benchmark，而是去测量那条线：$J$ 与 $Q$ 的分离、OOD 保留率、验证器的错误接受率、安全内核的真实代价。对工程师，结论更简单：把轨迹留成证据，把验证做成工具，把边界放在循环之外——这些今天就能做，而且无论 RSI 何时到来都不会白做。

### 附录：代表性 Benchmark {#sec-appendix}

下表整理 Weng 原文附录中的主要 benchmark，补充发表状态与关键数字。**表格为本文整理，数字以各论文原始报告为准。**

<div class="he-wrap">
<table class="he-table">
  <thead>
    <tr><th>Benchmark</th><th>测什么</th><th>规模 / 设置</th><th>代表性结果</th><th>引用</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>PaperBench</strong></td>
      <td>从零复现 ICML 论文（理解、编码、跑实验）</td>
      <td>20 篇 Spotlight/Oral；8,316 项 rubric，作者参与制定</td>
      <td>当时最好 agent（Claude 3.5 Sonnet）约 21%，低于 ML 博士</td>
      <td><a href="#ref-29">[29]</a></td>
    </tr>
    <tr>
      <td><strong>CORE-Bench</strong></td>
      <td>已发表论文的计算可复现性</td>
      <td>90 篇论文 → 270 任务；CS / 社科 / 医学；多难度级别</td>
      <td>最难级别上 GPT-4o 系列约 21%</td>
      <td><a href="#ref-39">[39]</a></td>
    </tr>
    <tr>
      <td><strong>ScienceAgentBench</strong></td>
      <td>数据驱动科学发现 agent</td>
      <td>44 篇论文 → 102 任务；四学科</td>
      <td>当时最好系统约 1/3 任务可独立完成</td>
      <td><a href="#ref-30">[30]</a></td>
    </tr>
    <tr>
      <td><strong>RE-Bench</strong></td>
      <td>前沿 ML 研发工程 vs 人类专家</td>
      <td>7 个开放环境；≤8×H100；71 次人类 8h 尝试</td>
      <td>2h：AI 4× 人类；8h/32h：人类反超</td>
      <td><a href="#ref-31">[31]</a></td>
    </tr>
    <tr>
      <td><strong>MLE-bench</strong></td>
      <td>离线 Kaggle 竞赛 ML 工程</td>
      <td>75 个竞赛；含资源缩放与污染分析</td>
      <td>o1-preview + AIDE 在 16.9% 竞赛达铜牌线</td>
      <td><a href="#ref-32">[32]</a></td>
    </tr>
    <tr>
      <td><strong>KernelBench</strong></td>
      <td>LLM 写 GPU kernel 的正确性与速度</td>
      <td>250 个 PyTorch 任务</td>
      <td>指标 fast_p = 正确且快于基线的占比</td>
      <td><a href="#ref-40">[40]</a></td>
    </tr>
  </tbody>
</table>
</div>

### 参考文献 {#sec-refs}

标注 [P3] 为正式期刊或会议论文集；[P1] 为预印本或技术报告，结论以最终发表版本为准。发表状态核验截止 2026/07/10。

<ol class="he-refs">
  <li id="ref-1">[经典] Good, I. J. <a href="https://doi.org/10.1016/S0065-2458(08)60418-0">Speculations Concerning the First Ultraintelligent Machine</a>. Advances in Computers, 1965.</li>
  <li id="ref-2">[P3] Yao et al. <a href="https://openreview.net/forum?id=WE_vluYUL-X">ReAct: Synergizing Reasoning and Acting in Language Models</a>. ICLR 2023.</li>
  <li id="ref-3">[P3] Yang et al. <a href="https://papers.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html">SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering</a>. NeurIPS 2024.</li>
  <li id="ref-4">[P3] Shinn et al. <a href="https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html">Reflexion: Language Agents with Verbal Reinforcement Learning</a>. NeurIPS 2023.</li>
  <li id="ref-5">[P3] Liu et al. <a href="https://aclanthology.org/2024.tacl-1.9/">Lost in the Middle: How Language Models Use Long Contexts</a>. TACL 2024.</li>
  <li id="ref-6">[P3] Wu et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html">LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory</a>. ICLR 2025.</li>
  <li id="ref-7">[P3] Wang et al. <a href="https://proceedings.mlr.press/v267/wang25bx.html">Agent Workflow Memory</a>. ICML 2025.</li>
  <li id="ref-8">[P3] Ruan et al. <a href="https://openreview.net/forum?id=GEcwtMk1uA">Identifying the Risks of LM Agents with an LM-Emulated Sandbox</a>. ICLR 2024 Spotlight.</li>
  <li id="ref-9">[P3] van der Weij et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/b5e5753b0a0e440a6d8dc7e143617cec-Abstract-Conference.html">AI Sandbagging: Language Models Can Strategically Underperform on Evaluations</a>. ICLR 2025.</li>
  <li id="ref-10">[P3] Khattab et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html">DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines</a>. ICLR 2024.</li>
  <li id="ref-11">[P3] Fernando et al. <a href="https://proceedings.mlr.press/v235/fernando24a.html">Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution</a>. ICML 2024.</li>
  <li id="ref-12">[P3] Agrawal et al. <a href="https://arxiv.org/abs/2507.19457">GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning</a>. ICLR 2026 Oral.</li>
  <li id="ref-13">[P3] Zhang et al. <a href="https://openreview.net/forum?id=eC4ygDs02R">Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models</a>. ICLR 2026.</li>
  <li id="ref-14">[P1] Ye et al. <a href="https://arxiv.org/abs/2601.21557">Meta Context Engineering via Agentic Skill Evolution</a>. arXiv, 2026.</li>
  <li id="ref-15">[P3] Hu, Lu &amp; Clune. <a href="https://openreview.net/forum?id=t9U3LW7JVX">Automated Design of Agentic Systems</a>. ICLR 2025.</li>
  <li id="ref-16">[P3] Zhang et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2025/file/5492ecbce4439401798dcd2c90be94cd-Paper-Conference.pdf">AFlow: Automating Agentic Workflow Generation</a>. ICLR 2025 Oral.</li>
  <li id="ref-17">[P1] Lee et al. <a href="https://arxiv.org/abs/2603.28052">Meta-Harness: End-to-End Optimization of Model Harnesses</a>. arXiv, 2026.</li>
  <li id="ref-18">[P1] Zhang et al. <a href="https://arxiv.org/abs/2606.09498">Self-Harness: Harnesses That Improve Themselves</a>. arXiv, 2026.</li>
  <li id="ref-19">[P3] Zhang et al. <a href="https://openreview.net/forum?id=pUpzQZTvGY">Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents</a>. ICLR 2026.</li>
  <li id="ref-20">[P1] Novikov et al. <a href="https://arxiv.org/abs/2506.13131">AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery</a>. Google DeepMind, 2025.</li>
  <li id="ref-21">[P3] Lange, Imajuku &amp; Cetin. <a href="https://openreview.net/forum?id=lKEdGCoDNC">ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution</a>. ICLR 2026.</li>
  <li id="ref-22">[P3] Romera-Paredes et al. <a href="https://www.nature.com/articles/s41586-023-06924-6">Mathematical Discoveries from Program Search with Large Language Models</a>. Nature, 2024.</li>
  <li id="ref-23">[P3] Zelikman et al. <a href="https://arxiv.org/abs/2310.02304">Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation</a>. COLM 2024.</li>
  <li id="ref-24">[P1] Hebbar et al. <a href="https://arxiv.org/abs/2605.27276">SIA: Self Improving AI with Harness &amp; Weight Updates</a>. arXiv, 2026.</li>
  <li id="ref-25">[P3] Gao, Schulman &amp; Hilton. <a href="https://proceedings.mlr.press/v202/gao23h.html">Scaling Laws for Reward Model Overoptimization</a>. ICML 2023.</li>
  <li id="ref-26">[P3] Skalse et al. <a href="https://openreview.net/forum?id=yb3HOXO3lX2">Defining and Characterizing Reward Gaming</a>. NeurIPS 2022.</li>
  <li id="ref-27">[P3] Lu et al. <a href="https://www.nature.com/articles/s41586-026-10265-5">Towards End-to-End Automation of AI Research</a>. Nature, 2026.</li>
  <li id="ref-28">[P3] Ghareeb et al. <a href="https://www.nature.com/articles/s41586-026-10652-y">A Multi-Agent System for Automating Scientific Discovery</a>. Nature, 2026.</li>
  <li id="ref-29">[P3] Starace et al. <a href="https://proceedings.mlr.press/v267/starace25a.html">PaperBench: Evaluating AI's Ability to Replicate AI Research</a>. ICML 2025.</li>
  <li id="ref-30">[P3] Chen et al. <a href="https://openreview.net/forum?id=6z4YKr0GK6">ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery</a>. ICLR 2025.</li>
  <li id="ref-31">[P3] Wijk et al. <a href="https://proceedings.mlr.press/v267/wijk25a.html">RE-Bench: Evaluating Frontier AI R&amp;D Capabilities of Language Model Agents against Human Experts</a>. ICML 2025 Spotlight.</li>
  <li id="ref-32">[P3] Chan et al. <a href="https://arxiv.org/abs/2410.07095">MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering</a>. ICLR 2025.</li>
  <li id="ref-33">[P1] Trehan &amp; Chopra. <a href="https://arxiv.org/abs/2601.03315">Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts</a>. arXiv, 2026.</li>
  <li id="ref-34">[P1] Bubeck et al. <a href="https://arxiv.org/abs/2511.16072">Early Science Acceleration Experiments with GPT-5</a>. arXiv, 2025.</li>
  <li id="ref-35">[P1] Kulikov et al. <a href="https://arxiv.org/abs/2606.25996">Autodata: An Agentic Data Scientist to Create High Quality Synthetic Data</a>. arXiv, 2026.</li>
  <li id="ref-36">[P1] Meng et al. <a href="https://arxiv.org/abs/2605.26340">ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence</a>. arXiv, 2026.</li>
  <li id="ref-37">[P1] Zhang et al. <a href="https://arxiv.org/abs/2603.19461">Hyperagents</a>. arXiv, 2026.</li>
  <li id="ref-38">[P1] Wang et al. <a href="https://arxiv.org/abs/2511.23473">ThetaEvolve: Test-time Learning on Open Problems</a>. arXiv, 2025.</li>
  <li id="ref-39">[P3] Siegel et al. <a href="https://arxiv.org/abs/2409.11363">CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark</a>. TMLR, 2024.</li>
  <li id="ref-40">[P3] Ouyang et al. <a href="https://arxiv.org/abs/2502.10517">KernelBench: Can LLMs Write Efficient GPU Kernels?</a>. ICML 2025.</li>
</ol>

<div class="he-source">
<strong>原始来源：</strong>Lilian Weng, "Harness Engineering for Self-Improvement," Lil'Log, 4 July 2026. <a href="https://lilianweng.github.io/posts/2026-07-04-harness/">原文链接</a>。本文第一至四节的方法机制解读以原文及各论文原始文献为依据；分层框架、J/Q 判别、第六节实验设计、第八节工程化解读与全部图示为本文扩展。预印本结论以最终发表版本为准。
</div>
