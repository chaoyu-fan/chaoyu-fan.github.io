---
layout: page
permalink: /blogs/tool-use-landscape-2026/index.html
title: 大模型 tool use 版图：协议、训练、优化与评测
description: 对 OpenAI、Anthropic、Gemini、DeepSeek、Mistral、Cohere 的 tool use 差异做一次可落地的对比，并整理训练方法、优化研究和基准评测。
---

<style>
.tu-lead{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1rem .95rem;border-radius:10px;margin:1rem 0 1.2rem}
.tu-callout{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem 1rem .95rem;margin:1rem 0 1.2rem}
.tu-callout p{margin:0;color:#405160;line-height:1.75}
.tu-wrap{overflow-x:auto;margin:1rem 0 1.2rem}
.tu-table{width:100%;border-collapse:collapse;min-width:860px;font-size:.95rem}
.tu-table th,.tu-table td{border-bottom:1px solid #dde4ea;padding:.72rem .55rem;text-align:left;vertical-align:top}
.tu-table th{color:#34495a}
.tu-table td{color:#4b5c69;line-height:1.72}
.tu-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.2rem}
.tu-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem}
.tu-card h3{margin:.05rem 0 .45rem;color:#2f4756;font-size:1.02rem}
.tu-card p{margin:0;color:#536572;line-height:1.75}
.tu-list li{margin:.35rem 0;line-height:1.75;color:#42586a}
.tu-source{margin-top:1.35rem;padding-top:1rem;border-top:1px solid #dde4ea;color:#56636f;font-size:.92rem;line-height:1.8}
@media (max-width: 840px){.tu-grid{grid-template-columns:1fr}}
</style>

## 大模型 tool use 版图：协议、训练、优化与评测

> 更新时间：2026/05/16  
> 文章定位：技术调研 + 工程落地笔记。

tool use 不是“模型会不会调 API”这么简单。真正决定一个 agent 能不能跑起来的，通常是三件事：

1. 模型什么时候决定调用工具
2. 调用参数能不能稳定落到 schema
3. 工具结果能不能正确回灌到下一轮推理

把这三层拆开看，主流厂商的差异就很清楚了。

<div class="tu-callout">
  <p><strong>先给结论：</strong>现阶段没有一家是“全场景最强”。OpenAI 更像统一的 agent 平台入口，Anthropic 更强调显式 tool event loop，Gemini 更擅长多工具并行和串联，DeepSeek 更像 OpenAI 风格兼容层里补上了 thinking 和 strict schema，Mistral、xAI、Qwen 和 Cohere 则分别站在经典函数调用、OpenAI-compatible 调用、开源模型工具模板和企业检索增强这些位置上。</p>
</div>

### 主流差异

<div class="tu-wrap">
<table class="tu-table">
  <thead>
    <tr>
      <th>厂商</th>
      <th>主接口</th>
      <th>典型模式</th>
      <th>具体模式</th>
      <th>工程上的意义</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>OpenAI</strong></td>
      <td>Responses API + function calling</td>
      <td>custom function, hosted tools, remote MCP, `tool_choice`, structured outputs</td>
      <td>统一的 agent 入口，和 built-in tools 一起收敛到同一套调用面</td>
      <td>适合做统一 agent 层，少折腾协议转换，但要接受 Responses API 作为主入口</td>
    </tr>
    <tr>
      <td><strong>Anthropic</strong></td>
      <td>Messages API + <code>tools</code></td>
      <td><code>tool_use</code> / <code>tool_result</code> blocks, <code>tool_choice</code>, parallel tool use</td>
      <td>显式 event loop，client-side tools 和 server-side tools 区分清楚</td>
      <td>适合显式控制工具循环，做多轮交互和工具回填时很顺手</td>
    </tr>
    <tr>
      <td><strong>Gemini</strong></td>
      <td><code>function_declarations</code> + <code>functionCall</code></td>
      <td><code>AUTO</code> / <code>ANY</code> / <code>NONE</code>, parallel function calling, compositional function calling</td>
      <td>函数调用和 thought signatures 绑定，适合多轮和并行工具链</td>
      <td>适合多工具并行、串联调用，SDK 能帮你省掉很多胶水代码</td>
    </tr>
    <tr>
      <td><strong>DeepSeek</strong></td>
      <td>Chat Completions + <code>tools</code></td>
      <td>OpenAI-style <code>tools</code>, <code>tool_choice</code>, beta strict schema, thinking mode tool calls</td>
      <td>OpenAI-like 兼容层，强调 strict JSON schema 和 thinking mode 回传</td>
      <td>适合想要 OpenAI 风格调用方式、但又需要更严格 JSON 约束的场景</td>
    </tr>
    <tr>
      <td><strong>Mistral</strong></td>
      <td>Chat / Function Calling</td>
      <td>function calling, tool call response, tool result replay, agent function calling</td>
      <td>经典 chat/function calling 路线，支持 tool_choice 与 parallel_tool_calls</td>
      <td>更像经典 tool calling，适合简单直接的工具链</td>
    </tr>
    <tr>
      <td><strong>xAI</strong></td>
      <td>OpenAI-compatible chat + tools</td>
      <td>function calling, parallel function calling 默认开启</td>
      <td>兼容 OpenAI 风格，默认并行 function calling</td>
      <td>适合已有 OpenAI Chat Completions 兼容层的系统快速接入</td>
    </tr>
    <tr>
      <td><strong>Qwen</strong></td>
      <td>Qwen-Agent / OpenAI-compatible serving</td>
      <td>函数调用模板、结构化解析、vLLM/Ollama 等 serving parser</td>
      <td>开源模型侧更依赖模板、parser 和 serving 层的函数解析</td>
      <td>适合自托管和开源模型场景，但要重点验证模板、parser 和 thinking 输出的兼容性</td>
    </tr>
    <tr>
      <td><strong>Cohere</strong></td>
      <td>Chat endpoint</td>
      <td>single-step tool use, multi-step tool use, citations</td>
      <td>企业检索和证据型输出优先，citations 是显式卖点</td>
      <td>如果你很看重引用和可追溯输出，它的产品定位很清楚</td>
    </tr>
  </tbody>
</table>
</div>

### 这件事本质上分四层

<div class="tu-grid">
  <div class="tu-card">
    <h3>1. 触发层</h3>
    <p>模型要先判断“要不要调用工具”。这一步决定的是路径选择，不是答案本身。很多失败其实发生在这里，模型压根没意识到该查、该算、该问外部系统。</p>
  </div>
  <div class="tu-card">
    <h3>2. 参数层</h3>
    <p>工具决定以后，参数能不能填对更关键。字段名、类型、枚举、必填项、日期格式，这些小东西最容易把 agent 拉垮。</p>
  </div>
  <div class="tu-card">
    <h3>3. 编排层</h3>
    <p>单次调用只是起点。真实任务通常需要多工具并行、串联、重试和状态回写。Gemini、Anthropic 这类接口在这里的表达力更强。</p>
  </div>
  <div class="tu-card">
    <h3>4. 闭环层</h3>
    <p>工具结果必须回到模型上下文里，下一轮推理才能继续。没有这个闭环，tool use 只是“发了个请求”，不是 agent loop。</p>
  </div>
</div>

### tool use 是怎么训练出来的

从公开资料看，主流路线不是单一的。大致有三种。

- **监督式轨迹学习**。Toolformer 这类工作会把“何时调用、调哪个工具、填什么参数、怎么消化结果”直接写进训练目标里。它的关键点不是把模型训练成会聊天，而是训练成会在合适位置插入 API 调用。
- **大规模合成轨迹**。Gorilla、ToolLLM、APIGen、ToolACE 都在做类似事情，只是数据构造方式不同。有的从真实 API 文档和检索器出发，有的直接合成可验证指令和 solution path，目标都是把“可学习的工具轨迹”做厚。
- **奖励驱动优化**。最近更明显的趋势，是把工具交互当成可优化 trajectory 来做。Search-R1 这类工作已经明确把多轮 search/tool 交互放进 RL 里，优化的不只是最终答案，还有中间路径是否值得走。

我自己的判断是：**tool use 的训练，正在从“教模型学会一条 API 语法”，转向“教模型在任务轨迹里做正确的动作选择”。**

### 有 tool use optimization 研究吗

有，而且已经不是边角料。

<div class="tu-wrap">
<table class="tu-table">
  <thead>
    <tr>
      <th>方向</th>
      <th>代表工作</th>
      <th>优化目标</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>数据生成优化</td>
      <td>Toolformer, ToolLLM, APIGen, ToolACE</td>
      <td>提高覆盖率、可验证性、轨迹质量</td>
    </tr>
    <tr>
      <td>稳定性优化</td>
      <td>StableToolBench</td>
      <td>让不稳定 API 和噪声评测变得可重复</td>
    </tr>
    <tr>
      <td>搜索/决策优化</td>
      <td>Search-R1</td>
      <td>让模型学会更合理地发起多轮搜索或工具查询</td>
    </tr>
    <tr>
      <td>并行执行优化</td>
      <td>LLMCompiler</td>
      <td>把独立工具调用拆开并行执行，降低延迟</td>
    </tr>
    <tr>
      <td>异步执行优化</td>
      <td>Asynchronous LLM Function Calling</td>
      <td>避免同步函数调用把推理线程卡住</td>
    </tr>
    <tr>
      <td>缓存与边缘优化</td>
      <td>Less is More, ToolCaching</td>
      <td>减少重复调用和边缘场景下的工具开销</td>
    </tr>
  </tbody>
</table>
</div>

这里我想强调一个判断：**tool use optimization 不是只优化“更准”，而是同时优化“更稳、更多步更少步、更快、更省”。**  
所以你会看到它既出现在训练论文里，也出现在系统论文里，还会出现在 benchmark 论文里。

### 基准评测到底在测什么

不同 benchmark 测的是不同失效模式。

- **BFCL**：更像 function calling 准确率和格式正确性测试，重点在“会不会正确发起调用”
- **API-Bank**：更早期也更基础，关注工具增强 LLM 的效果、提升路径和障碍
- **ToolBench / StableToolBench**：关注大规模真实 API 生态，后者专门解决 API 状态漂移和评测不稳定
- **AgentBench**：看的是更广义的 agent 能力，在 8 个环境里测推理和决策
- **tau-bench**：更接近真实业务对话，强调用户-代理交互、策略约束和多次试验下的可靠性

如果把它们放在一起看，就能发现一件事：

**单轮 function call 正确，不等于 multi-turn agent 成功。**

### 如果你在做类 Codex agent，我会这样选

1. **先统一内部协议**。不要让每家模型的 tool call 形态直接污染你的业务层，内部先收敛成统一的 tool event schema。
2. **再写 provider adapter**。OpenAI 用 Responses API，Anthropic 用 <code>tool_use</code> / <code>tool_result</code>，Gemini 处理 thought signatures，DeepSeek 额外照顾 <code>strict</code> 和 beta endpoint。
3. **评测要分层**。BFCL 看调用正确性，tau-bench 看多轮可靠性，任务集自己的回归测试看最终业务成败。
4. **别只盯单点分数**。tool use 真正的瓶颈，通常是协议稳定性、回填一致性和多轮状态管理，不是模型会不会说话。

### 我这篇的结论

现有大模型厂商的 tool use 差异，表面上是 API 设计不同，实际是产品对 agent 的定义不同：

- 有的把 tool use 视作统一能力入口
- 有的把它视作显式事件流
- 有的把它视作多工具编排
- 有的把它视作严格 schema 的结构化输出问题

对开发者来说，最实用的做法不是赌一家“最好”，而是把自己的 agent 栈拆成协议层、调度层和评测层。  
这样你换模型时，改的是适配器，不是整个系统。

<div class="tu-source">
<strong>资料来源</strong>：
<a href="https://platform.openai.com/docs/guides/tools?api-mode=responses">OpenAI Using tools</a>，
<a href="https://platform.openai.com/docs/guides/function-calling/lifecycle">OpenAI Function calling</a>，
<a href="https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview">Anthropic Tool use</a>，
<a href="https://ai.google.dev/gemini-api/docs/function-calling">Gemini Function calling</a>，
<a href="https://api-docs.deepseek.com/guides/tool_calls">DeepSeek Tool Calls</a>，
<a href="https://docs.mistral.ai/capabilities/function_calling">Mistral Function Calling</a>，
<a href="https://docs.x.ai/developers/tools/function-calling">xAI Function Calling</a>，
<a href="https://qwen.readthedocs.io/en/stable/framework/function_call.html">Qwen Function Calling</a>，
<a href="https://docs.cohere.com/v2/docs/tool-use-overview">Cohere Tool use</a>，
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

本文对厂商“训练细节”的表述，主要依据公开论文、官方文档和可公开验证的实现约定。没有公开细节的部分，我只做了谨慎推断。
</div>
