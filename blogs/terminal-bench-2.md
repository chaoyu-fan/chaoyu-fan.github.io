---
layout: page
permalink: /blogs/terminal-bench-2/index.html
title: Terminal-Bench 2.0 完全导读
description: 基于 tbench.ai、Harbor 与 Hugging Face 官方说明，纠正上一版不准确的任务清单，并补齐运行、结果文件、trajectory、reward 与提交要求。
---

## Terminal-Bench 2.0 完全导读

> 更新时间：2026/04/17  
> 文章定位：官方资料核对版，重点补齐运行流程、结果目录、trajectory / reward 文件和榜单提交要求。

上一版这篇文章里，最大的问题不是措辞，而是我把 **89 个任务**写成了一份看起来很完整、其实并不可靠的“中文分类清单”。

这次我重新对照了 Terminal-Bench 官方站点、Terminal-Bench 2.0 论文、Harbor 官方文档，以及 Hugging Face 的官方 leaderboard 提交说明。结论很简单：

- **Terminal-Bench 2.0 确实是 89 个任务。**
- **官方站点也确实提供任务浏览页面。**
- **但我上一版那种“我替官方重新分好的 89 题中文 taxonomy”，并不是官方发布的标准任务结构。**

所以这次我不再继续维护那份不准确的清单，而是把文章改成一篇更实用、也更可信的版本：

- Terminal-Bench 2.0 到底是什么
- 官方资料里到底确认了哪些事实
- 现在应该怎么跑
- 跑完之后 job / trial / trajectory / reward 文件分别长什么样
- 如果你想上榜，提交目录到底要怎么组织

