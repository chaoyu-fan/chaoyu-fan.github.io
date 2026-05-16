---
layout: page
permalink: /blogs/tool-use-landscape-2026/index.html
title: 大模型 tool use 的真正分歧：谁拥有执行循环
description: 一篇面向 agent 工程的 tool use 技术综述：比较 OpenAI、Anthropic、Gemini、DeepSeek、Mistral、xAI、Qwen、Cohere 的工具调用模式，并梳理训练方法、优化研究和评测基准。
---

<style>
.tu-lead{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1rem .95rem;border-radius:10px;margin:1rem 0 1.2rem}
.tu-lead p{margin:.35rem 0;color:#405160;line-height:1.78}
.tu-callout{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem 1rem .95rem;margin:1rem 0 1.2rem}
.tu-callout p{margin:0;color:#405160;line-height:1.75}
.tu-wrap{overflow-x:auto;margin:1rem 0 1.2rem}
.tu-table{width:100%;border-collapse:collapse;min-width:900px;font-size:.94rem}
.tu-table th,.tu-table td{border-bottom:1px solid #dde4ea;padding:.72rem .55rem;text-align:left;vertical-align:top}
.tu-table th{color:#34495a}
.tu-table td{color:#4b5c69;line-height:1.7}
.tu-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.2rem}
.tu-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem}
.tu-card h3{margin:.05rem 0 .45rem;color:#2f4756;font-size:1.02rem}
.tu-card p{margin:0;color:#536572;line-height:1.75}
.tu-list li{margin:.35rem 0;line-height:1.75;color:#42586a}
.tu-badges{display:flex;flex-wrap:wrap;gap:.45rem;margin:.85rem 0 0}
.tu-badge{display:inline-block;border:1px solid #dce5ec;border-radius:999px;padding:.18rem .55rem;font-size:.82rem;color:#445a68;background:#fbfcfe}
.tu-source{margin-top:1.35rem;padding-top:1rem;border-top:1px solid #dde4ea;color:#56636f;font-size:.92rem;line-height:1.8}
@media (max-width: 840px){.tu-grid{grid-template-columns:1fr}}
</style>

## 大模型 tool use 的真正分歧：谁拥有执行循环

> 更新时间：2026/05/16
> 文章定位：技术综述 + agent 工程判断。

讨论 tool use 时，最容易把问题说浅：模型返回一个 JSON，应用执行一个函数，再把结果塞回去。
这句话没有错，但它只描述了最外层的语法。真正决定 agent 是否可靠的，不是“有没有 function calling”，而是五个控制权分别属于谁：

- 谁决定要不要调用工具
- 谁保证参数符合 schema
- 谁执行工具并处理失败
- 谁保存中间推理和工具结果
- 谁评估一次工具轨迹是否成功

我的结论是：**主流厂商的 tool use 差异，本质上不是 API 字段名不同，而是对 agent 执行循环所有权的分配不同。**
OpenAI 正在把 tool use 收敛成平台级 agent surface；Anthropic 把工具调用暴露成清晰的事件流；Gemini 把并行和串联工具调用做成 SDK 友好的编排能力；DeepSeek、Mistral、xAI 和 Qwen 更接近 OpenAI-compatible 或 chat-function calling 路线；Cohere 则更偏企业检索、引用和证据链。

<div class="tu-lead">
  <p><strong>如果只记一个判断：</strong>tool use 的工程难点不在“调用一个函数”，而在“跨多轮、多工具、多失败路径时，系统是否还能保持状态一致”。</p>
  <p>因此，评估一个模型或 API 的 tool use 能力时，不能只看单轮 function call 命中率，还要看 schema 约束、并行调用、工具结果回填、失败重试、推理态保留和 benchmark 的任务形态。</p>
</div>

### 证据等级说明

这篇文章混合了三类信息。为避免把工程判断写成官方结论，我先把证据等级标出来：

<div class="tu-wrap">
<table class="tu-table">
  <thead>
    <tr>
      <th>标签</th>
      <th>含义</th>
      <th>本文中的例子</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="tu-badge">官方事实</span></td>
      <td>来自厂商官方文档或 API 行为描述</td>
      <td>Anthropic 的 <code>tool_use</code>/<code>tool_result</code>，Gemini 的 parallel/compositional function calling，DeepSeek thinking mode 支持工具调用</td>
    </tr>
    <tr>
      <td><span class="tu-badge">论文支持</span></td>
      <td>来自公开论文或 benchmark 论文的研究结论</td>
      <td>Toolformer 的自监督工具调用、ToolLLM 的大规模 API 数据、StableToolBench 对评测稳定性的处理</td>
    </tr>
    <tr>
      <td><span class="tu-badge">工程推断</span></td>
      <td>基于官方协议、论文和 agent 工程经验做出的归纳，不是厂商原话</td>
      <td>“执行循环所有权”“平台化路线 vs 协议化路线”“tool-use reliability 公式”</td>
    </tr>
  </tbody>
</table>
</div>

下面所有“各家具体模式”以官方事实为主；“路线划分”“可靠性公式”“类 Codex agent 设计建议”属于本文工程推断，需要用你自己的 harness 和 benchmark 验证。

### 一、各家具体模式：差异在协议，不只在模型

<div class="tu-badges">
  <span class="tu-badge">官方事实为主</span>
  <span class="tu-badge">少量工程推断</span>
</div>

<div class="tu-wrap">
<table class="tu-table">
  <thead>
    <tr>
      <th>厂商</th>
      <th>工具调用模式</th>
      <th>执行循环归属</th>
      <th>最值得注意的工程点</th>
      <th>适合什么场景</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>OpenAI</strong></td>
      <td>Responses API 下的 function calling、built-in tools、remote MCP、structured outputs</td>
      <td>平台和应用共同拥有。模型提出工具调用，平台提供部分 hosted tools，应用也可执行自定义函数</td>
      <td>工具能力正在和 Responses API、Agents SDK、MCP、Computer Use 等统一到同一个 agent surface</td>
      <td>适合做统一 agent 平台，尤其是你希望 web search、file search、computer use、自定义函数在同一层被编排</td>
    </tr>
    <tr>
      <td><strong>Anthropic</strong></td>
      <td>Messages API 中的 <code>tool_use</code> / <code>tool_result</code> block，支持 <code>tool_choice</code> 和 parallel tool use</td>
      <td>应用拥有显式循环。模型输出 tool event，应用执行工具，再把结果作为下一轮消息返回</td>
      <td>事件边界清楚，client-side tools 和 server-side tools 分明，适合把工具调用作为可审计轨迹处理</td>
      <td>适合需要强控制、多轮回填、可观察性和人为审计的 agent 系统</td>
    </tr>
    <tr>
      <td><strong>Gemini</strong></td>
      <td><code>function_declarations</code>、<code>functionCall</code>，支持 <code>AUTO</code> / <code>ANY</code> / <code>NONE</code>、parallel 和 compositional function calling</td>
      <td>SDK 可部分接管。Python SDK 可自动执行函数调用循环，开发者也可手动处理</td>
      <td>thinking model 场景下需要处理 thought signatures，否则多轮工具调用可能丢失推理连续性</td>
      <td>适合多工具并行、串联调用和 SDK 优先的应用开发</td>
    </tr>
    <tr>
      <td><strong>DeepSeek</strong></td>
      <td>Chat Completions 风格 <code>tools</code>，支持 <code>tool_choice</code>、thinking mode tool calls、beta strict schema</td>
      <td>主要由应用拥有循环。协议接近 OpenAI Chat Completions，但 thinking 内容和工具消息回放要小心处理</td>
      <td>strict mode 可以提高 JSON schema 遵循度，但 beta endpoint 和 thinking 回传规则会影响 adapter 设计</td>
      <td>适合已有 OpenAI-compatible adapter、又希望引入 DeepSeek 模型和严格 schema 的系统</td>
    </tr>
    <tr>
      <td><strong>Mistral</strong></td>
      <td>function calling、tool call response、tool result replay、agent function calling</td>
      <td>应用拥有循环。整体是经典 chat-function calling 模式</td>
      <td>接口直接，支持 <code>tool_choice</code> 与 <code>parallel_tool_calls</code>，迁移成本相对低</td>
      <td>适合简单清晰的工具链，或已有 chat completions 架构的项目</td>
    </tr>
    <tr>
      <td><strong>xAI</strong></td>
      <td>OpenAI-compatible chat + function calling，parallel function calling 默认开启</td>
      <td>应用拥有循环。工具调用形态接近 OpenAI-compatible 生态</td>
      <td>默认并行调用可能提高吞吐，也可能放大工具幂等性、限流和结果合并问题</td>
      <td>适合已有 OpenAI-compatible provider abstraction 的系统快速试接</td>
    </tr>
    <tr>
      <td><strong>Qwen</strong></td>
      <td>Qwen-Agent、函数调用模板、OpenAI-compatible serving，常见于 vLLM、Ollama 等部署栈</td>
      <td>部署层和应用共同拥有。开源模型场景下，模板、parser、serving runtime 都会影响结果</td>
      <td>自托管时不能只看模型权重，要验证 chat template、tool parser、thinking 输出和工具 JSON 的边界</td>
      <td>适合私有化部署、国产/开源模型接入、需要控制推理成本和部署环境的团队</td>
    </tr>
    <tr>
      <td><strong>Cohere</strong></td>
      <td>single-step tool use、multi-step tool use、citations</td>
      <td>应用拥有工具执行，平台强调多步推理与引用输出</td>
      <td>产品重心更偏企业检索、证据追踪和可引用回答，不只是通用函数调用</td>
      <td>适合 RAG、知识库问答、需要 citation 和证据链的企业应用</td>
    </tr>
  </tbody>
</table>
</div>

这张表背后的 insight 是：**tool use 正在分成两条路线。** 这是本文的工程推断，不是任何一家厂商的官方分类。

第一条是平台化路线。OpenAI、Gemini 在往“工具、状态、推理、执行环境都能由平台承接一部分”的方向走。优点是开发者少写 glue code，缺点是 provider surface 更厚，迁移成本更高。

第二条是协议化路线。Anthropic、DeepSeek、Mistral、xAI、Qwen 更强调消息协议中的工具事件，应用自己掌握执行循环。优点是可控、可观测、可替换，缺点是你必须自己处理并行、重试、幂等、状态和错误恢复。

### 二、为什么“会调用工具”还远远不够

<div class="tu-badges">
  <span class="tu-badge">工程推断</span>
</div>

一个可靠 tool-use agent 至少要过四关。

<div class="tu-grid">
  <div class="tu-card">
    <h3>1. 选择正确工具</h3>
    <p>模型必须先判断任务是否需要外部状态。这里失败时，模型通常会凭记忆回答、漏查数据库、跳过计算器，或在需要用户确认时直接行动。</p>
  </div>
  <div class="tu-card">
    <h3>2. 生成正确参数</h3>
    <p>字段名、类型、枚举、日期、单位和嵌套对象都会出错。strict schema、structured outputs 和 tool parser 解决的是这一层。</p>
  </div>
  <div class="tu-card">
    <h3>3. 管理工具轨迹</h3>
    <p>真实任务常常不是一次调用，而是检索、计算、写入、验证和重试的链条。这里考验的是状态机，不只是语言模型。</p>
  </div>
  <div class="tu-card">
    <h3>4. 从结果中继续推理</h3>
    <p>工具结果不是最终答案。模型还要判断结果是否可信、是否需要二次查询、是否违反约束，以及如何把结果解释给用户。</p>
  </div>
</div>

因此，tool use 能力可以拆成一个更实际的公式：

<div class="tu-callout">
  <p><strong>tool-use reliability = tool selection accuracy x argument validity x execution success x state continuity x recovery quality</strong></p>
</div>

单看 function call JSON 是否正确，只覆盖了第二项。真实 agent 经常坏在第三、第四、第五项。

### 三、tool use 是怎么训练出来的

<div class="tu-badges">
  <span class="tu-badge">论文支持</span>
  <span class="tu-badge">部分推断</span>
</div>

公开论文和产品行为显示，tool use 训练不是单一技术，而是逐步叠加出来的能力。

**第一层是格式学习。**
模型先要学会把自然语言意图映射成结构化调用。典型训练数据是“用户请求 -> 工具定义 -> 工具调用 JSON -> 工具结果 -> 最终回答”。这类数据可以来自人工标注，也可以来自合成轨迹。它解决的是“会不会按协议说话”。

**第二层是轨迹学习。**
Toolformer 的关键贡献不是某一个 API，而是让模型学习在文本生成过程中插入工具调用。Gorilla、ToolLLM 和 API-Bank 则把问题扩展到大量真实 API、API 文档检索和多工具任务。这里的目标已经不是“格式正确”，而是“在任务路径上调用正确工具”。

**第三层是合成与自改进。**
APIGen、ToolACE 这类工作说明，工具调用数据正在被系统化合成：先生成任务、工具、参数和调用轨迹，再过滤掉不可执行或低质量样本。合成数据的价值在于覆盖长尾 API 和组合调用，但风险是 synthetic trajectory 可能学到不真实的工具分布。

**第四层是奖励优化。**
Search-R1 这类工作把搜索/工具交互放进强化学习框架里，让模型不只学会“调用”，还学习何时继续搜索、何时停止、如何利用外部结果。这个方向更接近 agent optimization，因为优化对象是整条 trajectory，而不是单个 JSON。

这也解释了为什么很多模型在简单 demo 里表现不错，进到真实 agent 后会不稳定：demo 主要测格式学习，真实系统测的是轨迹学习和恢复能力。

### 四、tool use optimization 研究在优化什么

<div class="tu-badges">
  <span class="tu-badge">论文支持</span>
  <span class="tu-badge">工程映射为推断</span>
</div>

tool use optimization 不是单一问题。它至少分成六类。

<div class="tu-wrap">
<table class="tu-table">
  <thead>
    <tr>
      <th>优化对象</th>
      <th>代表研究</th>
      <th>真正想解决的问题</th>
      <th>工程映射</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>工具调用数据</td>
      <td>Toolformer, Gorilla, ToolLLM, APIGen, ToolACE</td>
      <td>缺少高质量、可执行、覆盖长尾工具的训练轨迹</td>
      <td>为模型或小模型 adapter 构建 tool-call SFT 数据</td>
    </tr>
    <tr>
      <td>API 检索与选择</td>
      <td>Gorilla, ToolLLM, ToolBench</td>
      <td>工具数量一多，模型不知道该看哪个文档、选哪个 API</td>
      <td>在 agent 前面加 tool retrieval 和 tool ranking</td>
    </tr>
    <tr>
      <td>评测稳定性</td>
      <td>StableToolBench</td>
      <td>真实 API 会变、会限流、会失败，导致 benchmark 不可复现</td>
      <td>用模拟 API、缓存、状态隔离和 deterministic evaluator 降低噪声</td>
    </tr>
    <tr>
      <td>轨迹决策</td>
      <td>Search-R1</td>
      <td>模型需要学会何时搜索、何时停止、如何把工具结果纳入推理</td>
      <td>用 outcome reward 或 process reward 优化多轮工具策略</td>
    </tr>
    <tr>
      <td>并行与延迟</td>
      <td>LLMCompiler, Asynchronous LLM Function Calling</td>
      <td>多工具任务如果串行执行，延迟会急剧上升</td>
      <td>把独立调用并行化，或让工具执行和模型推理异步交叠</td>
    </tr>
    <tr>
      <td>成本与缓存</td>
      <td>Less is More, ToolCaching</td>
      <td>重复工具调用浪费 token、延迟和外部 API 预算</td>
      <td>缓存工具结果，减少不必要调用，设计幂等和失效策略</td>
    </tr>
  </tbody>
</table>
</div>

这里最重要的变化是：**研究重点正在从“函数调用准确率”转向“工具轨迹的系统效率”。**
在真实应用里，一个 agent 少调一次无用搜索、多并行两个独立 API、失败后能正确回滚，可能比单轮 JSON 准确率多 1 个百分点更有价值。

### 五、benchmark 应该怎么读

<div class="tu-badges">
  <span class="tu-badge">论文支持</span>
  <span class="tu-badge">使用建议为推断</span>
</div>

不同 benchmark 的问题意识不同，不能混着看。

<div class="tu-wrap">
<table class="tu-table">
  <thead>
    <tr>
      <th>基准</th>
      <th>主要测什么</th>
      <th>容易漏掉什么</th>
      <th>适合怎么用</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>BFCL</strong></td>
      <td>函数选择、参数生成、格式遵循、多函数调用</td>
      <td>真实工具执行、状态回滚、用户交互</td>
      <td>用来筛模型和 provider 的基础 function calling 能力</td>
    </tr>
    <tr>
      <td><strong>API-Bank</strong></td>
      <td>工具增强 LLM 的基础任务、调用能力和对话场景</td>
      <td>复杂真实 API 环境和长期状态</td>
      <td>用来理解 tool-augmented LLM 的早期能力边界</td>
    </tr>
    <tr>
      <td><strong>ToolBench</strong></td>
      <td>大规模真实 API 上的工具检索、选择和调用</td>
      <td>API 漂移导致的可复现性问题</td>
      <td>用来测长尾 API 生态下的工具选择能力</td>
    </tr>
    <tr>
      <td><strong>StableToolBench</strong></td>
      <td>在更稳定的环境中复现实用工具调用评测</td>
      <td>真实生产系统里的权限、延迟和用户约束</td>
      <td>用来减少 API 漂移对评测结论的污染</td>
    </tr>
    <tr>
      <td><strong>AgentBench</strong></td>
      <td>多环境 agent 能力，包括操作、规划、代码和决策</td>
      <td>单一工具协议细节</td>
      <td>用来看模型是否具备更广义的 agent 行为能力</td>
    </tr>
    <tr>
      <td><strong>tau-bench</strong></td>
      <td>真实业务域中的用户-代理-工具交互，以及多次试验下的可靠性</td>
      <td>纯 function call 格式细节</td>
      <td>用来判断 agent 在业务流程里是否稳定，而不是只会调用函数</td>
    </tr>
  </tbody>
</table>
</div>

我的建议是用三层评测，而不是押一个榜单：

1. **协议层**：用 BFCL 或自建 schema tests，看模型能否稳定生成正确 tool call。
2. **轨迹层**：用 ToolBench、StableToolBench 或内部工具任务集，看多步调用是否可靠。
3. **业务层**：用 tau-bench 风格的用户模拟和 policy checks，看 agent 是否真的完成业务目标。

这样评测才对应真实故障。否则你会得到一个“function call 很强，但业务流程经常失败”的模型。

### 六、如果你在做类 Codex agent，应该怎么设计

<div class="tu-badges">
  <span class="tu-badge">工程推断</span>
  <span class="tu-badge">需要本地 benchmark 验证</span>
</div>

类 Codex agent 的核心不是聊天，而是把模型动作落到工作区、终端、文件、浏览器和外部服务上。这里 tool use 的设计要保守。

**第一，内部协议必须先稳定。**
不要让 OpenAI、Anthropic、Gemini、DeepSeek 的原生 tool call 对象直接进入业务逻辑。内部先定义统一事件：

- `tool_call_requested`
- `tool_call_validated`
- `tool_call_started`
- `tool_call_succeeded`
- `tool_call_failed`
- `tool_result_attached`

provider adapter 只负责把外部协议翻译成内部事件。这样换模型时，改的是 adapter，不是整个 agent。

**第二，工具执行层要独立于模型层。**
模型负责提出意图，执行器负责权限、沙箱、幂等、超时、重试和日志。尤其是 coding agent，写文件、跑命令、发网络请求都不是普通函数调用，必须有独立的安全边界。

**第三，thinking 与 tool result 要分开保存。**
DeepSeek、Gemini 这类模型对 thinking 或 thought signatures 有额外约束。工程上不要把“模型内部推理”“工具调用参数”“工具输出”“最终回答”混成一个字符串。混在一起后，复现、压缩上下文和跨 provider 迁移都会变困难。

**第四，benchmark 要进入 CI。**
不要只在接入当天跑一次 demo。应该维护一组小而稳定的工具任务：文件编辑、命令执行、搜索、失败重试、参数校验、并行工具、权限拒绝、工具超时。每接一个 provider，都跑同一套任务。

### 结论：tool use 不是能力点，是系统边界

tool use 最初看起来像模型能力：会不会调用函数。
但在 agent 系统里，它更像系统边界：模型、工具执行器、状态存储、权限控制和评测器之间，谁对哪一步负责。

所以我更愿意用一句话总结这轮调研：

<div class="tu-callout">
  <p><strong>tool use 的成熟标志，不是模型能返回一个漂亮的 JSON，而是系统能把一串不完美的工具调用变成可恢复、可审计、可评测的执行轨迹。</strong></p>
</div>

这也是为什么类 Codex agent 不应该把 provider 的 tool use 当成黑盒能力直接塞进主流程。你可以换模型，但执行循环、工具权限、状态回填和 benchmark 必须掌握在自己的系统里。

<div class="tu-source">
<strong>资料来源</strong>：
<a href="https://developers.openai.com/api/docs/guides/tools">OpenAI Using tools</a>，
<a href="https://developers.openai.com/api/docs/guides/function-calling">OpenAI Function calling</a>，
<a href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">Anthropic Tool use</a>，
<a href="https://ai.google.dev/gemini-api/docs/function-calling">Gemini Function calling</a>，
<a href="https://api-docs.deepseek.com/guides/tool_calls">DeepSeek Tool Calls</a>，
<a href="https://docs.mistral.ai/studio-api/conversations/function-calling">Mistral Function Calling</a>，
<a href="https://docs.x.ai/developers/tools/function-calling">xAI Function Calling</a>，
<a href="https://qwen.readthedocs.io/en/stable/framework/function_call.html">Qwen Function Calling</a>，
<a href="https://docs.cohere.com/v2/docs/tool-use-overview">Cohere Tool use</a>；
以及论文
<a href="https://arxiv.org/abs/2302.04761">Toolformer</a>，
<a href="https://arxiv.org/abs/2305.15334">Gorilla</a>，
<a href="https://arxiv.org/abs/2307.16789">ToolLLM</a>，
<a href="https://arxiv.org/abs/2304.08244">API-Bank</a>，
<a href="https://arxiv.org/abs/2406.18518">APIGen</a>，
<a href="https://arxiv.org/abs/2409.00920">ToolACE</a>，
<a href="https://arxiv.org/abs/2403.07714">StableToolBench</a>，
<a href="https://arxiv.org/abs/2308.03688">AgentBench</a>，
<a href="https://arxiv.org/abs/2406.12045">tau-bench</a>，
<a href="https://arxiv.org/abs/2503.09516">Search-R1</a>，
<a href="https://arxiv.org/abs/2312.04511">LLMCompiler</a>，
<a href="https://arxiv.org/abs/2411.15399">Less is More</a>，
<a href="https://arxiv.org/abs/2502.11271">OctoTools</a>。

本文对厂商训练细节的表述，依据公开论文、官方文档和可公开验证的接口行为。没有公开细节的部分，只作为工程推断处理。
</div>
