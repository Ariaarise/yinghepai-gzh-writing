# 硬核派公众号内容生产系统（yinghepai-gzh-writing）

> 让不同的人 + 不同模型 + 不同素材，稳定地产出**真的像硬核派**的文章。
> **三层解耦**：Content（写什么）≠ Design（长什么样）≠ QA（对不对）。
> **自包含**：文风解剖、事实库、排版组件、校验脚本、真实范本全部打包，零外部依赖。

---

## 🎯 用它，你能产出这样的文章

这是本系统真实产出的文章效果（「阅知未来·硬核AI科普」第三期收官，已发布）：

**首屏（引言卡金句 + 石墨极简排版）：**

![首屏效果](yinghepai-gzh-writing/assets/showcase/01-hero.png)

**正文中部（章节标识 + 下划线强调 + 药丸标签）：**

![正文中部](yinghepai-gzh-writing/assets/showcase/02-middle.png)

**收官结尾（系列升华 + 品牌黄锚点）：**

![收官结尾](yinghepai-gzh-writing/assets/showcase/03-end.png)

> 💡 以上截图来自 `references/example-3rd-session.html`——完整的已排版范本，可直接打开看细节、当模板改。

---

## ⚙️ 它怎么工作（完整 Pipeline）

```
收到素材
  → 素材类型判断（逐字稿优先）
  → 素材不足检测（缺啥问啥，不脑补）
  → 提炼 FACT SHEET 事实库（防幻觉）
  → 编辑判断（这篇值得写什么，允许删50%素材）
  → 写作（按文风解剖写）
  → 事实审查（人名/数字/推断逐项核）
  → 风格审查（禁词/AI味/段落节奏）
  → 排版（按组件选择矩阵）
  → HTML 校验（0 ERROR）
  → 交付（预览页 + 复制到公众号）
```

**对比传统方式：** 普通 skill 是「给 AI 一堆规则让它自由发挥」；这个是**机器可执行的状态机**——每步该做什么、判断什么条件、失败怎么办，都写死了。

---

## 📂 三大层（解耦设计）

| 层 | 职责 | 资源 |
|----|------|------|
| **Content** | 写什么：选题/素材理解/事实提取/结构/写作/标题/金句 | style-anatomy.md + fact-sheet-template.md + 类型模板 |
| **Design** | 长什么样：HTML/组件/品牌色/引言卡/微信兼容 | theme-graphite-minimal.md + common-components.md + 组件选择矩阵 |
| **QA** | 对不对：事实/人名/数字/标题/AI味/HTML/品牌 | evals/evals.md + QA 清单 |

**好处：** 写完文章可以不排版；已有 HTML 只做 QA；改排版不动写作逻辑。

---

## ✨ 能产出什么类型的文章

| 类型 | 标题策略 | 效果 |
|------|---------|------|
| 活动回顾 | 现场感/结果/数字 | 引言卡金句 + 嘉宾详写 + 现场 + 致谢 |
| 工具推荐 | 痛点/结果/场景 | 痛点开头 + 每个工具「适合什么/内容/特征」|
| 人物专访 | 身份/反差/观点 | 金句开场 + 成长线 + 干货 + 快问快答 |
| 赛事公告 | 活动名/动作/时间 | 规则 + 奖项 + 参与方式清晰 |
| 合作宣传 | 品牌+事件+利益 | 致谢合作方 + 引导关注 |

---

## 🚀 怎么用（10 秒上手）

1. 把 `yinghepai-gzh-writing/SKILL.md` 作为规范 prompt 给任何 AI（Claude/GPT/Hermes/Codex）
2. 给 AI 素材（活动纪要/逐字稿/照片说明）
3. AI 按 pipeline 自动执行：读素材 → 建事实库 → 写作 → 审查 → 排版 → 校验 → 交付预览页
4. 点「复制到公众号」→ 粘贴 → 发布

**Hermes 用户：** `cp -r yinghepai-gzh-writing ~/.hermes/skills/content-creation/`

---

## 📁 文件结构（自包含）

```
yinghepai-gzh-writing/
├── SKILL.md                          # 系统总控 + pipeline + 三层规范
├── examples/
│   └── quality-cases.md              # 好坏样例（含真实反例 + 编辑判断）
├── evals/
│   └── evals.md                      # 20个评测case + 6维评分（100分制）
├── references/
│   ├── style-anatomy.md              # ⭐ 文风解剖（❌/✅/Why 对比 + 禁词表）
│   ├── fact-sheet-template.md        # ⭐ FACT SHEET 事实库（防幻觉）
│   ├── theme-graphite-minimal.md     # 石墨极简主题组件库
│   ├── common-components.md          # 通用组件
│   ├── hardcore-brand.md             # 品牌规范
│   ├── activity-review-template.md   # 三期真实范本
│   ├── example-3rd-session.html      # 完整已排版 HTML 范本
│   └── feishu-minutes-scrape.md      # 妙记抓取
├── scripts/
│   ├── validate_gzh_html.py          # HTML 校验（0 ERROR）
│   ├── wrap_preview.py               # 预览页生成
│   └── component_lint.py             # 组件检查
└── assets/
    ├── preview-template.html         # 预览模板
    └── showcase/                     # 效果截图
```

**脚本冒烟测试：** 复制到全新环境，`validate_gzh_html.py` / `wrap_preview.py` / `component_lint.py` / `run_eval.py` 可直接运行（只依赖 Python 标准库，已验证）。Skill 内容质量通过 examples/evals 持续人工验证；自动化评测见 `scripts/run_eval.py`。

---

## 🛡️ 防坑机制（真实反例固化）

- **FACT SHEET 防幻觉**：文章只能从事实库写，禁止脑补；素材不足宁可说不写
- **金句来源等级**：原话 > 编辑提炼 > AI生成；不硬造金句、不冒充原话
- **6 个真实反例**：标题锁数量/官腔/品牌名错/内容单薄/人名错/markdown 符号
- **禁词表 + AI味检测**：赋能/旨在/综上所述/排比三连…见 style-anatomy

---

## 🔄 持续进化

- **20 case 评测集**：改完跑一遍，评分 ≥85 才算过，防改坏
- **更新日志**：SKILL.md 末尾记录每次架构演进（v1.0→v1.1→v1.2→v1.3）
- **反馈飞轮**：使用中发现新坑 → 追加反例 → 越来越准

## 📄 License
MIT
