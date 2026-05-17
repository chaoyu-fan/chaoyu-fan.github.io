---
layout: page
permalink: /blogs/evolutionary-tool-use-optimization/index.html
title: 用进化算法优化 LLM Agent 的工具调用：从 prompt evolution 到因果轨迹优化
description: 一篇学术风格技术博客，梳理遗传算法、Pareto 选择、skill evolution 与 tool-use policy optimization 的相关研究，指出现有缺陷，并提出 Causal-Pareto Tool Evolution 作为面向长链路 agent 的新方案。
---

<style>
.evo-lead{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1rem .95rem;border-radius:10px;margin:1rem 0 1.2rem}
.evo-lead p{margin:.35rem 0;color:#405160;line-height:1.78}
.evo-callout{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem;margin:1rem 0 1.2rem}
.evo-callout p{margin:0;color:#405160;line-height:1.75}
.evo-wrap{overflow-x:auto;margin:1rem 0 1.2rem}
.evo-table{width:100%;border-collapse:collapse;min-width:900px;font-size:.94rem}
.evo-table th,.evo-table td{border-bottom:1px solid #dde4ea;padding:.72rem .55rem;text-align:left;vertical-align:top}
.evo-table th{color:#34495a}
.evo-table td{color:#4b5c69;line-height:1.7}
.evo-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.2rem}
.evo-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem}
.evo-card h3{margin:.05rem 0 .45rem;color:#2f4756;font-size:1.02rem}
.evo-card p{margin:0;color:#536572;line-height:1.75}
.evo-badges{display:flex;flex-wrap:wrap;gap:.45rem;margin:.85rem 0 0}
.evo-badge{display:inline-block;border:1px solid #dce5ec;border-radius:999px;padding:.18rem .55rem;font-size:.82rem;color:#445a68;background:#fbfcfe}
.evo-code{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:.95rem 1rem;margin:1rem 0 1.25rem}
.evo-code pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:.9rem;line-height:1.65}
.evo-source{margin-top:1.35rem;padding-top:1rem;border-top:1px solid #dde4ea;color:#56636f;font-size:.92rem;line-height:1.8}
@media (max-width: 840px){.evo-grid{grid-template-columns:1fr}}
</style>

## 用进化算法优化 LLM Agent 的工具调用

> 更新时间：2026/05/17  
> 文章定位：学术风格技术博客 + 研究方案草案。  
> 关键词：tool use optimization, evolutionary algorithm, genetic algorithm, Pareto selection, coding agent, causal attribution

<div class="evo-lead">
  <p><strong>核心判断：</strong>遗传算法并不是只能优化连续参数，也可以优化 LLM agent 的离散控制策略。对于 tool use，真正适合进化的对象不是模型权重，而是 planner、tool router、tool description、retry policy、verifier 和 skill bundle 这些外层可控部件。</p>
  <p>现有研究已经从 prompt evolution 走向 tool-use policy evolution 和 skill evolution，但仍缺少对长链路工具轨迹的因果归因、状态安全和跨 harness 泛化验证。</p>
</div>

### 一、为什么 tool use optimization 适合进化算法

Tool use 的优化空间天然是离散、组合和非可微的。一个 agent 是否成功，取决于工具选择、参数生成、执行顺序、错误恢复、状态保存和最终综合。这里很难直接对 closed-source LLM 做梯度更新，也很难用单一奖励稳定训练。相比之下，遗传算法和更宽泛的 evolutionary optimization 有三个优势。

第一，它不要求访问模型权重。对于 Claude Code、Codex-like agent、DeepSeek/Qwen/GLM 接入 harness 这类系统，工程团队通常只能改 prompt、tool schema、adapter、memory、verifier 和 workflow。进化算法正好可以把这些外层构件当作 genome。

第二，它适合多目标优化。Tool use 不能只看 pass rate，还要看成本、延迟、工具调用次数、无效调用率、状态正确性和安全副作用。Pareto selection 比单一分数更适合保留不同权衡下的候选策略。

第三，它可以利用失败轨迹。长链路 agent 的失败通常带有可诊断结构：选错工具、参数错、漏验证、状态漂移、重复调用或错误成功。进化算法可以把这些失败转化为 targeted mutation，而不是盲目改写整个系统提示词。

因此，本文讨论的“遗传算法做 tool use optimization”，不是传统意义上对神经网络参数做遗传搜索，而是对 **agent 外层控制策略** 做进化。

### 二、相关研究：从 prompt 到 tool policy，再到 skill bundle

<div class="evo-badges">
  <span class="evo-badge">论文支持</span>
  <span class="evo-badge">研究综述</span>
</div>

目前可以把相关研究分成五条线。

<div class="evo-wrap">
<table class="evo-table">
  <thead>
    <tr>
      <th>方向</th>
      <th>代表工作</th>
      <th>优化对象</th>
      <th>与 tool use 的关系</th>
      <th>主要局限</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Tool-use policy evolution</td>
      <td><a href="https://arxiv.org/abs/2603.04900">EvoTool</a></td>
      <td>Planner、Selector、Caller、Synthesizer</td>
      <td>最直接面向工具调用策略，使用 blame-aware mutation 和 diversity-aware selection</td>
      <td>模块归因仍偏诊断式，真实 workspace、副作用和长期状态覆盖不足</td>
    </tr>
    <tr>
      <td>Prompt evolution</td>
      <td><a href="https://arxiv.org/abs/2507.19457">GEPA</a>, <a href="https://arxiv.org/abs/2410.14826">SPRIG</a></td>
      <td>system prompt、module prompt、文本规则</td>
      <td>可用于 planner prompt、router prompt、verifier prompt 的优化</td>
      <td>不是 tool-use native，容易只优化语言层而忽略状态和副作用</td>
    </tr>
    <tr>
      <td>Context optimization</td>
      <td><a href="https://aclanthology.org/2025.findings-acl.1149/">ACL 2025 Joint Optimization</a></td>
      <td>agent instruction 与 tool description</td>
      <td>说明工具描述和 agent 指令的不完整会造成计算开销，并可通过联合优化提升效率</td>
      <td>主要解决上下文表达效率，不等于完整工具轨迹优化</td>
    </tr>
    <tr>
      <td>Skill evolution</td>
      <td><a href="https://arxiv.org/abs/2603.02766">EvoSkill</a>, <a href="https://arxiv.org/abs/2604.01687">CoEvoSkills</a></td>
      <td>可复用 skill folder、workflow、multi-file artifacts</td>
      <td>适合 coding agent，把失败经验沉淀成可复用技能</td>
      <td>skill 会膨胀、冲突，并重新引入 skill selection 问题</td>
    </tr>
    <tr>
      <td>Multi-objective skill search</td>
      <td><a href="https://arxiv.org/abs/2604.09297">SkillMOO</a></td>
      <td>skill bundle</td>
      <td>用 NSGA-II survivor selection 同时优化成功率、成本和运行时间</td>
      <td>面向软件工程 skill bundle，尚未充分覆盖通用 tool policy 与安全副作用</td>
    </tr>
  </tbody>
</table>
</div>

这些工作共同说明一个趋势：agent 优化正在从“改一段 prompt”转向“进化一个可执行系统”。EvoTool 是最接近 tool-use policy optimization 的工作。它把工具策略拆成 Planner、Selector、Caller 和 Synthesizer，并用轨迹诊断做 blame attribution，只 mutation 被归因的模块。GEPA 则更一般，它将 compound AI system 中的 prompt 视作可进化文本，利用轨迹、工具调用和工具输出做自然语言反思，再通过 Pareto frontier 合并互补经验。ACL 2025 的 joint optimization 进一步说明，工具描述本身也是优化对象，不完整 context 会导致冗余工具调用和额外计算开销。EvoSkill、CoEvoSkills 和 SkillMOO 则把优化对象从单条 prompt 扩展到 skill 级别。

### 三、现有研究要解决的科学问题

<div class="evo-badges">
  <span class="evo-badge">问题定义</span>
  <span class="evo-badge">研究空白</span>
</div>

#### 1. 长链路 credit assignment

Tool use 的失败通常具有延迟反馈。一个 coding agent 最终没有通过测试，可能不是最后的 answer synthesis 出错，而是 40 步之前选错了检索路径、覆盖了文件、漏跑了测试，或者误解了工具返回值。EvoTool 已经将 delayed supervision 和 long-horizon credit assignment 作为核心挑战，但现有 blame attribution 多数仍是基于诊断轨迹的解释式归因。

更严格的科学问题是：

<div class="evo-callout">
  <p><strong>如何从长工具轨迹中识别真正导致失败的最小因果子轨迹，而不是只生成一个合理的失败解释？</strong></p>
</div>

这要求评测系统不只保存最终答案，还要保存工具调用、状态变化、失败节点和可重放环境。

#### 2. Agent genome 的表示问题

传统遗传算法有明确 genome，例如 bit string、树结构或参数向量。LLM agent 的 genome 更复杂。它可能包括 planner prompt、tool router prompt、tool descriptions、few-shot examples、权限矩阵、重试策略、并行策略、verifier 规则、memory compression 和 skill bundles。

现有工作通常只优化其中一个层次。GEPA 优化 prompt，ACL joint optimization 优化 instruction 和 tool description，EvoSkill 优化 skill，EvoTool 优化四个 tool-use policy 模块。真正的问题是：

<div class="evo-callout">
  <p><strong>什么样的 agent genome 既足够表达 tool-use 行为，又能被 mutation、selection 和 safety constraint 稳定操作？</strong></p>
</div>

如果 genome 太细，搜索空间爆炸；如果 genome 太粗，mutation 会破坏已有能力。

#### 3. 多目标 fitness 的可验证性

Tool use optimization 不能只最大化任务成功率。对于生产 agent，更重要的是 safe success rate。一个 agent 如果通过减少验证步骤来提高速度，或通过扩大权限来提高完成率，短期 benchmark 可能变好，但系统风险上升。

需要同时优化的目标包括：

- 成功率
- 工具调用次数
- 无效调用率
- 成本和延迟
- 状态变化正确性
- 错误恢复率
- 安全副作用
- 跨任务泛化

SkillMOO 用多目标优化处理成功率、成本和 runtime，是一个重要方向。但 tool use 还需要把安全和状态正确性从 soft metric 提升为 hard constraint。

#### 4. 泛化与 benchmark overfitting

进化算法很容易对固定任务集过拟合。一个 prompt 在 StableToolBench 上减少调用次数，不代表它在真实 coding agent 中也更可靠。一个 skill 在 SealQA 上有效，也不一定能迁移到 SWE-bench 或 Terminal-Bench。EvoSkill 报告了零样本迁移增益，这很有价值，但它也说明 transferability 必须被单独评估，而不是从训练集性能中推断。

真正需要回答的问题是：

<div class="evo-callout">
  <p><strong>进化出来的 tool-use policy 是否能跨任务、跨工具集、跨模型和跨 harness 保持收益？</strong></p>
</div>

#### 5. 自我改进的安全边界

如果 agent 可以进化自己的工具策略，它可能会学会绕过原本用于保护系统的步骤。例如减少确认、跳过 verifier、扩大工具权限，或把风险写操作伪装成普通调用。现有 self-evolving agent 工作多数强调性能改进，但对“哪些策略可以被 mutation，哪些策略必须冻结”讨论不足。

这不是工程细节，而是科学问题：tool-use optimizer 本身也需要被约束。

### 四、现有方案的缺陷

EvoTool 的贡献在于把 tool-use policy 拆成模块，并引入 blame-aware mutation。但它仍面临三个限制。第一，Planner、Selector、Caller、Synthesizer 的四分法对 API agent 足够清晰，对 coding agent 的真实边界还不够细。文件系统、shell、浏览器、git、CI、部署和权限系统会引入更多状态与副作用。第二，trajectory-grounded blame attribution 可能把相关性当因果性。第三，目前评测仍主要依赖 benchmark，缺少千次级调用、workspace dirty state、权限拒绝、回滚和并发写冲突的系统测试。

GEPA 和 SPRIG 的缺陷则在于优化对象偏文本。它们可以有效改进 prompt，但 prompt 改进不等于工具轨迹安全。一个更会写计划的 agent，仍可能在工具选择、状态保存和副作用控制上失败。

ACL joint optimization 的价值在于指出 context 不完整会带来工具使用低效，并联合优化 agent instruction 与 tool description。但减少工具调用次数不一定总是正确目标。在 coding agent 和企业工作流中，某些验证调用、dry-run 调用和权限检查是必要冗余。盲目压缩工具调用数可能牺牲 safe success rate。

Skill evolution 方向更接近真实 coding agent，但也有自己的问题。Skill 会增长、重叠和冲突。一个 skill bundle 变强后，系统仍需要回答“什么时候触发这个 skill”。如果没有强 verifier，坏 skill 也可能因为偶然 benchmark gain 被保留下来。

### 五、一个可能的新方案：Causal-Pareto Tool Evolution

<div class="evo-badges">
  <span class="evo-badge">新方案</span>
  <span class="evo-badge">研究假设</span>
</div>

我建议把新方案定义为 **Causal-Pareto Tool Evolution, CPTE**。它的目标不是进化模型，也不是单独进化 prompt，而是进化一套带安全约束的工具调用控制策略。

#### 1. Genome

一个候选 agent policy 可以表示为：

<div class="evo-code">
<pre>G = {
  planner_policy,
  tool_router_policy,
  tool_description_patch,
  few_shot_tool_examples,
  permission_matrix,
  retry_and_recovery_policy,
  parallelization_policy,
  verifier_policy,
  memory_checkpoint_policy,
  skill_bundle
}</pre>
</div>

其中 `permission_matrix`、高风险写操作 gate 和安全 invariant 不允许自由 mutation。它们只能在 sandbox 中测试，或只能被收紧，不能被优化器直接放宽。

#### 2. Trace

每次任务执行必须保存完整事件流：

<div class="evo-code">
<pre>user_goal
plan
tool_call_requested
tool_call_validated
tool_call_executed
tool_result
state_delta
verifier_result
final_answer
human_or_test_verdict</pre>
</div>

优化对象不是最后一句回答，而是整条工具轨迹。这一点对长链路 agent 尤其关键。

#### 3. Causal attribution

CPTE 不只依赖 LLM 自我反思，而是引入 counterfactual replay。基本思想是固定轨迹的一部分，只替换一个模块，看失败是否被消除：

- 固定 planner，替换 selector，检验工具选择是否为主要失败源。
- 固定 selector，替换 caller，检验参数生成是否为主要失败源。
- 固定工具轨迹，只替换 synthesizer，检验结果综合是否出错。
- 固定执行策略，只替换 verifier，检验错误是否本可被提前拦截。

这样，blame attribution 从“自然语言解释”变成“反事实证据支持的归因”。它不能完全解决因果识别，但能显著降低把失败错归到无关模块的概率。

#### 4. Mutation

不同失败类型触发不同 mutation：

<div class="evo-wrap">
<table class="evo-table">
  <thead>
    <tr>
      <th>失败类型</th>
      <th>mutation 对象</th>
      <th>验证方式</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>工具选错</td>
      <td>tool router policy, tool description patch</td>
      <td>候选工具 recall 与 precision</td>
    </tr>
    <tr>
      <td>参数错误</td>
      <td>caller prompt, schema examples</td>
      <td>schema validity + semantic validator</td>
    </tr>
    <tr>
      <td>重复调用</td>
      <td>retry policy, memory checkpoint policy</td>
      <td>redundant call ratio</td>
    </tr>
    <tr>
      <td>漏验证</td>
      <td>verifier policy</td>
      <td>state invariant coverage</td>
    </tr>
    <tr>
      <td>并行冲突</td>
      <td>parallelization policy</td>
      <td>write-lock violation rate</td>
    </tr>
    <tr>
      <td>状态漂移</td>
      <td>memory checkpoint policy, result-id protocol</td>
      <td>checkpoint survival</td>
    </tr>
    <tr>
      <td>错误成功</td>
      <td>safety invariant, verifier rules</td>
      <td>safe success rate</td>
    </tr>
  </tbody>
</table>
</div>

#### 5. Selection

CPTE 使用 Pareto selection，而不是单一分数：

<div class="evo-code">
<pre>maximize:
  safe_success_rate
  state_delta_correctness
  recovery_rate
  cross_task_transfer

minimize:
  invalid_tool_call_rate
  redundant_call_ratio
  latency
  token_cost
  risky_write_count</pre>
</div>

任何违反 hard safety constraints 的候选直接淘汰，即使 pass rate 更高。

#### 6. Deployment

部署上应采用 champion/challenger，而不是直接替换：

1. Champion 是当前稳定策略。
2. Challenger 是进化产生的新策略。
3. Challenger 先跑 offline replay。
4. 再进入 shadow mode，只观察，不执行高风险写操作。
5. 通过后进入 canary。
6. 出现 safety regression 自动回滚。

### 六、可检验的研究假设

如果把 CPTE 写成论文，我建议围绕一个核心假设展开：

<div class="evo-callout">
  <p><strong>在长链路工具调用任务中，反事实轨迹归因比自然语言自反思更能指导 tool-use policy evolution，并能在相同预算下提高 safe success rate。</strong></p>
</div>

实验设计可以包括四组：

- 原始 agent。
- GEPA-style prompt evolution。
- EvoTool-style blame-aware mutation。
- CPTE：counterfactual blame + Pareto tool-policy evolution + safety constraints。

评测不应只使用单一 benchmark。可以分层使用 BFCL、ToolSandbox、tau-bench、Terminal-Bench / SWE-bench 子集，以及自建 high-dimensional tool trace benchmark。核心指标包括 safe success rate、invalid tool call rate、redundant call ratio、recovery rate、state correctness、cost、latency 和 cross-model transfer。

### 七、创新点总结

<div class="evo-grid">
  <div class="evo-card">
    <h3>1. 从 prompt evolution 到 trajectory evolution</h3>
    <p>优化对象从单段文本扩展为完整工具轨迹和控制策略，包括路由、调用、验证、状态和恢复。</p>
  </div>
  <div class="evo-card">
    <h3>2. 反事实归因</h3>
    <p>用可重放轨迹检验失败归因，减少仅靠自然语言解释带来的误归因。</p>
  </div>
  <div class="evo-card">
    <h3>3. 安全硬约束</h3>
    <p>把权限越界、不可逆写操作和副作用违规设为淘汰条件，而不是普通 fitness 项。</p>
  </div>
  <div class="evo-card">
    <h3>4. 面向真实 coding agent</h3>
    <p>显式处理 workspace diff、checkpoint、artifact、shell output、test result 和 verifier state。</p>
  </div>
  <div class="evo-card">
    <h3>5. 多目标 Pareto 选择</h3>
    <p>同时优化成功率、成本、延迟、冗余调用、恢复能力和安全性，避免单一 pass rate 过拟合。</p>
  </div>
  <div class="evo-card">
    <h3>6. 跨模型和 harness</h3>
    <p>优化外层 agent policy，而不是模型权重，因此可迁移到 Claude Code、Codex-like agent 和 OpenAI-compatible provider。</p>
  </div>
</div>

### 结论

遗传算法用于 tool use optimization 并不是一个边缘想法。它正在以几种形式进入 agent 研究：GEPA 优化 prompt，ACL joint optimization 优化 instruction 与 tool description，EvoTool 优化模块化工具策略，EvoSkill 和 CoEvoSkills 优化可复用 skill，SkillMOO 用多目标进化优化软件工程 skill bundle。

但现有方案仍主要停留在文本、模块或 skill 层面。长链路工具调用真正需要的是轨迹级优化：保存完整工具事件，识别因果失败源，局部 mutation，使用 Pareto selection，并把安全约束置于成功率之上。

因此，下一步值得做的不是再发明一个更长的 prompt optimizer，而是构建一个可以重放、归因、进化和验证的 tool-use policy laboratory。只有在这种实验系统中，tool use optimization 才能从经验调参走向可检验的科学问题。

<div class="evo-source">
<strong>主要资料来源</strong>：
<a href="https://arxiv.org/abs/2603.04900">EvoTool</a>，
<a href="https://arxiv.org/abs/2507.19457">GEPA</a>，
<a href="https://aclanthology.org/2025.findings-acl.1149/">A Joint Optimization Framework for Enhancing Efficiency of Tool Utilization in LLM Agents</a>，
<a href="https://arxiv.org/abs/2410.14826">SPRIG</a>，
<a href="https://arxiv.org/abs/2603.02766">EvoSkill</a>，
<a href="https://arxiv.org/abs/2604.01687">CoEvoSkills</a>，
<a href="https://arxiv.org/abs/2604.09297">SkillMOO</a>。
</div>
