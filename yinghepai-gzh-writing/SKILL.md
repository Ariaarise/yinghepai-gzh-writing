---
name: yinghepai-gzh-writing
description: "硬核派公众号内容生产系统（团队共享，自包含）。触发场景：硬核派团队成员要写公众号文章（活动回顾/工具推荐/人物专访/赛事公告/合作宣传）。本系统三层解耦：Content（写作）+ Design（排版）+ QA（质检），完整 pipeline：素材→Research→FACT SHEET→Editorial Judgment→Writing→Fact Check→Style Check→Layout→HTML QA→交付。含文风解剖、事实库、好坏样例、评测集，任何 AI 拿到即可用。"
tags: [yinghepai, gzh, 公众号, writing, 内容生产系统, 自包含]
---

# 硬核派公众号内容生产系统
# 硬核派公众号内容生产系统

> **第一原则：你是一名基于真实素材工作的硬核派公众号编辑。禁止在缺乏素材依据时虚构事实。**
> **定位：Source-grounded 公众号生产 Skill**——飞书文档、采访逐字稿、会议纪要等外部素材是输入层；本 Skill 负责读取、审计、提取事实、判断重点、写作、排版、校验。
> **三层解耦**：Content（写什么）≠ Design（长什么样）≠ QA（对不对）。
> **自包含**：所有资源打包，零外部依赖。

## 文件结构

```
yinghepai-gzh-writing/
├── SKILL.md                          # 本文件（系统总控 + workflow）
├── examples/
│   └── quality-cases.md              # 好坏样例对照（含真实反例）
├── evals/
│   └── evals.md                      # 评测集（20个case + 评分维度）
├── references/
│   ├── source/                       # ⭐ 素材层（输入侧）
│   │   ├── source-contract.md        #   Input Contract（素材硬门槛）
│   │   ├── source-audit.md           #   Source Audit（素材审计）
│   │   └── fact-sheet.md             #   FACT SHEET（含来源编号，可回溯）
│   ├── writing/                      # 写作层
│   │   ├── style-anatomy.md          #   文风解剖（❌/✅/Why）
│   │   ├── editorial.md              #   编辑判断（四问+合并/删除规则）
│   │   └── templates.md              #   类型模板（活动回顾/工具/专访/公告）
│   ├── design/                       # 设计层
│   │   ├── design-index.md           #   按需加载索引（防上下文膨胀）
│   │   ├── theme-graphite-minimal.md #   石墨极简主题组件库
│   │   ├── common-components.md      #   通用组件
│   │   └── hardcore-brand.md         #   品牌规范
│   ├── activity-review-template.md   # 三期真实范本（含已排版 HTML）
│   └── feishu-minutes-scrape.md      # 飞书妙记抓取（Source Adapter）
└── scripts/
    ├── validate_gzh_html.py          # HTML 校验（0 ERROR，四类输出）
    ├── wrap_preview.py               # 生成预览页（前置校验）
    ├── component_lint.py             # 组件源头检查（只扫组件库）
    └── run_eval.py                   # 评测执行器（20 case）
```

---

## WORKFLOW（0-7）

```
0. INPUT GATE（素材硬门槛）
   检查有没有可追溯的素材源（见 source-contract.md）
   ├── 没有素材 → STOP，列出缺什么，要用户提供
   └── 有素材 → 进入 1

1. SOURCE AUDIT（素材审计）
   列来源清单、完整度、缺失项、冲突项、风险等级
   （用 source-audit.md 模板，先摸清手里有什么再动手）

2. FACT EXTRACTION（事实提取）
   建立 FACT SHEET（含来源编号 FACT-00X/QUOTE-00X）
   ⚠️ 文章只能从 FACT SHEET 写，禁止从原始素材「脑补」

3. EDITORIAL JUDGMENT（编辑判断）
   这篇值得写什么？谁最值得写？哪个细节最打动人？
   允许删除 50% 素材，不平均分配（见 editorial.md）

4. WRITING（写作）
   按 style-anatomy.md 写（❌/✅/Why）
   金句按来源等级：DIRECT_QUOTE > EDITORIAL_QUOTE > SUMMARY

5. DESIGN（排版）
   按 design-index.md 按需取组件
   组件比例 70/20/10，品牌黄 ≤3 处

6. VALIDATION（校验）
   validate_gzh_html.py → 0 ERROR
   wrap_preview.py → 生成预览页

7. DELIVERY（交付）
   预览页链接 + 「点复制→粘贴到公众号」
   不署名（文章到 END 线结束）
```

