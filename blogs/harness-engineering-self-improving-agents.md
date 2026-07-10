---
layout: page
permalink: /blogs/harness-engineering-self-improving-agents/index.html
title: Harness Engineering：自我改进智能体真正的系统边界
description: 基于 Lilian Weng 的 Harness Engineering 文章，重新梳理 agent harness 的分层、优化对象与证据边界，并提出可证伪的递归自我改进定义、因果实验和安全评测框架。
---

<style>
.he-lead{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1.05rem;border-radius:10px;margin:1rem 0 1.25rem}
.he-lead p{margin:.35rem 0;color:#405160;line-height:1.82}
.he-callout{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem 1.05rem;margin:1rem 0 1.25rem}
.he-callout p{margin:.15rem 0;color:#405160;line-height:1.78}
.he-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.25rem}
.he-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem}
.he-card h3{margin:.05rem 0 .5rem;color:#2f4756;font-size:1.02rem}
.he-card p{margin:0;color:#536572;line-height:1.76}
.he-wrap{overflow-x:auto;margin:1rem 0 1.25rem}
.he-table{width:100%;border-collapse:collapse;min-width:880px;font-size:.93rem}
.he-table th,.he-table td{border-bottom:1px solid #dde4ea;padding:.72rem .58rem;text-align:left;vertical-align:top}
.he-table th{color:#34495a;background:#f8fafc}
.he-table td{color:#4b5c69;line-height:1.68}
.he-eq{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:.9rem 1rem;margin:1rem 0 1.25rem;overflow-x:auto}
.he-eq code{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:#2f4756;font-size:.92rem;white-space:nowrap}
.he-figure{margin:1.35rem 0 1.45rem}
.he-figure img{display:block;width:100%;height:auto;border-radius:10px;border:1px solid #dce5ec;background:#050507}
.he-figure figcaption{color:#667784;font-size:.86rem;line-height:1.65;margin-top:.55rem;text-align:center}
.he-badges{display:flex;flex-wrap:wrap;gap:.42rem;margin:.75rem 0}
.he-badge{display:inline-block;border:1px solid #dce5ec;border-radius:999px;padding:.18rem .56rem;font-size:.8rem;color:#445a68;background:#fbfcfe}
.he-badge.peer{border-color:#9fc7b8;color:#24634e;background:#f5fbf8}
.he-badge.pre{border-color:#e3cda2;color:#725621;background:#fffaf0}
.he-list li{margin:.38rem 0;line-height:1.75;color:#42586a}
.he-refs{font-size:.9rem;line-height:1.72;color:#56636f}
.he-refs li{margin:.48rem 0}
.he-source{margin-top:1.4rem;padding:1rem;border:1px solid #dce5ec;border-radius:10px;background:#fbfcfe;color:#56636f;font-size:.92rem;line-height:1.8}
@media (max-width:840px){.he-grid{grid-template-columns:1fr}.he-table{min-width:760px}}
</style>

## Harness Engineering：自我改进智能体真正的系统边界

> 更新时间：2026/07/10  
> 文章定位：研究型技术博客 + 方法学批判 + 可检验研究方案。  
> 关键词：agent harness, recursive self-improvement, context engineering, workflow search, auto-research, causal evaluation

<div class="he-source">
本文以 Lilian Weng 的文章 <a href="https://lilianweng.github.io/posts/2026-07-04-harness/">Harness Engineering for Self-Improvement</a> 为起点。原文作者为 Lilian Weng，发表于 2026 年 7 月 4 日。本文不是逐句翻译，而是保留其核心问题，重新组织中文论证，并补充同行评审文献、证据分级、专业机制图与可证伪的研究设计。文中的扩展判断与研究方案由本文负责，不代表原作者观点。
</div>

模型能力越来越强之后，一个反常识事实正在变得清楚：**真正决定 agent 能否长期、可靠地完成任务的，不只是基础模型，还包括模型外部那层执行系统。**

这层系统负责把目标变成可执行动作：选择上下文，保存状态，调用工具，调度子代理，检查结果，控制权限，记录轨迹，并在失败后决定重试、回滚还是停止。它就是这里所说的 **harness**。

<div class="he-lead">
  <p><strong>核心判断：</strong>未来几年最可操作的“自我改进”，很可能首先发生在模型外部：prompt、context、memory、workflow、tool interface、verifier 与 harness code 被持续优化；模型权重不一定立即改变。</p>
  <p><strong>但必须降温：</strong>一次 benchmark 提分只能说明当前 harness 在当前评测上更好，不能自动证明系统获得了递归自我改进能力，更不能证明它会稳定走向更高智能。</p>
</div>

理解这个领域，最重要的是避免三组混淆：

1. **任务分数提升**不等于**通用能力提升**。
2. **harness 被改进**不等于**优化器越来越会改进 harness**。
3. **自动生成论文**不等于**自动完成科学发现**。

下面从系统边界、优化层级、证据强度和实验方法四个角度重新梳理。

### 一、Harness 到底是什么

早期 agent 常被概括成：

<div class="he-eq"><code>Agent = LLM + Memory + Tools + Planning + Action</code></div>

这个定义适合解释组件，却不足以解释一个真实系统如何运行。现代 harness 更接近 runtime 或操作系统：它规定模型看到什么、能做什么、如何保存状态、怎样判断成功，以及哪些边界不能跨越。

对任务 <code>x</code>，可以把一次执行写成：

<div class="he-eq"><code>轨迹 τ ~ p(τ | 任务 x, 基础模型 Mθ, Harness Hφ, 安全内核 Kκ, 预算 B)</code></div>

其中：

- <code>Mθ</code> 是基础模型及其原生推理、生成和工具协议能力；
- <code>Hφ</code> 是可以优化的上下文、编排、执行、验证与元优化逻辑；
- <code>Kκ</code> 是不可由系统自行修改的权限、沙箱、预算、审计、隐藏评测和回滚机制；
- <code>B</code> 是 token、工具调用、时间、费用与并发预算；
- <code>τ</code> 不只是最终回答，而是包含动作、工具结果、状态变化和验证证据的完整轨迹。

<figure class="he-figure">
  <img src="/assets/images/harness-engineering/layered-harness-boundary.svg" alt="分层 Agent Harness 与不可变安全边界">
  <figcaption>图 1｜一个可研究、可审计的 harness 应明确区分可优化层与不可自修改的可信计算边界。本文原创图。</figcaption>
</figure>

这种分层比“模型加几个工具”更准确，也解释了为什么同一个模型放进不同 coding agent 后，行为会明显不同。<a href="#ref-1">ReAct [1]</a> 证明了交错推理与环境动作的价值；<a href="#ref-6">SWE-agent [6]</a> 更直接地表明，专门设计的 Agent-Computer Interface 会显著改变同一模型在软件工程任务中的表现。

但这里需要克制：现有工作大多是在固定模型、固定任务上比较少量接口。它们支持“harness 设计很重要”，还不足以支持“harness 与模型智能同等重要”这一更强结论。要回答后者，需要真正的 <code>模型 × harness × 预算 × 任务</code> 析因实验。

### 二、六个关键设计模式

<div class="he-callout">
  <p><strong>来源边界：</strong>可执行循环、外部持久状态与子代理/后台任务承接自 Weng 原文；artifact 生命周期、独立验证器和不可变安全内核是本文结合后续文献做的方法学扩展。</p>
</div>

<div class="he-grid">
  <div class="he-card">
    <h3>1. 可执行循环，而不是静态 prompt</h3>
    <p>系统需要显式的 plan → act → observe → verify → revise 循环，并带有停止条件、预算和失败出口。<a href="#ref-2">Reflexion [2]</a> 展示了轨迹、反馈和语言反思的作用，但循环本身仍须可观测，否则“反思”只是一段无法核验的自然语言。</p>
  </div>
  <div class="he-card">
    <h3>2. 持久状态，而不是无限上下文</h3>
    <p>日志、代码差异、实验结果和中间 artifact 应外置保存，再按需检索。TACL 的 <a href="#ref-3">Lost in the Middle [3]</a> 与 ICLR 2025 的 <a href="#ref-4">LongMemEval [4]</a> 都说明，窗口更长不等于信息利用更可靠。</p>
  </div>
  <div class="he-card">
    <h3>3. Artifact 是一等公民</h3>
    <p>代码、测试结果、数据、论文草稿和状态快照不能只存在于聊天记录。它们要有路径、版本、哈希、来源和生命周期，才能被重放、比较与审计。</p>
  </div>
  <div class="he-card">
    <h3>4. 子代理需要进程管理</h3>
    <p>并行搜索只有在任务可分解、状态可隔离时才有价值。父代理应能启动、观察、取消和合并后端任务；共享写状态则需要锁、事务或分支隔离。</p>
  </div>
  <div class="he-card">
    <h3>5. 验证器不能只是模型自评</h3>
    <p>优先使用测试、schema、数据库状态、策略约束等确定性证据。LLM judge 可以补充语义判断，但同一模型基于同一轨迹自评，容易继承同一盲点。</p>
  </div>
  <div class="he-card">
    <h3>6. 安全边界位于优化循环之外</h3>
    <p>身份、凭据、工具 allowlist、隐藏评测、审计日志、更新签名与 kill switch 不应由被优化系统自行批准修改。<a href="#ref-24">ToolEmu [24]</a> 与 <a href="#ref-25">AI Sandbagging [25]</a> 分别说明高风险工具失效和评测失真的可能性；性能收益不能抵消严重安全违规。</p>
  </div>
</div>

关于“文件系统是长期记忆”的说法也应更精确。文件有简单、透明、易版本化的工程优势，但现有研究并没有证明普通文件系统普遍优于数据库、向量检索、事件日志或混合记忆。<a href="#ref-4">LongMemEval [4]</a> 更支持把记忆拆成索引、检索与阅读问题；<a href="#ref-5">Agent Workflow Memory [5]</a> 则说明，从历史轨迹中提炼可复用的程序性 workflow 可能比原样堆积日志更有效。

### 三、Harness 优化正在优化什么

过去三年的变化不是“prompt engineering 消失了”，而是优化对象在向更高层移动。

<div class="he-wrap">
<table class="he-table">
  <thead>
    <tr>
      <th>优化层级</th>
      <th>典型对象</th>
      <th>代表研究</th>
      <th>当前证据边界</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Prompt 与示例</td>
      <td>指令、few-shot、模块 prompt、变异 prompt</td>
      <td><a href="#ref-7">DSPy [7]</a>、<a href="#ref-8">Promptbreeder [8]</a>、<a href="#ref-13">GEPA [13]</a></td>
      <td>可以系统优化文本组件；不等于工具执行、权限和状态管理同时得到优化</td>
    </tr>
    <tr>
      <td>Context 与 Memory</td>
      <td>检索、压缩、playbook、workflow memory</td>
      <td><a href="#ref-5">Agent Workflow Memory [5]</a>、<a href="#ref-12">ACE [12]</a>、<a href="#ref-29">MCE [29]</a></td>
      <td>ACE 已由 ICLR 2026 接收；MCE 截至本文写作时仍是预印本</td>
    </tr>
    <tr>
      <td>Workflow</td>
      <td>节点、边、角色、控制流、重试和停止条件</td>
      <td><a href="#ref-10">ADAS [10]</a>、<a href="#ref-11">AFlow [11]</a></td>
      <td>在受控 benchmark 上可超过部分手工 workflow；跨领域稳定性仍待检验</td>
    </tr>
    <tr>
      <td>Harness Code</td>
      <td>执行器、上下文逻辑、工具策略、完整 agent repository</td>
      <td><a href="#ref-14">DGM [14]</a>、<a href="#ref-26">Meta-Harness [26]</a>、<a href="#ref-27">Self-Harness [27]</a></td>
      <td>DGM 已由 ICLR 2026 接收；后两项仍是近期预印本，且主要依赖少量 benchmark</td>
    </tr>
    <tr>
      <td>Optimizer</td>
      <td>负责生成、筛选和改写候选方案的 improver</td>
      <td><a href="#ref-9">STOP [9]</a>、<a href="#ref-8">Promptbreeder [8]</a></td>
      <td>已证明优化器可以成为搜索对象；弱模型在递归迭代中也可能退化</td>
    </tr>
    <tr>
      <td>Harness + 权重</td>
      <td>在外层系统修改和参数更新之间分配反馈</td>
      <td><a href="#ref-30">SIA [30]</a>、自博弈与测试时学习</td>
      <td>方向重要，但现有结果容易混入更强 meta-model、训练预算和 baseline 选择等混杂</td>
    </tr>
  </tbody>
</table>
</div>

这不是一条“越往后必然越先进”的单向阶梯。优化对象越大，表达能力越强，搜索空间、评测成本、回归风险和安全攻击面也越大。代码确实是一种通用的 agent 表示，但“可以修改所有代码”通常不是优势，而是缺少边界。

可自动计算 fitness 的程序问题提供了更强的搜索证据：<a href="#ref-15">ShinkaEvolve [15]</a> 研究了更高样本效率的程序进化，<a href="#ref-16">FunSearch [16]</a> 在 Nature 展示了由程序搜索产生数学发现的案例，<a href="#ref-28">AlphaEvolve [28]</a> 也报告了大规模算法与代码优化结果。但这些证据仍不能直接外推到科学品味、因果解释和长期研究价值等模糊目标。

### 四、为什么 Harness 优化还不是严格的递归自我改进

Good 在 1965 年提出“超智能机器”能够设计更好的机器这一经典设想 <a href="#ref-31">[31]</a>。许多现代论文则把固定模型下的 agent 自修改称为 self-improvement。工程上这样说可以理解，科学上却需要更严格的操作定义。**下面的 F/J/Q 形式化和三级分类是本文提出的操作性扩展，不是 Weng 原文的定义。**

先定义当前 harness 在任务分布 <code>D</code> 上的结果向量：

<div class="he-eq"><code>F<sub>D</sub>(φ) = (能力, 可靠性, −成本, 泛化, −安全风险, −人工介入)</code></div>

向量不能直接比较大小。主分析应报告 Pareto 前沿；如果实验必须选择单一候选，则在看结果前预注册标准化函数 <code>z</code> 和权重 <code>w</code>，定义标量效用：

<div class="he-eq"><code>J<sub>D</sub>(φ) = w<sup>T</sup> z(F<sub>D</sub>(φ))，且 P(严重安全违规) ≤ ε、Cost(φ) ≤ B</code></div>

如果一次搜索得到 <code>J(φ<sub>r+1</sub>) &gt; J(φ<sub>r</sub>)</code>，我们只能说当前 harness 被改进。要判断“系统是否越来越会改进自己”，还需要评价元优化器 <code>Uψ</code>：

<div class="he-eq"><code>Q(ψ) = E[(J(Πκ Uψ(φ, 轨迹)) − J(φ)) / 搜索成本]</code></div>

<code>Πκ</code> 表示安全投影：违反权限、预算、审计或隐藏评测完整性的候选直接拒绝。

<figure class="he-figure">
  <img src="/assets/images/harness-engineering/optimization-vs-rsi.svg" alt="Harness 优化与递归自我改进的区别">
  <figcaption>图 2｜只有预注册标量效用 J 上升，证明的是有界 harness 优化；优化能力 Q 也在全新元任务上持续上升，才接近更强的递归自我改进定义。本文原创图。</figcaption>
</figure>

我建议把相关论断分成三级：

<div class="he-wrap">
<table class="he-table">
  <thead>
    <tr>
      <th>级别</th>
      <th>可以声称什么</th>
      <th>最低证据要求</th>
      <th>典型例子</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>A. 任务适配</td>
      <td>当前系统在开发任务上得分更高</td>
      <td>固定模型、清晰预算、可重复评测</td>
      <td>prompt tuning、context 更新、workflow 搜索</td>
    </tr>
    <tr>
      <td>B. 有界 Harness 自我改进</td>
      <td>系统生成并接受了能提高 held-out 表现的自身修改</td>
      <td>无人工语义编辑、独立验证、回归测试、旧任务保持</td>
      <td>DGM、Self-Harness、Meta-Harness 一类方法</td>
    </tr>
    <tr>
      <td>C. 递归自我改进</td>
      <td>优化器本身越来越擅长产生有效改进</td>
      <td>至少三轮、固定搜索预算、全新元任务、Q 的轮次斜率置信区间排除零、无 OOD 与安全退化</td>
      <td>目前仍缺少公认的强证据</td>
    </tr>
  </tbody>
</table>
</div>

这一区分能避免把 <a href="#ref-14">DGM [14]</a> 在固定模型、预定义代码表面和 benchmark 上的进化，直接外推为开放式智能爆炸。它是一项重要结果，但更准确的名称是 **bounded empirical self-improvement**：有边界、可评测的经验性自我改进。

### 五、现有证据真正支持了什么

#### 已有较强证据

1. **接口和运行时设计会改变 agent 表现。** <a href="#ref-6">SWE-agent [6]</a> 在 NeurIPS 2024 系统研究中直接比较了 ACI 设计；这比产品体验或个案更接近因果证据。
2. **文本、示例和 workflow 可以被程序化优化。** <a href="#ref-7">DSPy [7]</a>、<a href="#ref-8">Promptbreeder [8]</a>、<a href="#ref-10">ADAS [10]</a>、<a href="#ref-11">AFlow [11]</a>、<a href="#ref-13">GEPA [13]</a> 分别覆盖了编译、进化、代码搜索、MCTS 与轨迹反思。
3. **长上下文不等于可靠记忆。** <a href="#ref-3">Lost in the Middle [3]</a>、<a href="#ref-4">LongMemEval [4]</a> 与 <a href="#ref-5">Agent Workflow Memory [5]</a> 共同支持选择性检索、结构化状态和程序性经验复用。
4. **递归结构不保证单调变好。** <a href="#ref-9">STOP [9]</a> 报告较弱模型在迭代中可能退化，说明基础能力、搜索器和 evaluator 都是必要条件。
5. **优化 proxy 会产生 Goodhart 风险。** <a href="#ref-22">Reward Model Overoptimization [22]</a> 与 <a href="#ref-23">Reward Gaming [23]</a> 表明，持续优化不完美奖励可能损害真实目标。
6. **自动科研仍有明显能力缺口。** <a href="#ref-19">PaperBench [19]</a>、<a href="#ref-20">ScienceAgentBench [20]</a> 与 <a href="#ref-21">RE-Bench [21]</a> 都显示，短时局部优势不能替代长时规划、复现和专家判断。

#### 仍然证据不足

1. Harness 与基础模型对最终能力的相对贡献，目前缺少大规模析因研究。
2. 文件系统是否是最优长期记忆，没有普遍证据。
3. 单个公开 benchmark 上的连续提分，不能证明跨任务、跨模型、跨 harness 泛化。
4. <a href="#ref-28">AlphaEvolve [28]</a> 在可自动计算 fitness 的程序搜索中很强，但不能直接证明对科学品味、因果解释或长期研究价值同样有效。
5. AI Scientist 能运行论文生产流水线，不等于已经可靠完成科学发现。
6. Self-Harness、Meta-Harness、MCE、SIA 等近期工作仍需要同行评审、独立复现和更广任务覆盖。

为避免把“题目相关”误写成“强证据”，本文采用双轴分级：

<div class="he-wrap">
<table class="he-table">
  <thead>
    <tr>
      <th>维度</th>
      <th>等级</th>
      <th>含义</th>
      <th>建议写法</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>发表状态 P</td>
      <td>P3 / P2 / P1 / P0</td>
      <td>正式 proceedings 或期刊 / 已确认接收 / 预印本 / 博客与产品材料</td>
      <td>预印本必须写“作者报告”，不能写“研究已证明”</td>
    </tr>
    <tr>
      <td>支撑强度 E</td>
      <td>E3 / E2 / E1 / E0</td>
      <td>直接且有 held-out 对照 / 相关但范围有限 / 背景动机 / 不足</td>
      <td>同时注明单 benchmark、合成环境、专有模型、LLM judge 等限制</td>
    </tr>
  </tbody>
</table>
</div>

### 六、把这个方向写成更好的科学问题

现在很多研究的基本叙事是：“让 agent 修改自己的 harness，然后 benchmark 上升。”这个叙事太容易成立，也太难排除混杂。更有价值的问题应该允许实验否定。**RQ1–RQ7 及图 3 均为本文提出的研究方案，不是 Weng 原文内容。**

#### RQ1：收益来自架构，还是来自更多计算

把 L1 上下文、L2 编排、L4 验证做成 <code>2³</code> 析因设计；所有组固定 token、工具调用和时间预算，并增加一个消耗同等预算但不改变决策的 sham 对照。

**可证伪假设：**固定预算后，编排与验证仍能在 IID 和 OOD 上产生超过预注册最小效应的提升。

#### RQ2：独立验证器是否真的减少静默错误

比较无验证、同代理自评、独立同模型验证、独立异模型验证。不能只看 pass rate，还要同时报告 false acceptance、false rejection、恢复率、尾部风险与延迟。

**可证伪假设：**独立 verifier 显著降低错误接受率，并且不是通过全面拒绝任务来伪装安全。

#### RQ3：公开 benchmark 提分能保留多少

在公开开发集优化，在仓库级、论文级、时间外和新任务族上盲测。主检验不使用不稳定的简单比值，而是比较预注册的标准化效应 <code>g<sub>dev</sub></code> 与 <code>g<sub>OOD</sub></code>，检验“优化方法 × 数据切分”的交互项。

<div class="he-eq"><code>H<sub>0</sub>: g<sub>OOD</sub> − g<sub>dev</sub> = 0；同时报告差值、置信区间与任务级 bootstrap</code></div>

只有当 <code>g<sub>dev</sub></code> 为正且超过预注册最小效应时，才把 <code>R = g<sub>OOD</sub>/g<sub>dev</sub></code> 作为描述性保持率，并报告置信区间；本文不预设普适的 0.5 阈值。

#### RQ4：任务变强后，优化器是否也变强

每轮都使用全新的开发批次和盲测元任务，分别追踪 <code>J</code> 与 <code>Q</code>。固定优化器即使持续提高任务分数，也不能算优化能力增长。

**可证伪假设：**只有允许在安全范围内修改元优化器的条件，才会出现显著为正的 <code>Q</code> 斜率。

#### RQ5：单一 pass rate 是否诱导低质量策略

比较只优化 pass rate、成本约束优化和 Pareto 多目标优化。除成功率外，记录 token、工具调用、墙钟时间、人工分钟、安全违规、回退率和 Pareto hypervolume。

**可证伪假设：**只优化 pass rate 的候选，会在 OOD、成本或安全上被多目标方案支配。

#### RQ6：哪一层 Harness 最能跨模型迁移

在源模型上分别优化 prompt、context、workflow、工具协议与 verifier，再冻结迁移到至少两个其他模型家族。

**可证伪假设：**工具协议、状态管理和验证策略的迁移率，高于模型特定 prompt、记忆压缩和路由策略。

#### RQ7：不可变安全内核能否阻断自修改攻击

在无外网、合成凭据的一次性沙箱中，对比不可变内核、仅日志监控和完全可修改三组。

**可证伪假设：**可信内核把严重违规率压到预注册上限以下，同时良性任务性能下降不超过 2 个百分点的非劣界值。

<figure class="he-figure">
  <img src="/assets/images/harness-engineering/causal-evaluation-matrix.svg" alt="Harness 研究的因果评测矩阵">
  <figcaption>图 3｜推荐的随机析因、隐藏切分和多目标评测设计。真正要识别的是架构效应，而不是更多 token、更多工具调用或更多试错带来的表面收益。本文原创图。</figcaption>
</figure>

评测矩阵至少应覆盖八个维度：

<div class="he-wrap">
<table class="he-table">
  <thead>
    <tr>
      <th>维度</th>
      <th>核心指标</th>
      <th>为什么不能省略</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>任务能力</td><td>pass@1、连续任务分数、子目标完成率</td><td>描述当前系统能做什么</td></tr>
    <tr><td>可靠性</td><td>重复运行方差、最差十分位、CVaR、flaky rate</td><td>均值会掩盖长尾失败</td></tr>
    <tr><td>效率</td><td>token、工具调用、时间、费用、能耗代理</td><td>高分可能只是更贵</td></tr>
    <tr><td>泛化</td><td>IID、OOD、时间外、跨模型、旧任务保持</td><td>区分学习与 benchmark 过拟合</td></tr>
    <tr><td>改进能力</td><td>Q、单位搜索成本增益、有效修改比例</td><td>区分对象层提分与元优化提升</td></tr>
    <tr><td>自主程度</td><td>人工介入次数、人工分钟、语义编辑量</td><td>避免把人类调参算成系统自我改进</td></tr>
    <tr><td>安全</td><td>严重违规、越权、泄密、误阻断、回滚时间</td><td>安全必须是硬约束而非平均奖励</td></tr>
    <tr><td>评测完整性</td><td>测试污染、reward hacking、审计日志完整率</td><td>优化器也可能学会优化评测漏洞</td></tr>
  </tbody>
</table>
</div>

统计上，应以任务为聚类单元做配对运行，二元结果使用混合效应 logistic 模型，连续结果使用稳健混合模型或分层 bootstrap，并对多重假设做 Holm 校正。最小实用效应、数据切分和停止规则应在实验前预注册。

### 七、自动科研是 Harness 的压力测试，不是最终证明

自动科研把 harness 的所有困难压在一个任务里：文献检索、问题提出、代码实现、实验执行、证据审查、写作、同行评议和长期记忆。

<a href="#ref-17">AI Scientist [17]</a> 于 2026 年发表在 Nature，说明专家设计的系统可以把选题、实验、写作和评审串成端到端流水线；但其结果也包含实现错误、浅层想法和虚构引用。三篇 workshop 投稿中，一篇评分超过接收线，但研究团队依照预设方案撤稿，因此不应写成已获正式接收。<a href="#ref-18">Robin [18]</a> 同样发表于 Nature，它在眼科药物再利用案例中把文献、假设和数据分析连成闭环，但实验执行、精确 protocol 和部分分析仍需要人类。

基准也给出了更克制的图景：

- <a href="#ref-19">PaperBench [19]</a> 使用 20 篇 ICML 论文和 8,316 个作者参与制定的评分项；论文发布时最佳 agent 平均约 21%，低于 ML 博士基线。
- <a href="#ref-20">ScienceAgentBench [20]</a> 从 44 篇同行评审论文中抽取 102 个数据驱动任务；当时最佳系统只能完成约三分之一。
- <a href="#ref-21">RE-Bench [21]</a> 发现 AI 在 2 小时预算下可以超过人类，但人类在更长时间预算下收益更好，并在 8 小时和 32 小时条件下反超。

因此，“自动科研”至少应分成四级：

1. **文档生产**：能搜索、整理和写出结构完整的论文。
2. **可复现实验**：代码、数据、配置和结论可以由第三方重跑。
3. **可靠发现**：假设新颖、实验能区分替代理论、结果可复现。
4. **方法学自我改进**：系统不仅产出发现，还能在全新领域持续提高自己的研究方法。

现有证据最稳固的是文档生产，以及受控任务中的部分实验执行；对完整第三方复现、可靠发现和方法学自我改进，证据仍不足。

更值得研究的自动科研问题不是“能否再生成一篇论文”，而是：

- 如何为新颖性、因果解释和长期价值构造不过度可博弈的 evaluator？
- 如何保存失败实验和负结果，让系统知道何时放弃假设，而不是继续“数值胶带”式修补？
- 如何阻止进化与强化学习把候选群体压缩成同一种高分套路？
- 如何检测实现漂移：代码最终运行的算法是否仍是最初声称的方法？
- 人类应在问题选择、风险审批、异常结果解释和最终结论中的哪个时点介入？

“科学品味”也不应停留在不可测的口号。可以用盲法专家成对比较、跨时间复现、信息增益、替代理论排除能力和后续实验价值，把它拆成多个不完美但可审计的 proxy；再明确承认这些 proxy 仍会受到 Goodhart 效应影响。

### 八、一个可落地的 Harness 最小协议

如果把上述研究结论落到 coding agent 或 research agent，我会要求每个工具调用至少形成这样的事件：

<div class="he-eq"><code>{task_id, step_id, role, tool, args, risk, preconditions, result_id, state_delta, verifier_result, cost, timestamp}</code></div>

随后执行四层门控：

1. **调用前**：schema、语义、权限、预算和用户确认。
2. **执行中**：沙箱、超时、重试、幂等键、写锁和资源限制。
3. **调用后**：状态差、artifact、测试结果和错误分类。
4. **发布前**：held-in 回归、held-out 盲测、OOD、安全攻击集与人工审批。

自我改进候选不应直接替换生产系统。更稳的流程是：

<div class="he-eq"><code>offline replay → shadow mode → canary → champion/challenger → 自动回滚</code></div>

严重安全违规是淘汰条件，不是可以被更高成功率抵消的一个普通负分项。

### 结论

Harness Engineering 的价值，不是给 prompt engineering 换一个更大的名字，而是把 agent 从“会生成文本的模型”重新定义为“在约束下运行的可执行系统”。

这个系统真正值得优化的对象包括上下文、记忆、workflow、工具协议、验证器、代码和元优化器。现有顶会顶刊研究表明，其中若干层在特定模型、任务、benchmark 与预算下可以被自动搜索并带来有界收益；同时，长上下文失效、benchmark 过拟合、proxy reward、自动科研失败与安全攻击也说明，优化循环越强，外部边界越重要。

<div class="he-callout">
  <p><strong>最重要的研究问题不是“agent 能不能修改自己”，而是“在什么证据、预算和安全边界下，这种修改能跨任务持续提高，并且不会把评测漏洞误当成进步”。</strong></p>
</div>

在这个标准下，今天最可信的结论是：我们已经看到有界的 harness 自我改进；真正的递归自我改进，仍然是一个需要严格定义、因果实验和长期盲测才能回答的开放问题。

### 参考文献

<div class="he-badges">
  <span class="he-badge peer">P3：正式期刊/会议</span>
  <span class="he-badge pre">P1：预印本/技术报告</span>
</div>

<ol class="he-refs">
  <li id="ref-1"><strong>[P3]</strong> Yao et al. <a href="https://openreview.net/forum?id=WE_vluYUL-X">ReAct: Synergizing Reasoning and Acting in Language Models</a>. ICLR, 2023.</li>
  <li id="ref-2"><strong>[P3]</strong> Shinn et al. <a href="https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html">Reflexion: Language Agents with Verbal Reinforcement Learning</a>. NeurIPS, 2023.</li>
  <li id="ref-3"><strong>[P3]</strong> Liu et al. <a href="https://aclanthology.org/2024.tacl-1.9/">Lost in the Middle: How Language Models Use Long Contexts</a>. TACL, 2024.</li>
  <li id="ref-4"><strong>[P3]</strong> Wu et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html">LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory</a>. ICLR, 2025.</li>
  <li id="ref-5"><strong>[P3]</strong> Wang et al. <a href="https://proceedings.mlr.press/v267/wang25bx.html">Agent Workflow Memory</a>. ICML, 2025.</li>
  <li id="ref-6"><strong>[P3]</strong> Yang et al. <a href="https://papers.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html">SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering</a>. NeurIPS, 2024.</li>
  <li id="ref-7"><strong>[P3]</strong> Khattab et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html">DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines</a>. ICLR, 2024.</li>
  <li id="ref-8"><strong>[P3]</strong> Fernando et al. <a href="https://proceedings.mlr.press/v235/fernando24a.html">Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution</a>. ICML, 2024.</li>
  <li id="ref-9"><strong>[P3]</strong> Zelikman et al. <a href="https://colmweb.org/2024/AcceptedPapers.html">Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation</a>. COLM Spotlight, 2024.</li>
  <li id="ref-10"><strong>[P3]</strong> Hu, Lu &amp; Clune. <a href="https://openreview.net/forum?id=t9U3LW7JVX">Automated Design of Agentic Systems</a>. ICLR, 2025.</li>
  <li id="ref-11"><strong>[P3]</strong> Zhang et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2025/file/5492ecbce4439401798dcd2c90be94cd-Paper-Conference.pdf">AFlow: Automating Agentic Workflow Generation</a>. ICLR Oral, 2025.</li>
  <li id="ref-12"><strong>[P3]</strong> Zhang et al. <a href="https://openreview.net/forum?id=eC4ygDs02R">Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models</a>. ICLR, 2026.</li>
  <li id="ref-13"><strong>[P3]</strong> Agrawal et al. <a href="https://iclr.cc/virtual/2026/oral/10009494">GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning</a>. ICLR Oral, 2026.</li>
  <li id="ref-14"><strong>[P3]</strong> Zhang et al. <a href="https://openreview.net/forum?id=pUpzQZTvGY">Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents</a>. ICLR, 2026.</li>
  <li id="ref-15"><strong>[P3]</strong> Lange, Imajuku &amp; Cetin. <a href="https://openreview.net/forum?id=lKEdGCoDNC">ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution</a>. ICLR, 2026.</li>
  <li id="ref-16"><strong>[P3]</strong> Romera-Paredes et al. <a href="https://www.nature.com/articles/s41586-023-06924-6">Mathematical Discoveries from Program Search with Large Language Models</a>. Nature, 2024.</li>
  <li id="ref-17"><strong>[P3]</strong> Lu et al. <a href="https://www.nature.com/articles/s41586-026-10265-5">Towards End-to-End Automation of AI Research</a>. Nature, 2026.</li>
  <li id="ref-18"><strong>[P3]</strong> Ghareeb et al. <a href="https://www.nature.com/articles/s41586-026-10652-y">A Multi-Agent System for Automating Scientific Discovery</a>. Nature, 2026.</li>
  <li id="ref-19"><strong>[P3]</strong> Starace et al. <a href="https://proceedings.mlr.press/v267/starace25a.html">PaperBench: Evaluating AI’s Ability to Replicate AI Research</a>. ICML, 2025.</li>
  <li id="ref-20"><strong>[P3]</strong> Chen et al. <a href="https://openreview.net/forum?id=6z4YKr0GK6">ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery</a>. ICLR, 2025.</li>
  <li id="ref-21"><strong>[P3]</strong> Wijk et al. <a href="https://proceedings.mlr.press/v267/wijk25a.html">RE-Bench: Evaluating Frontier AI R&amp;D Capabilities of Language Model Agents against Human Experts</a>. ICML Spotlight, 2025.</li>
  <li id="ref-22"><strong>[P3]</strong> Gao, Schulman &amp; Hilton. <a href="https://proceedings.mlr.press/v202/gao23h.html">Scaling Laws for Reward Model Overoptimization</a>. ICML, 2023.</li>
  <li id="ref-23"><strong>[P3]</strong> Skalse et al. <a href="https://openreview.net/forum?id=yb3HOXO3lX2">Defining and Characterizing Reward Gaming</a>. NeurIPS, 2022.</li>
  <li id="ref-24"><strong>[P3]</strong> Ruan et al. <a href="https://openreview.net/forum?id=GEcwtMk1uA">Identifying the Risks of LM Agents with an LM-Emulated Sandbox</a>. ICLR Spotlight, 2024.</li>
  <li id="ref-25"><strong>[P3]</strong> van der Weij et al. <a href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/b5e5753b0a0e440a6d8dc7e143617cec-Abstract-Conference.html">AI Sandbagging: Language Models Can Strategically Underperform on Evaluations</a>. ICLR, 2025.</li>
  <li id="ref-26"><strong>[P1]</strong> Lee et al. <a href="https://arxiv.org/abs/2603.28052">Meta-Harness: End-to-End Optimization of Model Harnesses</a>. arXiv preprint, 2026.</li>
  <li id="ref-27"><strong>[P1]</strong> Zhang et al. <a href="https://arxiv.org/abs/2606.09498">Self-Harness: Harnesses That Improve Themselves</a>. arXiv preprint, 2026.</li>
  <li id="ref-28"><strong>[P1]</strong> Novikov et al. <a href="https://arxiv.org/abs/2506.13131">AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery</a>. Google DeepMind technical report, 2025.</li>
  <li id="ref-29"><strong>[P1]</strong> Ye et al. <a href="https://arxiv.org/abs/2601.21557">Meta Context Engineering via Agentic Skill Evolution</a>. arXiv preprint, 2026.</li>
  <li id="ref-30"><strong>[P1]</strong> Hebbar et al. <a href="https://arxiv.org/abs/2605.27276">SIA: Self Improving AI with Harness &amp; Weight Updates</a>. arXiv preprint, 2026.</li>
  <li id="ref-31"><strong>[经典文献]</strong> Good, I. J. <a href="https://doi.org/10.1016/S0065-2458(08)60418-0">Speculations Concerning the First Ultraintelligent Machine</a>. Advances in Computers, 1965.</li>
</ol>

<div class="he-source">
<strong>原始来源：</strong>Lilian Weng, “Harness Engineering for Self-Improvement,” Lil’Log, 4 July 2026. <a href="https://lilianweng.github.io/posts/2026-07-04-harness/">原文链接</a>。<br>
<strong>范围说明：</strong>本文对 2026 年近期工作的发表状态核验截止于 2026/07/10；预印本的结论可能在后续同行评审中变化。
</div>