<style>
.tb-lead p{color:#3d5060;line-height:1.82}
.tb-table{width:100%;border-collapse:collapse;margin:1rem 0 1.2rem;font-size:.96rem}
.tb-table th,.tb-table td{border-bottom:1px solid #dde4ea;padding:.75rem .55rem;text-align:left;vertical-align:top}
.tb-table th{color:#405361}
.tb-note{color:#596977;font-size:.92rem;line-height:1.78}
.tb-callout{background:#f6fbfd;border-left:4px solid #4a7a8c;padding:1rem 1rem .9rem;border-radius:10px;margin:1rem 0}
.tb-card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0 1.25rem}
.tb-card{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:1rem 1rem .9rem}
.tb-card h3{margin:.1rem 0 .5rem;font-size:1rem;line-height:1.45;color:#304552}
.tb-card p{margin:0;color:#556674;font-size:.92rem;line-height:1.72}
.tb-code{background:#fbfcfe;border:1px solid #dce5ec;border-radius:10px;padding:.9rem 1rem;margin:1rem 0 1.2rem}
.tb-code pre{margin:0;white-space:pre-wrap;word-break:break-word}
.tb-mini{font-size:.9rem;color:#61707d}
.tb-source li{margin:.45rem 0;line-height:1.72;color:#42586a}
@media (max-width: 720px){
  .tb-card-grid{grid-template-columns:1fr}
}
</style>

<div class="blk-v2 tb-lead">
  <div class="sh-v2">先把官方事实说清楚</div>
  <p><strong>官方 benchmark 页面</strong>明确写着：<a href="https://www.tbench.ai/benchmarks/terminal-bench-2">Terminal-Bench 2.0</a> 目前展示 <strong>89 tasks</strong>。</p>
  <p><strong>Terminal-Bench 2.0 论文</strong>则进一步说明：这 89 个任务来自 93 位贡献者提交的 229 个候选任务，最终筛出 89 个进入正式 benchmark；每个任务都带有独立环境、人工编写的参考解、以及用于验证终态的测试。</p>
  <p>论文还强调了一点：它测的不是“你中间说得像不像”，而是<strong>最终容器状态有没有满足任务要求</strong>。换句话说，这是 outcome-driven benchmark，而不是 chat-style benchmark。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">为什么上一版的任务清单不该继续保留</div>
  <div class="tb-callout">
    正确的做法，不是我替官方硬造一份“89 题中文总分类”，而是把官方已经确认的信息写准确，并把读者指向官方任务浏览器。
  </div>
  <p>我重新核对后发现，官方资料里可以被稳定确认的是：</p>
  <ul>
    <li>官方任务总数是 89。</li>
    <li>官方任务浏览页支持按 category、tag、difficulty 过滤。</li>
    <li>论文给出了高层类别分布：软件工程是最大类，同时覆盖 system administration、data science、security、scientific computing、file operations 等类别；论文还明确说，数据集中也包含 personal assistant、video processing 这类非传统“纯软件工程”任务。</li>
  </ul>
  <p>但官方并没有在我这次核对的文档里，给出一份与我上一版完全对应的“89 个任务中文重分组清单”。所以继续保留那份清单，只会让文章看起来更完整，却更不准确。</p>
  <p class="tb-note">如果你真想逐题看，最稳妥的方法是直接用官方任务页：<a href="https://www.tbench.ai/benchmarks/terminal-bench-2">tbench.ai/benchmarks/terminal-bench-2</a>。它本身就是当前最准确的任务浏览入口。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">Terminal-Bench 2.0 真正在测什么</div>
  <div class="tb-card-grid">
    <div class="tb-card">
      <h3>环境发现</h3>
      <p>先读目录、依赖、配置、日志、测试入口，再决定怎么做。很多题第一步都不是写代码。</p>
    </div>
    <div class="tb-card">
      <h3>长链路执行</h3>
      <p>任务通常不是单点修补，而是探索、修改、运行、验证、交付的一整条链。</p>
    </div>
    <div class="tb-card">
      <h3>终态验证</h3>
      <p>最终看的是 verifier 能不能从容器终态里读出“你真的完成了”，而不是中间过程看起来像完成了。</p>
    </div>
    <div class="tb-card">
      <h3>工程收尾能力</h3>
      <p>文件路径、服务状态、输出格式、模型大小、测试结果，这些都属于真实交付的一部分。</p>
    </div>
  </div>
  <p class="tb-note">这也是为什么 Terminal-Bench 对 agent engineering 很有价值。它不是在测“会不会答题”，而是在测“会不会把工作做完”。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">如何运行 Terminal-Bench</div>
  <p>根据 Harbor 官方教程，<strong>Harbor 是 Terminal-Bench 2.0 的官方运行 harness</strong>。如果你今天要跑，请优先按 Harbor 的当前文档来，不要依赖旧博客或旧命令。</p>

  <table class="tb-table">
    <thead>
      <tr>
        <th>步骤</th>
        <th>当前官方说法</th>
        <th>我建议怎么理解</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>准备环境</td>
        <td>Harbor Quickstart 要求 Python 3.12+ 和 Docker。</td>
        <td>先把 Docker 跑起来，再装 Harbor。</td>
      </tr>
      <tr>
        <td>安装 Harbor</td>
        <td>Quickstart 推荐 <code>uv tool install harbor</code>。</td>
        <td>装完先用 <code>harbor --version</code> 验证。</td>
      </tr>
      <tr>
        <td>验证 Harbor 是否正常</td>
        <td>官方教程先跑 Oracle：<code>harbor run -d terminal-bench/terminal-bench-2 -a oracle</code></td>
        <td>这一步是 sanity check，先证明你的 Harbor、本地 Docker 和任务下载链路没问题。</td>
      </tr>
      <tr>
        <td>跑真实 agent</td>
        <td>官方教程示例是 Claude Code + Daytona。</td>
        <td>本地先小并发试跑，再决定是否上云扩容。</td>
      </tr>
    </tbody>
  </table>

  <div class="tb-code">
<pre><code>uv tool install harbor
harbor --version
</code></pre>
  </div>

  <p>先做最小验证：</p>

  <div class="tb-code">
<pre><code>harbor run -d terminal-bench/terminal-bench-2 -a oracle
</code></pre>
  </div>

  <p>然后再跑自己的 agent。以官方文档里的 Claude Code 例子来说：</p>

  <div class="tb-code">
<pre><code>export ANTHROPIC_API_KEY=&lt;YOUR-KEY&gt;

harbor run \
  -d terminal-bench/terminal-bench-2 \
  -m anthropic/claude-opus-4-1 \
  -a claude-code \
  --n-concurrent 4
</code></pre>
  </div>

  <p class="tb-note">这里有一个容易混淆的小点：Harbor 的一些旧文档和旧示例里还能看到 <code>terminal-bench@2.0</code> 这种写法，但我在 2026/04/17 核对的当前官方教程页，使用的是 <code>terminal-bench/terminal-bench-2</code>。如果你今天照着官方教程跑，优先用 slash 这一版。</p>

  <p>如果你要上 Daytona 跑更高并发，官方教程给的是：</p>

  <div class="tb-code">
<pre><code>export DAYTONA_API_KEY="&lt;your-daytona-api-key&gt;"
export ANTHROPIC_API_KEY="&lt;your-anthropic-api-key&gt;"

harbor run \
  -d terminal-bench/terminal-bench-2 \
  -m anthropic/claude-haiku-4-5 \
  -a claude-code \
  --env daytona \
  -n 32
</code></pre>
  </div>
</div>

<div class="blk-v2">
  <div class="sh-v2">跑完之后，结果目录里到底有什么</div>
  <p>这一部分是我觉得上一版最应该补的。Harbor 官方的 run-jobs 文档已经把 job 和 trial 的基本目录结构写得很清楚了。</p>

  <div class="tb-code">
<pre><code>jobs/job-name
├── config.json
├── result.json
├── trial-name
│   ├── config.json
│   ├── result.json
│   ├── agent
│   │   ├── recording.cast
│   │   └── trajectory.json
│   └── verifier
│       ├── ctrf.json
│       ├── reward.txt
│       ├── test-stderr.txt
│       └── test-stdout.txt
└── ...
</code></pre>
  </div>

  <table class="tb-table">
    <thead>
      <tr>
        <th>文件</th>
        <th>作用</th>
        <th>实战里最常怎么用</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>jobs/&lt;job&gt;/config.json</code></td>
        <td>整个 job 的配置</td>
        <td>回看当时用的 agent、model、dataset、并发参数。</td>
      </tr>
      <tr>
        <td><code>jobs/&lt;job&gt;/result.json</code></td>
        <td>聚合后的 job 结果</td>
        <td>看总 reward、成功率、错误概况。</td>
      </tr>
      <tr>
        <td><code>trial-name/config.json</code></td>
        <td>单个 trial 的配置</td>
        <td>排查某一题为何跑法与别题不同。</td>
      </tr>
      <tr>
        <td><code>trial-name/result.json</code></td>
        <td>单个 trial 的结果</td>
        <td>看单题是否成功、耗时、报错。</td>
      </tr>
      <tr>
        <td><code>agent/recording.cast</code></td>
        <td>终端录屏 / cast 记录</td>
        <td>复盘 agent 在 shell 里的实际操作顺序。</td>
      </tr>
      <tr>
        <td><code>agent/trajectory.json</code></td>
        <td>标准化 trajectory 文件</td>
        <td>做调试、SFT、RL 或 viewer 回放。</td>
      </tr>
      <tr>
        <td><code>verifier/ctrf.json</code></td>
        <td>测试报告</td>
        <td>看验证脚本到底哪一步挂了。</td>
      </tr>
      <tr>
        <td><code>verifier/reward.txt</code></td>
        <td>单 trial 奖励值</td>
        <td>最直接地判断这题成功没、奖励是多少。</td>
      </tr>
      <tr>
        <td><code>verifier/test-stdout.txt</code> / <code>test-stderr.txt</code></td>
        <td>verifier 输出</td>
        <td>定位失败原因最快的地方之一。</td>
      </tr>
    </tbody>
  </table>

  <p>如果你想开浏览器看这些结果，当前文档建议直接运行：</p>

  <div class="tb-code">
<pre><code>harbor view jobs
</code></pre>
  </div>

  <p class="tb-note">Harbor viewer 支持看 job、trial、trajectory、奖励、时长、错误、artifact，属于复盘 benchmark 结果时非常高频的工具。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">trajectory.json 里通常有什么</div>
  <p>Harbor 用的是 <strong>ATIF</strong>，也就是 Agent Trajectory Interchange Format。它不是一份随意日志，而是面向 debugging、trajectory replay、SFT 和 RL 的标准化 JSON 结构。</p>

  <p>官方 ATIF 文档里给出的核心字段大致包括：</p>

  <ul>
    <li>根对象：<code>schema_version</code>、<code>session_id</code>、<code>agent</code>、<code>steps</code>、可选的 <code>final_metrics</code></li>
    <li><code>agent</code>：agent 名称、版本、模型名</li>
    <li><code>steps</code>：按顺序记录每一步交互</li>
    <li>每个 <code>Step</code>：通常有 <code>step_id</code>、<code>timestamp</code>、<code>source</code>、<code>message</code></li>
    <li>agent step 还可以带 <code>reasoning_content</code>、<code>tool_calls</code>、<code>observation</code>、<code>metrics</code></li>
    <li><code>metrics</code>：prompt tokens、completion tokens、cached tokens、cost 等运行指标</li>
    <li><code>final_metrics</code>：总 token、总 cost、总 steps 等聚合指标</li>
  </ul>

  <p>如果你只把它当“对话记录”，会低估它的价值。更准确地说，它是一份结构化的 agent 运行轨迹：你能看到用户指令、agent 回复、工具调用、环境返回、token 和成本信息，甚至还能做回放和训练数据导出。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">reward 文件到底怎么写</div>
  <p>Harbor 的 task 文档把这件事写得非常明确：<strong>测试脚本必须在 <code>/logs/verifier/</code> 里产出 reward 文件</strong>，否则 verifier 没法判定任务结果。</p>

  <table class="tb-table">
    <thead>
      <tr>
        <th>文件</th>
        <th>格式</th>
        <th>适合什么场景</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>/logs/verifier/reward.txt</code></td>
        <td>纯文本数字，比如 <code>1</code> 或 <code>0</code></td>
        <td>最简单的 pass / fail 任务。</td>
      </tr>
      <tr>
        <td><code>/logs/verifier/reward.json</code></td>
        <td>JSON 数值字典，比如 <code>{"accuracy": 0.95, "runtime_sec": 1.23}</code></td>
        <td>你要同时输出多个数值指标时。</td>
      </tr>
    </tbody>
  </table>

  <p>Harbor 默认会先读 <code>reward.txt</code>，没有的话再回退到 <code>reward.json</code>。官方 task 文档给的示例也很直接：跑测试成功就往 <code>/logs/verifier/reward.txt</code> 写 <code>1</code>，失败就写 <code>0</code>。</p>

  <div class="tb-code">
<pre><code>#!/bin/bash

uvx pytest /tests/test.py

if [ $? -eq 0 ]; then
  echo 1 &gt; /logs/verifier/reward.txt
else
  echo 0 &gt; /logs/verifier/reward.txt
fi
</code></pre>
  </div>

  <p>另外，Harbor 还定义了几个特殊路径：</p>

  <ul>
    <li><code>/logs/verifier/</code>：reward 和 verifier 日志</li>
    <li><code>/logs/agent/</code>：agent 运行日志</li>
    <li><code>/logs/</code>：会在运行后下载回 host，方便调试</li>
    <li><code>/logs/artifacts/</code>：零配置 artifact 收集目录</li>
  </ul>
</div>

<div class="blk-v2">
  <div class="sh-v2">artifact 文件怎么保存</div>
  <p>如果你的任务会生成模型、输出文件、报告图、日志等需要带出容器的产物，Harbor 官方推荐直接写到 <code>/logs/artifacts/</code>。这样 trial 结束后会自动收集到 host 上。</p>

  <div class="tb-code">
<pre><code># Inside the sandbox
echo "result" &gt; /logs/artifacts/output.txt
cp model.pt /logs/artifacts/model.pt
</code></pre>
  </div>

  <p>收集后，trial 目录里通常会多出一个 <code>artifacts/</code> 文件夹，以及对应的 <code>manifest.json</code>：</p>

  <div class="tb-code">
<pre><code>&lt;trial_dir&gt;/
├── artifacts/
│   ├── manifest.json
│   ├── output.txt
│   └── hello.txt
├── agent/
├── verifier/
├── config.json
└── result.json
</code></pre>
  </div>

  <p class="tb-note">这对 leaderboard 提交也很重要，因为 Hugging Face 的官方提交流程明确要求：trial 目录里不能只有 <code>result.json</code>，还需要包含运行产出的其他 artifacts。</p>
</div>

<div class="blk-v2">
  <div class="sh-v2">如何提交到 Terminal-Bench 2.0 leaderboard</div>
  <p>这部分官方要求写得相当具体，基本可以直接照着做。</p>

  <p>提交仓库是这个 Hugging Face 数据集仓库：</p>
  <p><a href="https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard">harborframework/terminal-bench-2-leaderboard</a></p>

  <p>官方 README 里给出的提交流程是：</p>

  <ol>
    <li>Fork 仓库</li>
    <li>新建 branch</li>
    <li>把提交内容放到 <code>submissions/terminal-bench/2.0/&lt;agent&gt;__&lt;model(s)&gt;/</code></li>
    <li>开 Pull Request</li>
  </ol>

  <p>推荐的目录结构是：</p>

  <div class="tb-code">
<pre><code>submissions/
  terminal-bench/
    2.0/
      &lt;agent&gt;__&lt;model&gt;/
        metadata.yaml
        &lt;job-folder&gt;/
          config.json
          &lt;trial-1&gt;/result.json
          &lt;trial-2&gt;/result.json
          ...
</code></pre>
  </div>

  <p><code>metadata.yaml</code> 是必需的，README 里要求至少包含：</p>

  <div class="tb-code">
<pre><code>agent_url: https://...
agent_display_name: "My Agent"
agent_org_display_name: "Org"
models:
  - model_name: gpt-5
    model_provider: openai
    model_display_name: "GPT-5"
    model_org_display_name: "OpenAI"
</code></pre>
  </div>

  <p>更重要的是验证规则。要通过自动校验，官方目前要求：</p>

  <ul>
    <li><code>timeout_multiplier</code> 必须等于 <code>1.0</code></li>
    <li>不能覆盖 agent timeout</li>
    <li>不能覆盖 verifier timeout</li>
    <li>不能覆盖 CPU / memory / storage 资源</li>
    <li>所有 trial 目录都必须有合法的 <code>result.json</code></li>
    <li>所有 trial 目录都必须包含其他运行 artifacts</li>
    <li>每个 task 至少要评估 5 次，README 直接建议用 <code>-k 5</code></li>
    <li>agent 不能访问 Terminal-Bench 网站或 GitHub 仓库，否则会被判定为 reward hacking</li>
  </ul>

  <div class="tb-callout">
    这一条值得单独记住：如果你的 agent 会联网，记得显式阻止它访问 tbench.ai 和 benchmark 仓库。官方 README 已经把这件事写进自动校验规则里了。
  </div>
</div>

<div class="blk-v2">
  <div class="sh-v2">如果你正在做 agent，我会怎么用这套 benchmark</div>
  <p>我现在对 Terminal-Bench 2.0 的看法，比上一版更明确了：</p>
  <ul>
    <li>它最适合拿来检查一套 agent system 是否真的具备“终端里完成工作”的能力。</li>
    <li>它不适合被二手转述成“某某类别 12 题、某某类别 9 题”的伪精确清单。</li>
    <li>真正有价值的，是拿官方任务浏览器看任务本身，再用 Harbor 的 job / trial / trajectory / verifier 文件做失败分析。</li>
  </ul>

  <p>如果你是自己在做 coding agent，我会建议用下面这个顺序：</p>
  <ol>
    <li>先用 Oracle 跑通 Harbor，确认环境没问题。</li>
    <li>再小并发试跑自己的 agent，看最基础的成功率和失败簇。</li>
    <li>重点读 <code>trial/result.json</code>、<code>trajectory.json</code>、<code>reward.txt</code>、<code>test-stderr.txt</code>。</li>
    <li>等单次稳定后，再按 leaderboard 要求做更规范的多 trial 评估和提交。</li>
  </ol>
</div>

<div class="blk-v2">
  <div class="sh-v2">核对来源</div>
  <ul class="tb-source">
    <li><a href="https://www.tbench.ai/benchmarks/terminal-bench-2">Terminal-Bench 2.0 官方任务浏览页</a>：确认当前显示 89 tasks，并提供 category / tag / difficulty 过滤。</li>
    <li><a href="https://openreview.net/pdf?id=574281303882f822808ab57ac3a57a2bddfbc7a3">Terminal-Bench 2.0 论文</a>：确认 89 个正式任务、229 个候选任务、93 位贡献者、任务结构与高层类别信息。</li>
    <li><a href="https://www.harborframework.com/docs/tutorials/running-terminal-bench">Harbor: Running Terminal-Bench</a>：当前官方运行方式与 dataset 标识。</li>
    <li><a href="https://www.harborframework.com/docs/run-jobs/run-evals">Harbor: Run Evals</a>：job / trial 目录结构与结果查看方式。</li>
    <li><a href="https://www.harborframework.com/docs/tasks">Harbor: Tasks</a>：reward.txt / reward.json、/logs/verifier、/logs/agent 等特殊路径。</li>
    <li><a href="https://www.harborframework.com/docs/agents/trajectory-format">Harbor: Agent Trajectory Format (ATIF)</a>：trajectory.json 的结构与用途。</li>
    <li><a href="https://www.harborframework.com/docs/run-jobs/results-and-artifacts">Harbor: Artifact Collection</a>：/logs/artifacts 与 artifacts/manifest.json。</li>
    <li><a href="https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard">Hugging Face leaderboard 提交仓库</a>：metadata.yaml、提交目录和自动校验规则。</li>
  </ul>
</div>
