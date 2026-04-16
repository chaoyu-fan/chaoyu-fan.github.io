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
.tb-table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
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
  <div class="sh-v2">89 个官方任务清单（中文对照）</div>
  <p class="tb-mini">下面这份表格是我在 2026/04/17 直接从 <a href="https://www.tbench.ai/benchmarks/terminal-bench-2">官网任务页</a>抓取并核对的当前 89 个任务。任务顺序、官方分类和难度以官网为准；中文名和任务内容是基于官网任务卡信息做的中文整理，方便快速浏览。</p>

  <div class="tb-table-wrap">
    <table class="tb-table">
      <thead>
        <tr>
          <th>任务分类</th>
          <th>任务名字</th>
          <th>中文名</th>
          <th>任务内容</th>
          <th>难易程度</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>adaptive-rejection-sampler</code></td>
          <td>自适应拒绝采样器</td>
          <td>用 R 实现自适应拒绝采样器，校验输入、检测对数凹性并附测试</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>bn-fit-modify</code></td>
          <td>贝叶斯网络拟合与修改</td>
          <td>从样本恢复贝叶斯网络 DAG，拟合后对 Y 做干预并重新采样</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>break-filter-js-from-html</code></td>
          <td>突破 HTML 中的 JS 过滤</td>
          <td>构造可绕过现有 HTML 过滤脚本的页面，使其自动触发 alert</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>调试<br><code>debugging</code></td>
          <td><code>build-cython-ext</code></td>
          <td>构建 Cython 扩展</td>
          <td>修复 pyknotid 与 Numpy 2.3 兼容问题并编译安装 Cython 扩展</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>build-pmars</code></td>
          <td>构建 pMARS</td>
          <td>从 Debian 源构建无 X11 依赖的 pMARS 并安装</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>build-pov-ray</code></td>
          <td>构建 POV-Ray</td>
          <td>下载并编译 POV-Ray 2.2，使其能渲染给定场景</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>机器学习<br><code>machine-learning</code></td>
          <td><code>caffe-cifar-10</code></td>
          <td>Caffe 训练 CIFAR-10</td>
          <td>安装 CPU 版 Caffe，并训练 CIFAR-10 模型 500 轮</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>cancel-async-tasks</code></td>
          <td>取消异步任务</td>
          <td>实现支持并发上限且在中断时仍能执行清理的异步任务调度函数</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>游戏<br><code>games</code></td>
          <td><code>chess-best-move</code></td>
          <td>国际象棋最佳着法</td>
          <td>从棋盘图片判断白方最佳着法并写入结果</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>circuit-fibsqrt</code></td>
          <td>电路实现 fibsqrt</td>
          <td>编写逻辑门电路文件，使模拟器输出 fib(isqrt(N))</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>cobol-modernization</code></td>
          <td>COBOL 现代化改造</td>
          <td>修复并现代化 COBOL 程序，使其正确处理输入并更新数据文件</td>
          <td>简单<br><code>easy</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>code-from-image</code></td>
          <td>从图像还原代码</td>
          <td>根据图片中的伪代码实现逻辑，并输出最终结果</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>compile-compcert</code></td>
          <td>编译 CompCert</td>
          <td>在当前系统上从源码构建并验证 CompCert 3.13.1 编译器</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>configure-git-webserver</code></td>
          <td>配置 Git Web 服务器</td>
          <td>配置 SSH Git 服务器，并将推送内容自动发布为网页</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>个人助理<br><code>personal-assistant</code></td>
          <td><code>constraints-scheduling</code></td>
          <td>约束式日程安排</td>
          <td>根据多人可用时间与已有冲突，安排满足约束的一小时会议</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>模型训练<br><code>model-training</code></td>
          <td><code>count-dataset-tokens</code></td>
          <td>统计数据集 token 数</td>
          <td>按 README 正确统计指定 Hugging Face 数据集 science 域的 deepseek token 数</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>crack-7z-hash</code></td>
          <td>破解 7z 哈希</td>
          <td>破解压缩包并恢复 secret_file.txt 中的单词</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>调试<br><code>debugging</code></td>
          <td><code>custom-memory-heap-crash</code></td>
          <td>自定义内存堆崩溃排查</td>
          <td>只修改 user.cpp，修复 RELEASE 模式崩溃问题</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>文件操作<br><code>file-operations</code></td>
          <td><code>db-wal-recovery</code></td>
          <td>数据库 WAL 恢复</td>
          <td>从损坏或异常的 SQLite WAL 中恢复完整数据库记录</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>机器学习<br><code>machine-learning</code></td>
          <td><code>distribution-search</code></td>
          <td>分布搜索</td>
          <td>寻找最符合目标 LLM 置信度指标的概率分布</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>dna-assembly</code></td>
          <td>DNA 组装</td>
          <td>设计含 egfp/FLAG 插入的 DNA 组装方案与引物</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>dna-insert</code></td>
          <td>DNA 插入</td>
          <td>设计引物，将输入质粒定点改造成目标质粒</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>文件操作<br><code>file-operations</code></td>
          <td><code>extract-elf</code></td>
          <td>提取 ELF 内容</td>
          <td>编写 Node 程序从 ELF 二进制中提取指定内存值并输出 JSON</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>文件操作<br><code>file-operations</code></td>
          <td><code>extract-moves-from-video</code></td>
          <td>从视频中提取动作序列</td>
          <td>下载 Zork 视频，转录并提取全部输入指令</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>数学<br><code>mathematics</code></td>
          <td><code>feal-differential-cryptanalysis</code></td>
          <td>FEAL 差分密码分析</td>
          <td>对给定 FEAL-like 实现做选择明文攻击，恢复 key[5]</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>数学<br><code>mathematics</code></td>
          <td><code>feal-linear-cryptanalysis</code></td>
          <td>FEAL 线性密码分析</td>
          <td>用线性密码分析从明密文对中恢复轮密钥</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>filter-js-from-html</code></td>
          <td>过滤 HTML 中的 JS</td>
          <td>编写 Python 过滤器移除 HTML 中的危险 JavaScript，并尽量保留安全内容</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据处理<br><code>data-processing</code></td>
          <td><code>financial-document-processor</code></td>
          <td>金融文档处理器</td>
          <td>对混合 PDF/JPG 文档做发票分类、字段抽取和结构化输出</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>fix-code-vulnerability</code></td>
          <td>修复代码漏洞</td>
          <td>按 CWE 定位并修复仓库中的安全漏洞</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>fix-git</code></td>
          <td>修复 Git 问题</td>
          <td>找回切回 master 后丢失的个人站点改动，并合并回主分支</td>
          <td>简单<br><code>easy</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>fix-ocaml-gc</code></td>
          <td>修复 OCaml 垃圾回收</td>
          <td>修复改造后的 OCaml GC，使编译器和运行时恢复正确</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>文件操作<br><code>file-operations</code></td>
          <td><code>gcode-to-text</code></td>
          <td>G-code 转文本</td>
          <td>从 G-code 打印路径判断最终印出的文字内容</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>git-leak-recovery</code></td>
          <td>Git 泄露恢复</td>
          <td>找回被重写历史删除的 secret，并彻底清理 Git 泄漏</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>git-multibranch</code></td>
          <td>多分支 Git 管理</td>
          <td>通过 SSH 搭建支持 main/dev 双分支部署的 Git 服务器</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>gpt2-codegolf</code></td>
          <td>GPT-2 代码高尔夫</td>
          <td>写一个无依赖 C 程序，用 TF ckpt 权重做 GPT-2 贪心采样</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>headless-terminal</code></td>
          <td>无头终端模式</td>
          <td>实现无头终端接口，支持按键、屏幕状态和进程交互</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>hf-model-inference</code></td>
          <td>Hugging Face 模型推理服务</td>
          <td>本地部署 Hugging Face 情感分类模型推理服务</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>install-windows-3.11</code></td>
          <td>安装 Windows 3.11</td>
          <td>在 QEMU 中启动 Windows 3.11，并按要求配置 VNC</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>kv-store-grpc</code></td>
          <td>gRPC 键值存储</td>
          <td>用 Python + gRPC 实现字符串键、数值值的 KV 服务</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>文件操作<br><code>file-operations</code></td>
          <td><code>large-scale-text-editing</code></td>
          <td>大规模文本编辑</td>
          <td>用高击键效率的 Vim 宏批量把百万行 CSV 转成目标格式</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数学<br><code>mathematics</code></td>
          <td><code>largest-eigenval</code></td>
          <td>最大特征值计算</td>
          <td>完成函数以求矩阵模最大的特征值和对应特征向量</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>机器学习<br><code>machine-learning</code></td>
          <td><code>llm-inference-batching-scheduler</code></td>
          <td>LLM 推理批处理调度器</td>
          <td>为静态图 LLM 推理系统实现 shape-aware 批处理调度器</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>数据处理<br><code>data-processing</code></td>
          <td><code>log-summary-date-ranges</code></td>
          <td>日志摘要日期区间提取</td>
          <td>汇总多份日志的日期范围、来源统计与时间覆盖情况</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>mailman</code></td>
          <td>配置 Mailman</td>
          <td>启动 Mailman3 + Postfix 邮件列表服务并满足基础邮件流要求</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>make-doom-for-mips</code></td>
          <td>让 Doom 跑在 MIPS 上</td>
          <td>用给定源码和 vm.js 让 Doom 在 MIPS 环境下跑起来并输出帧图</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>make-mips-interpreter</code></td>
          <td>编写 MIPS 解释器</td>
          <td>实现 MIPS 解释器，使给定 doomgeneric_mips ELF 可运行</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>mcmc-sampling-stan</code></td>
          <td>Stan 的 MCMC 采样</td>
          <td>安装 RStan 并对层次贝叶斯模型做采样，估计后验均值</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>调试<br><code>debugging</code></td>
          <td><code>merge-diff-arc-agi-task</code></td>
          <td>合并 diff 的 ARC-AGI 任务</td>
          <td>从两个 bundle 还原分支并合并 diff，完成 ARC-AGI 仓库任务</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数学<br><code>mathematics</code></td>
          <td><code>model-extraction-relu-logits</code></td>
          <td>ReLU logits 模型提取</td>
          <td>通过查询一层 ReLU 网络，恢复模型参数或等价表示</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>modernize-scientific-stack</code></td>
          <td>现代化科学计算栈</td>
          <td>将旧的 Python 2.7 气候分析代码迁移到现代 Python</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>mteb-leaderboard</code></td>
          <td>MTEB 榜单处理</td>
          <td>基于 MTEB 榜单为斯堪的纳维亚文本选择最佳嵌入模型</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>mteb-retrieve</code></td>
          <td>MTEB 检索任务</td>
          <td>用指定 embedding 模型检索与查询第五相似的文档</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据处理<br><code>data-processing</code></td>
          <td><code>multi-source-data-merger</code></td>
          <td>多源数据合并</td>
          <td>融合三种格式的用户数据源，并按优先级去重对齐字段</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>nginx-request-logging</code></td>
          <td>Nginx 请求日志配置</td>
          <td>配置 Nginx 监听、静态服务与高级请求日志格式</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>openssl-selfsigned-cert</code></td>
          <td>生成 OpenSSL 自签证书</td>
          <td>用 OpenSSL 生成符合要求的自签 TLS 证书与目录结构</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>调试<br><code>debugging</code></td>
          <td><code>overfull-hbox</code></td>
          <td>修复 Overfull hbox</td>
          <td>修复 LaTeX 文档的 overfull hbox 警告并成功编译</td>
          <td>简单<br><code>easy</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>password-recovery</code></td>
          <td>密码恢复</td>
          <td>在 /app 中做数字取证，找回被误删的 launchcode.txt 密码</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>path-tracing</code></td>
          <td>路径追踪实现</td>
          <td>编写 C 程序生成尽可能接近参考图的渲染图像</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>path-tracing-reverse</code></td>
          <td>逆向路径追踪</td>
          <td>逆向已编译程序，并用 C 复现完全相同的行为</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>polyglot-c-py</code></td>
          <td>C / Python 多语程序</td>
          <td>写一个单文件程序，可同时作为 Python 和 C 执行</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>polyglot-rust-c</code></td>
          <td>Rust / C 多语程序</td>
          <td>写一个单文件程序，可同时作为 Rust 和 C++ 执行</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>优化<br><code>optimization</code></td>
          <td><code>portfolio-optimization</code></td>
          <td>投资组合优化</td>
          <td>结合 C 与 Python 优化投资组合风险收益计算性能</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>protein-assembly</code></td>
          <td>蛋白质组装</td>
          <td>为 DHFR FRET 实验设计满足滤光片与构建约束的蛋白方案</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>prove-plus-comm</code></td>
          <td>证明加法交换律</td>
          <td>补全 Coq 证明，证明自然数加法交换律</td>
          <td>简单<br><code>easy</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>pypi-server</code></td>
          <td>搭建 PyPI 服务</td>
          <td>创建 vectorops 包，并在本地搭建可安装该包的 PyPI 服务</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>模型训练<br><code>model-training</code></td>
          <td><code>pytorch-model-cli</code></td>
          <td>PyTorch 模型命令行接口</td>
          <td>实现 MNIST 模型命令行推理工具，只输出预测数字</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>模型训练<br><code>model-training</code></td>
          <td><code>pytorch-model-recovery</code></td>
          <td>PyTorch 模型恢复</td>
          <td>根据权重和样本重建原始 PyTorch 模型结构</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>qemu-alpine-ssh</code></td>
          <td>QEMU Alpine SSH</td>
          <td>启动 Alpine 镜像并配置 SSH，使 localhost:2222 可登录</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>qemu-startup</code></td>
          <td>QEMU 启动问题</td>
          <td>以可经 telnet 访问登录提示的方式启动 Alpine QEMU</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>query-optimize</code></td>
          <td>查询优化</td>
          <td>优化给定 SQLite 查询，使结果不变但性能更好</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>raman-fitting</code></td>
          <td>拉曼光谱拟合</td>
          <td>拟合拉曼光谱的 G 峰和 2D 峰参数，并写入结果文件</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>regex-chess</code></td>
          <td>正则国际象棋</td>
          <td>写正则替换规则，生成某 FEN 下全部合法下一步局面</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>数据处理<br><code>data-processing</code></td>
          <td><code>regex-log</code></td>
          <td>日志正则提取</td>
          <td>写正则匹配含 IPv4 日志行中的最后一个 YYYY-MM-DD 日期</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>reshard-c4-data</code></td>
          <td>重切分 C4 数据</td>
          <td>编写压缩与验证脚本，按要求重切分并处理数据集</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>rstan-to-pystan</code></td>
          <td>RStan 迁移到 PyStan</td>
          <td>将给定 RStan 脚本改写为 PyStan 3 版本并完成采样</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据科学<br><code>data-science</code></td>
          <td><code>sam-cell-seg</code></td>
          <td>SAM 细胞分割</td>
          <td>用 Meta 的分割模型把矩形/折线掩码统一转换为折线</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>sanitize-git-repo</code></td>
          <td>清洗 Git 仓库敏感信息</td>
          <td>清理 GitHub 仓库中的 API key，并替换为占位值</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>schemelike-metacircular-eval</code></td>
          <td>类 Scheme 元循环求值器</td>
          <td>编写 metacircular evaluator，解释给定类 Scheme 语言</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>数据查询<br><code>data-querying</code></td>
          <td><code>sparql-university</code></td>
          <td>大学数据 SPARQL 查询</td>
          <td>在大学知识图谱上编写 SPARQL 查询回答指定问题</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>调试<br><code>debugging</code></td>
          <td><code>sqlite-db-truncate</code></td>
          <td>截断损坏的 SQLite 数据库恢复</td>
          <td>从二进制截断损坏的 SQLite 数据库中尽量恢复词条</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>系统管理<br><code>system-administration</code></td>
          <td><code>sqlite-with-gcov</code></td>
          <td>带 gcov 的 SQLite 构建</td>
          <td>用 gcov instrumentation 编译 SQLite 并加入 PATH</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>torch-pipeline-parallelism</code></td>
          <td>Torch 流水线并行</td>
          <td>为 LLaMA 训练实现 PyTorch pipeline parallel</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>torch-tensor-parallelism</code></td>
          <td>Torch 张量并行</td>
          <td>为线性层实现 PyTorch tensor parallel</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>模型训练<br><code>model-training</code></td>
          <td><code>train-fasttext</code></td>
          <td>训练 FastText 模型</td>
          <td>训练小于 150MB 且达到精度要求的 fastText Yelp 模型</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>科学计算<br><code>scientific-computing</code></td>
          <td><code>tune-mjcf</code></td>
          <td>调优 MJCF 模型</td>
          <td>调优 MuJoCo MJCF，使模拟更快且状态误差受控</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>视频处理<br><code>video-processing</code></td>
          <td><code>video-processing</code></td>
          <td>视频处理</td>
          <td>编写脚本分析跨栏视频，提取单次跳跃表现指标</td>
          <td>困难<br><code>hard</code></td>
        </tr>
        <tr>
          <td>安全<br><code>security</code></td>
          <td><code>vulnerable-secret</code></td>
          <td>提取脆弱程序中的 secret</td>
          <td>分析可执行程序并提取其中隐藏的 secret</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>winning-avg-corewars</code></td>
          <td>平均胜率更高的 Corewars</td>
          <td>编写 CoreWars 程序，对五个经典对手取得更高平均胜率</td>
          <td>中等<br><code>medium</code></td>
        </tr>
        <tr>
          <td>软件工程<br><code>software-engineering</code></td>
          <td><code>write-compressor</code></td>
          <td>编写压缩器</td>
          <td>为给定解压器生成可正确解开的压缩数据 data.comp</td>
          <td>困难<br><code>hard</code></td>
        </tr>
      </tbody>
    </table>
  </div>
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

  <p>然后再跑自己的 agent。这里要分清两件事：<strong>官方教程里明确给出的 Claude Code 命令，是 Daytona 版</strong>；如果你只是想在本地小并发试跑自己的 agent，可以把并发数调小，但那属于你自己的运行策略，不是官方固定示例。</p>

  <div class="tb-code">
<pre><code># 下面这段是本地小并发试跑思路，不是 Harbor 官方教程原文
export ANTHROPIC_API_KEY=&lt;YOUR-KEY&gt;

harbor run \
  -d terminal-bench/terminal-bench-2 \
  -m anthropic/claude-opus-4-1 \
  -a claude-code \
  --n-concurrent 4
</code></pre>
  </div>

  <p class="tb-note">这里还有一个容易混淆的小点：我在 2026/04/17 核对时，<strong>Harbor 的 “Running Terminal-Bench” 专题教程页</strong>使用的是 <code>terminal-bench/terminal-bench-2</code>；但 Harbor 的其他通用 eval 文档里，仍然还能看到 <code>terminal-bench@2.0</code> 这种 versioned 写法。也就是说，这两种写法都出现在官方文档中，只是当前 Terminal-Bench 专题教程页展示的是 slash 这一版。</p>

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
