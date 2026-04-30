---
layout: page
permalink: /blogs/terminal-bench-score-update-2026-04-30/index.html
title: Terminal-Bench 2.0 提分日志：把 Wecode GPT-5.5 从 83.8% 推到 88.1%
description: 记录 2026-04-30 这次 Wecode GPT-5.5 Terminal-Bench 2.0 更新提交：从 373/445 提升到 392/445，以及背后的 agent harness 工程、错题闭环、提交清理和 Hugging Face PR 替换流程。
---

<style>
.tbup-lead{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1rem .9rem;border-radius:10px;margin:1rem 0 1.25rem}
.tbup-note{color:#586674;font-size:.92rem;line-height:1.8}
.tbup-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.35rem}
.tbup-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem}
.tbup-card h3{margin:.1rem 0 .55rem;color:#2f4756;font-size:1.02rem}
.tbup-card p{margin:.35rem 0;color:#536572;line-height:1.75}
.tbup-code{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:.95rem 1rem;margin:1rem 0 1.25rem}
.tbup-code pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:.9rem;line-height:1.65}
.tbup-table{width:100%;border-collapse:collapse;margin:1rem 0 1.3rem;font-size:.95rem}
.tbup-table th,.tbup-table td{border-bottom:1px solid #dde4ea;padding:.72rem .55rem;text-align:left;vertical-align:top}
.tbup-table th{color:#405361}
.tbup-list li{margin:.42rem 0;line-height:1.75;color:#42586a}
.tbup-kpi{font-size:1.55rem;color:#2f4756;font-weight:700;line-height:1.2}
.tbup-delta{color:#2f6c58;font-weight:700}
@media (max-width: 800px){.tbup-grid{grid-template-columns:1fr}.tbup-kpi{font-size:1.35rem}}
</style>

## Terminal-Bench 2.0 提分日志：把 Wecode GPT-5.5 从 83.8% 推到 88.1%

> 更新时间：2026/04/30  
> 文章定位：一次真实 leaderboard 分数更新的工程复盘。  
> 提交结果：<a href="https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard/discussions/164">Wecode GPT-5.5 PR #164</a>

<div class="tbup-lead">
  <p>上一篇我写的是如何把一次 Terminal-Bench 2.0 run 整理成符合提交要求的 leaderboard submission。这一篇记录今天的更新：同一个 Wecode GPT-5.5 submission，从 4 月 26 日的 83.8% 提到 4 月 30 日的 88.1%。真正值得写的不是多了一个数字，而是分数提升背后的工程闭环：agent harness 更稳、trace 更可分析、失败样本能复盘、提交包能替换、远端 PR 能被精确验证。</p>
</div>

这次更新的核心结果：

<table class="tbup-table">
  <thead>
    <tr><th>项目</th><th>上一次提交</th><th>本次更新</th><th>变化</th></tr>
  </thead>
  <tbody>
    <tr><td>Job folder</td><td><code>wecode-tb2-4-26-5</code></td><td><code>wecode-tb2-4-30-5</code></td><td>替换为新的 run</td></tr>
    <tr><td>Passing trials</td><td>373 / 445</td><td>392 / 445</td><td class="tbup-delta">+19</td></tr>
    <tr><td>Score</td><td>83.8%</td><td>88.1%</td><td class="tbup-delta">+4.3 个百分点</td></tr>
    <tr><td>Zero-reward trials</td><td>72</td><td>53</td><td class="tbup-delta">少 19 个</td></tr>
    <tr><td>95% CI half-width</td><td>约 ±1.8</td><td>约 ±1.7</td><td>误差范围略收窄</td></tr>
  </tbody>
</table>

本次远端 `result.json` 中的关键字段是：

<div class="tbup-code">
<pre>id: 164ac7f1-f71e-410b-9e9f-04c4ca60e3c9
n_total_trials: 445
n_errors: 101
mean: 0.8808988764044944
score: 392 / 445 = 88.1%
eval key: wecode-installed-thin__wecode-tb2-4-30-5</pre>
</div>

这里要特别说明：`n_errors = 101` 不是“错了 101 道”。它是 runner 记录的异常/错误事件计数，和最终 reward 不是同一个统计口径。leaderboard score 仍然按 reward 统计，本次是 392 个 passing trials，53 个 zero-reward trials。

## 1. 提分不是一次 prompt 调参，而是 harness 工程

Terminal-Bench 2.0 的难点在于它不是普通问答 benchmark。任务运行在真实终端环境里，agent 需要下载依赖、读文件、改代码、跑测试、处理网络和容器状态，最后由 verifier 判断结果。

所以分数提升通常不会来自一个单点技巧，而是来自一组基础设施能力：

<div class="tbup-grid">
  <div class="tbup-card">
    <h3>更稳的运行控制</h3>
    <p>减少因为网络延迟、长耗时构建、命令超时造成的非任务失败，让 agent 有机会把本来能解的题跑完。</p>
  </div>
  <div class="tbup-card">
    <h3>可恢复的执行状态</h3>
    <p>把 run 当成长期作业处理，而不是一次性脚本。失败后能定位到 trial，能续跑，能保留必要 trace。</p>
  </div>
  <div class="tbup-card">
    <h3>trace-driven debugging</h3>
    <p>从 runtime trace 和 trajectory 里找失败模式，而不是只看最后 reward。错误要能归因到工具调用、环境、依赖、策略或时间预算。</p>
  </div>
  <div class="tbup-card">
    <h3>提交包可验证</h3>
    <p>本地分数只有经过目录、metadata、trajectory、result、远端 PR 的一致性校验后，才真正变成 leaderboard submission。</p>
  </div>
</div>

换句话说，这次 4.3 个百分点的提升，本质上是把 agent 从“能做题”继续推向“能稳定做一批真实终端任务”。

## 2. 错题闭环：从 zero-reward 到可行动问题

这次分数从 373/445 到 392/445，表面上是多过了 19 个 trial。工程上更重要的问题是：这些 trial 为什么之前过不了，现在为什么能过？

我把失败样本分成几类看：

<ul class="tbup-list">
  <li><strong>环境型失败</strong>：依赖下载慢、构建耗时长、镜像或网络不稳定，agent 的策略本身可能没错，但运行没有完成。</li>
  <li><strong>时间预算型失败</strong>：任务路径正确，但在编译、训练、检索、长测试上花掉太多时间，需要 harness 更好地管理 timeout 和日志。</li>
  <li><strong>信息提取型失败</strong>：agent 没有读对 README、测试脚本或隐藏约束，导致修改方向偏了。</li>
  <li><strong>执行策略型失败</strong>：agent 发现了问题但没有形成最小可验证改动，或者没有及时跑 verifier 相关测试。</li>
  <li><strong>提交完整性问题</strong>：本地 run 通过不等于能上榜，trajectory、metadata、job folder、result 文件缺一块都会影响提交质量。</li>
</ul>

这个过程更像 error taxonomy，不是简单的“重新跑一次”。每一类失败都对应一类 harness 改进：网络、断点、日志、prompt、工具调用策略、结果归档。

## 3. 系统提示词改进：从泛化建议到终端任务协议

Terminal-Bench 里的 prompt 不是越长越好。更有效的方向是让系统提示词变成一种执行协议，减少 agent 在真实终端任务里的无效动作。

我更看重这几类约束：

<ul class="tbup-list">
  <li>先读任务说明和测试入口，不要直接猜实现。</li>
  <li>优先做最小可验证改动，避免大面积重构。</li>
  <li>把长耗时命令当作风险点，合理设置检查点。</li>
  <li>失败后先解释证据，再改下一步，不要盲目重复。</li>
  <li>最后用任务自己的 verifier 或测试脚本闭环。</li>
</ul>

这些听起来很普通，但在 445 个 trials 的规模下，普通规则会放大成稳定性差异。一个 task 里少一次错误路径，乘以 89 个任务、每个 5 次，就会变成可见的分数差。

## 4. runtime trace 是 agent harness 的显微镜

只看最终 `reward: 0`，信息量太低。真正有价值的是 trace：

<div class="tbup-code">
<pre>trial result
  -> agent trajectory
  -> command timeline
  -> stdout / stderr
  -> timeout / exit code
  -> verifier output
  -> failure category</pre>
</div>

这套链路能回答几个关键问题：

<ul class="tbup-list">
  <li>agent 是没有理解任务，还是理解了但没跑完？</li>
  <li>失败发生在依赖安装、编译、测试、数据下载，还是最终答案写入？</li>
  <li>timeout 是任务本身重，还是 agent 执行了低价值命令？</li>
  <li>同一 task 的 5 个 trials 是否表现一致，还是随机性很大？</li>
</ul>

这也是我现在更愿意把 Terminal-Bench 看作 agent harness benchmark，而不只是模型 benchmark。模型能力当然重要，但 harness 决定了模型能力能不能稳定落到终端状态上。

## 5. 提交更新：不新开 PR，而是在同一个 PR 替换内容

今天的提交要求不是“再开一个新的 PR”，而是更新同一个 Wecode GPT-5.5 submission。最后远端状态是：

<div class="tbup-code">
<pre>PR: https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard/discussions/164
path: submissions/terminal-bench/2.0/Wecode__GPT-5.5
commit: 3736af1af23981c014f5d9b149603fa051b92c85</pre>
</div>

这里踩过一个小坑：第一次上传 4-30 的新 run 后，远端目录同时保留了旧的 `wecode-tb2-4-26-5` 和新的 `wecode-tb2-4-30-5`。这不符合“替换同一路径内容”的意图，也容易让 reviewer 误解 submission root 下到底哪一个 job 是有效结果。

最终修正后的远端目录只剩：

<div class="tbup-code">
<pre>Wecode__GPT-5.5/
  metadata.yaml
  wecode-tb2-4-30-5/
    config.json
    result.json
    ... 445 trial folders ...</pre>
</div>

旧路径 `wecode-tb2-4-26-5` 用 Hugging Face API 验证已经返回 `404 EntryNotFound`。

## 6. 本次提交前后的清理项

为了让 submission 更像一个可审计 release，我继续沿用了上一次沉淀的清理流程：

<ul class="tbup-list">
  <li>删除本地运行残留：<code>wecode-home</code>、<code>wecode.jsonl</code>、<code>wecode.stderr.txt</code>。</li>
  <li>删除 preflight 和运行侧文件：<code>wecode-proxy-preflight.txt</code>、<code>wecode-run-profile.json</code>、<code>wecode-run-status.json</code>。</li>
  <li>删除 job log 索引类文件：<code>job.log</code>、<code>job-log-index*</code>、<code>killed-active-trials-*.tsv</code>。</li>
  <li>保留必要审计材料：每个 trial 的 <code>result.json</code> 和 passing trajectory。</li>
  <li>system prompt 字段保持空字段，不用 <code>REDACTED</code> 文案污染提交内容。</li>
  <li>保持 job-level <code>result.json</code>，方便远端和人工快速判断分数来源。</li>
</ul>

本地 official-like validation 的结果是：

<div class="tbup-code">
<pre>official_like_errors: 0
job_count: 1
trial_count: 445
success: 392
task_count: 89</pre>
</div>

远端再次验证：

<div class="tbup-code">
<pre>metadata.yaml: exists
wecode-tb2-4-30-5/config.json: exists
wecode-tb2-4-30-5/result.json: exists
wecode-tb2-4-26-5: 404 EntryNotFound</pre>
</div>

## 7. 我从这次提分里总结出的 engineering knowhow

<div class="tbup-grid">
  <div class="tbup-card">
    <h3>把 benchmark run 当作实验系统</h3>
    <p>一次 run 不只是一个分数，而是 445 条可归因样本。每条样本都应该能追到配置、trace、结果和提交状态。</p>
  </div>
  <div class="tbup-card">
    <h3>优化 harness 比盲目换 prompt 更重要</h3>
    <p>prompt 会影响行为，但网络、timeout、续跑、日志、清理和验证决定了行为能否稳定兑现。</p>
  </div>
  <div class="tbup-card">
    <h3>错题要形成 taxonomy</h3>
    <p>不要只统计失败个数。要把失败拆成环境、时间、理解、执行、验证和提交结构问题。</p>
  </div>
  <div class="tbup-card">
    <h3>leaderboard submission 是 release</h3>
    <p>能跑出分数只是第一步。能被官方 repo 接收、审计、复算，才是完整工程闭环。</p>
  </div>
</div>

如果把这件事放到更学术的说法里，我会把它概括成：面向 outcome-driven terminal tasks 的自适应 agent harness。它不是让 agent 在一次对话里“看起来聪明”，而是通过运行轨迹、失败归因、恢复机制和提交验证，把 agent 的端到端任务完成率一点点推上去。

## 参考链接

<ul class="tbup-list">
  <li>Terminal-Bench 2.0 leaderboard：<a href="https://www.tbench.ai/leaderboard/terminal-bench/2.0">https://www.tbench.ai/leaderboard/terminal-bench/2.0</a></li>
  <li>Terminal-Bench 2.0 submission repo：<a href="https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard">https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard</a></li>
  <li>Wecode GPT-5.5 PR #164：<a href="https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard/discussions/164">https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard/discussions/164</a></li>
  <li>上一篇复盘：<a href="/blogs/terminal-bench-submission-engineering/">Terminal-Bench 2.0 提交复盘：从跑分、轨迹清理到 Hugging Face PR</a></li>
</ul>