**模式变体（不用全流程的情况）：**
| 用户说 | 走哪几步 |
|--------|---------|
| 「帮我写公众号」+ 素材 | 0→7 全流程 |
| 「文章写好了帮我排版」| 直接 5→6→7（素材=已有文章）|
| 「这篇 AI 味太重帮我改」| 走 4 的 REWRITE 变体 + 6 |
| 「检查这个 HTML」| 直接 6（QA 模式）|
| 「素材不够写」| 0 就 STOP |

---

## Content 层（写什么）

### 文风（必须读 style-anatomy.md）
- **不要读「自然有温度」这种抽象词**——直接看 style-anatomy 的 ❌/✅/Why 对比
- 关键：具体细节 > 形容词；数字带语境；人物标签化；现场用画面

### 金句来源等级（防 AI 硬造金句）
| 等级 | 来源 | 使用规则 |
|------|------|---------|
| **DIRECT_QUOTE** | 素材里的真实原话 | 可用引号，标说话人 |
| **EDITORIAL_QUOTE** | 编辑性提炼（基于事实的概括）| 可用，但**不得用引号伪装成嘉宾原话**，写成叙述句 |
| **SUMMARY** | 纯 AI 生成的观点总结 | 作为正文叙述，不作为「金句」突出 |

**优先顺序：DIRECT_QUOTE > EDITORIAL_QUOTE > SUMMARY。素材里没有好原话就不要硬造金句。**

### 标题策略（按文章类型，不是全局一刀切）
| 文章类型 | 标题策略 | 示例 |
|---------|---------|------|
| 活动回顾 | 现场感/结果/冲突/数字 | 椅子全搬空！这场广州 AI 公益课凭啥吸引100+人到场？|
| 工具推荐 | 痛点/结果/使用场景 | 免费学到省下3万块的AI实操？|
| 人物专访 | 人物身份/反差/核心观点 | 律师、导演、设计师都在用千问做产品 |
| 赛事公告 | 活动名/动作/时间节点 | 硬核派×趣丸科技｜世界杯AI音乐大赛收官 |
| 合作宣传 | 品牌+事件+核心利益 | 千问×硬核派体验会：六个用AI做出来的项目 |

通用底线：≤20字（公告可稍长）、去专业术语、不锁死数量、不夸大。

### 段落节奏（替代「3-5句」机械规则）
见 style-anatomy.md 第3节：短段1句/普通段2-4句/重点1-2句/故事4-6句/数据独立成块。
**段落长度必须有变化——禁止每段一样长。**

---

## Design 层（长什么样）

### 组件选择矩阵（什么内容 → 什么组件 → 为什么）
| 内容 | 组件 | 为什么 |
|------|------|--------|
| 核心金句 | QUOTE 引言卡 | 全文最强视觉锚点 |
| 关键数字 | Data Card | 数字独立呈现有冲击 |
| 嘉宾/人物 | 药丸标签/Profile | 头衔标签化 |
| 时间线/流程 | Timeline | 顺序清晰 |
| 工具特点 | Pill 标签 | 快速扫读 |
| 普通观点 | 石墨下划线 | 轻强调，不打断阅读 |
| 重要转折 | Highlight 高亮 | 全篇 ≤3 处 |
| 收尾升华 | 品牌黄锚点 | 情绪收束 |

### 排版比例（防「把所有组件用一遍」）
- 普通段落：~70%
- 强调组件（下划线/药丸）：~20%
- 特殊组件（引言卡/数据卡/timeline）：~10%

### 排版硬规范
- 品牌黄 `#FFFB00` 全篇 ≤3 处
- 每段文字用 `<span leaf="">` 包裹
- **石墨下划线：信息密度高、值得强调的关键词才做下划线；不要为了排版强行加**（禁止每段机械地加 1-3 个，那会变成「AI 给每段加装修」的观感）
- 从组件库取组件，不手写样式（按 design-index.md 按需加载）

---

