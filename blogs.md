---
layout: page
permalink: /blogs/index.html
title: Notes
description: Technical notes and essays by Chaoyu Fan on agent system design, research process, and applied machine learning.
---

<div class="blk-v2">
  <div class="sh-v2">Notes &amp; Writing</div>
  <p style="color:#3d5060;line-height:1.75;max-width:680px;">This section will collect technical notes, research reflections, and essays on AI systems and engineering. The goal is writing that is practical and worth returning to — not frequent posts for their own sake.</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">Planned Topics</div>
  <div class="ri-grid">
    <div class="ri-card c-blue">
      <div class="ri-title">Agent System Design</div>
      <p>Notes on building reliable multi-agent workflows — memory management, tool orchestration, failure recovery, and evaluation.</p>
    </div>
    <div class="ri-card c-violet">
      <div class="ri-title">Research Process</div>
      <p>How I approach literature synthesis, experiment tracking, and turning vague research questions into executable systems.</p>
    </div>
    <div class="ri-card c-teal">
      <div class="ri-title">Engineering &amp; ML</div>
      <p>Practical notes on applying machine learning to industrial optimization problems — what works, what doesn't, and why.</p>
    </div>
  </div>
  <p style="color:#3d5060;margin-top:1.5rem;font-size:.9rem;">First posts coming soon. Subscribe via <a href="https://github.com/chaoyu-fan" style="color:#2e4f63;">GitHub</a> or check back here.</p>
</div>


<div class="blk-v2">
  <div class="sh-v2">Latest Post</div>
  <div class="ri-grid">
    <div class="ri-card c-teal">
      <div class="ri-title">用进化算法优化 LLM Agent 的工具调用</div>
      <p>梳理 EvoTool、GEPA、SPRIG、EvoSkill、SkillMOO 等工作，讨论遗传/进化算法如何优化 tool-use policy，并提出 Causal-Pareto Tool Evolution 作为面向长链路 agent 的研究方案。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/evolutionary-tool-use-optimization/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-violet">
      <div class="ri-title">大模型 tool use 的真正分歧：谁拥有执行循环</div>
      <p>比较 OpenAI、Anthropic、Gemini、DeepSeek、Mistral、xAI、Qwen、Cohere 的工具调用模式，并说明为什么 tool use 的关键不是 JSON，而是执行循环、状态回填和评测边界。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/tool-use-landscape-2026/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-blue">
      <div class="ri-title">AI agents 如何重组 SCI 写作流程</div>
      <p>基于一条抖音视频口播稿，拆解 SCI 写作的模块化套路、真正卡住研究生的四座山，以及 AI agents 在选题、文献综述、数据分析和初稿生成中的合理位置。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/ai-agents-sci-writing-workflow/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-violet">
      <div class="ri-title">学术写作 AI 提示词手册：从论文润色、翻译到审稿回复</div>
      <p>整理一套面向学术写作场景的 AI 提示词，覆盖角色预设、论文撰写、学术润色、中英翻译、降重改写、参考文献、投稿审稿和文献阅读。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/academic-ai-prompts/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-teal">
      <div class="ri-title">LLM Agent Harness 的协议适配问题：从一次 GLM-5.1 接入失败说起</div>
      <p>记录一次把硅基流动 GLM-5.1 接入 Codex/Wecode 类 harness 的真实排障过程，并分析 Responses API 与 Chat Completions API 在 agent 系统里的协议边界。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/agent-harness-protocol-mismatch/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-blue">
      <div class="ri-title">Terminal-Bench 2.0 提分日志：把 Wecode GPT-5.5 从 83.8% 推到 88.1%</div>
      <p>记录 2026/04/30 这次更高分提交：从 373/445 到 392/445，以及背后的 agent harness 工程、trace 分析、错题闭环和同一个 Hugging Face PR 替换提交。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/terminal-bench-score-update-2026-04-30/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-teal">
      <div class="ri-title">Terminal-Bench 2.0 提交复盘：从跑分、轨迹清理到 Hugging Face PR</div>
      <p>记录一次 Wecode GPT-5.5 leaderboard submission 的完整工程过程：跑分、误差范围、metadata、trajectory、system prompt 清理、目录结构和 PR 提交。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/terminal-bench-submission-engineering/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-violet">
      <div class="ri-title">GPT-Image-2 提示词仓库整理：真正可复用的是四种写法</div>
      <p>基于一个高质量 GitHub prompt 仓库，整理出人像、海报、角色设定和 UI/信息图四类最值得复用的写法，并补上可直接改的中文模板。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/gpt-image-2-prompts/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-blue">
      <div class="ri-title">OpenClaw 办公智能体全景拆解</div>
      <p>基于 19 张演示截图，拆解它到底是在卖办公问答助手，还是一套真正会执行任务的工作流 agent。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/openclaw-office-agents/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-violet">
      <div class="ri-title">Terminal-Bench 2.0 完全导读</div>
      <p>基于 tbench.ai、Harbor 与 Hugging Face 官方说明，纠正上一版不准确的任务清单，并补齐运行、结果文件与提交要求。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/terminal-bench-2/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-blue">
      <div class="ri-title">Claude Code 开始长成一个生态了</div>
      <p>从教程、skills 到多智能体编排，整理这轮热门项目真正说明了什么，以及更稳的入场顺序。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/claude-code-ecosystem/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
    <div class="ri-card c-teal">
      <div class="ri-title">初创公司股权分配：把“出资”和“出力”拆开算</div>
      <p>从三人合伙的真实场景出发，聊清楚创业初期怎么分股更稳，并附上几份能直接改的协议模板骨架。</p>
      <p style="margin-top:.6rem;"><a href="/blogs/startup-equity-split/" style="color:#2e4f63;font-weight:600;">阅读全文 →</a></p>
    </div>
  </div>
</div>