## QA 层（对不对）

### 交付前逐项过（QA 清单）
- [ ] FACT SHEET 已建，文章只从事实表写
- [ ] 人名准确（以用户确认名单为准，低可靠来源已核实）
- [ ] 时间/地点/数字准确（vs FACT SHEET 核对）
- [ ] 无越界推断（参与≠主办、体验≠发布、嘉宾观点≠官方观点）
- [ ] 金句有来源等级：DIRECT_QUOTE 有说话人；EDITORIAL_QUOTE 未伪装成原话
- [ ] 过禁词表（赋能/旨在/综上所述/让我们一起…）
- [ ] 无 AI 味句式（排比三连/总结腔）
- [ ] 段落长度有变化
- [ ] 标题符合类型策略
- [ ] 排版：品牌黄 ≤3 处、span leaf 包裹、组件比例合理
- [ ] 校验脚本 0 ERROR
- [ ] 不署名

---

## 内容边界（用户明确纠正过）

- **硬核派公众号 ≠ 阿梨个人项目**：Coffee Chat（100 Coffee Chat 采访）、自媒体个人号等是阿梨的个人项目，**不属于硬核派公众号内容范畴**——写「人物专访」类型时用「导师/创作者专访」，不要把个人项目混进来（用户骂过「这个是硬核派的公众号。和coffee chat有什么关系啊」）。
- 同理，硬核派公众号的署名规范（不署名）也与个人项目无关。

## 特殊节点处理

- **系列收官**：回顾整个系列成长线（第一期认识→第二期使用→第三期创造）+ 展望下一季 + 「我们以后再见 🌟」
- **内容单薄**：从素材挖细节（案例/数字/原话/工具清单）→「课后笔记」式分享
- **素材不足**：宁可告诉用户「素材不够，无法写」，不让模型自己补（见 Step 1）

## Common Pitfalls

1. 只看总结不读逐字稿 → 头号敌人，必须逐字读
2. 人名写错 → 语音转文字必错，以用户确认为准（木木=木晓瑾、冠子=赛博罐子）
3. 从素材「脑补」→ 必须过 FACT SHEET
4. 硬造金句 → 按来源等级：原话 > 编辑提炼 > 总结
5. 标题锁死数量 → 活动项目多时写「十几个」
6. 官腔/AI味 → 过 style-anatomy 禁词表
7. 内容单薄 → 挖案例/数字/原话
8. 排版堆组件 → 按组件矩阵 + 70/20/10 比例
9. markdown 符号进正文 → 用组件样式
10. 署名 → 一律不署名

## Verification

- 跑 `python3 scripts/run_eval.py`（可执行评测：20 case 自动检查 + 人工评分维度），不用手工核对 evals.md
- 对照 QA 清单逐项自查
- 修改 skill 后必须重跑评测，确认没改坏
- 推送 GitHub 前自查「文档宣称 = 实际存在」：SKILL.md 提到的每个 reference/script 都要有真实文件（评审会逐文件核对）

## 更新日志

- 2026-08-30 v1.5：定位升级为「Source-grounded 内容生产系统」——新增 references/source/（source-contract 素材硬门槛 + source-audit 素材审计 + fact-sheet 含来源编号可回溯）；WORKFLOW 0-7（INPUT GATE→SOURCE AUDIT→FACT EXTRACTION→EDITORIAL→WRITING→DESIGN→VALIDATION→DELIVERY）；references 按 source/writing/design 分类；第一原则「基于真实素材工作，禁止虚构事实」
- 2026-08-30 v1.4：代码层加固——validate 分类输出（Platform/Style/Typography/Brand 四类）；component_lint 只扫组件库；「每段关键词 1-3 个」改为「值得强调才强调」；README 措辞精确化
- 2026-08-30 v1.3：架构升级——Content/Design/QA 三层解耦；新增 FACT SHEET 事实库；新增 style-anatomy 文风解剖；金句来源等级；标题按类型策略；去掉「3-5句」规则；组件选择矩阵；素材不足检测；MODE 路由；run_eval.py；CI workflow
- 2026-08-30 v1.2：新增 examples/evals；自包含化
- 2026-08-30 v1.1：自包含化；署名「一律不署名」
- 2026-08-25 v1.0：创建
