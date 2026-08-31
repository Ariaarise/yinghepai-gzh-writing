---
name: gzh-save
description: "公众号沉淀 — 保存微信公众号文章到 Obsidian me/05-People 作者文件夹。读取→识别作者→一字不改复制原文→打标签+双链→自查验证→存入。"
version: 2.0.0
author: Hermes Agent
---

# 公众号沉淀

保存微信公众号文章到 Obsidian vault 的 `me/05-People/[作者名]/` 下。

## 🔴 铁律（违反不可原谅）

**原文必须一字不改地复制。绝对不允许：**
- ❌ 删改任何字词
- ❌ 提取、概括、总结、改写
- ❌ 重新组织段落顺序或结构
- ❌ 加入自己的分析、评论或解读

**允许：**
- ✅ 压缩多余空行（连续3行以上空白→1行空白），使文件可读
- ✅ 保留原文加粗/斜体等格式
- ✅ **重点句加粗**（`**重点**`）——用户明确要求「有些好多重点的可以加粗」，选 2-5 处核心金句/观点加粗，不要太多

**⚠️ 段落结构铁律（用户多次纠正）：**
- ✅ **必须保留原文的自然段结构**——段落之间用空行分隔
- ❌ **绝对禁止给段落加编号**（`1. ` `2. ` 序号）——用户原话「我不理解文章排版怎么会有序号啊啊啊啊啊啊，不是自然段吗。和原文一致啊」
- 公众号原文是一个自然段 → 沉淀后也是一个自然段；原文有 N 个自然段 → 沉淀后 N 个自然段
- 原文段落结构在抓取时可能丢失（html2text 把 `<p>` 变成连续文本）→ **必须按语义/原文断点重新分段**，段间空行，**无编号**

**写入前必须逐字对比验证，确认每个字符完全一致。**

## 用户称呼

用户叫这个 skill **「公众号沉淀」**。当她说「公众号沉淀」时，执行本 skill。

## 触发条件

用户发来 `mp.weixin.qq.com` 链接并说「存一下」「放到 Obsidian」「收录」「公众号沉淀」等。

## 可选输出格式

用户可能要求两种输出之一：

1. **默认：存入 Obsidian**（`me/05-People/[作者名]/`）— 执行完整流程
2. **Word 文档**：用户要求「发我Word」「弄成Word发给我」等

### Word 文档转换步骤

当用户要 Word 版时，在完成 Step 4（提取原文）后，改为执行以下流程：

```python
from docx import Document
from docx.shared import Pt
import re

doc = Document()
style = doc.styles['Normal']
font = style.font
font.name = '等线'
font.size = Pt(11)

# 标题
title_p = doc.add_paragraph()
title_run = title_p.add_run('文章原标题')
title_run.bold = True
title_run.font.size = Pt(16)
doc.add_paragraph()

# 正文 — 保持原文分段结构
sections = body_text.strip().split('\n\n\n')
for section in sections:
    lines = section.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^\d+\s', line):
            p = doc.add_paragraph()
            r = p.add_run(line)
            r.bold = True
            r.font.size = Pt(13)
        else:
            doc.add_paragraph(line)
    doc.add_paragraph()

output_path = '/tmp/文章标题.docx'
doc.save(output_path)
```

通过 `MEDIA:/tmp/文章标题.docx` 发送给用户。

## 工作流程

### Step 1：检查 Mac SSH 连接

```bash
bash ~/.hermes/scripts/check-mac-ssh.sh
```
返回 `MAC_DOWN` 时**不阻塞**：先把文章提取、验证、生成文件（Step 2-8 都可以做，不依赖 Mac），
告知用户「文件已备好，Mac 上线后写入」。用户回复「重连/修复/Mac 上线了」后再执行 Step 9 写入。
Mac 经常休眠离线（Tailscale 显示 active 但 SSH 超时），唤醒后重试即可。

> Mac 离线且需要**找回已沉淀文章的原文**（如「公众号阅读-晚间回顾」cron 推荐旧文时）→ 用 `gzh-daily-review` skill 的 `references/mac-offline-recovery.md`（state.db 直查抓取记录、旧 cron 输出里的完整书库清单、zarazhang.com 英文原版、playwright 过 JS challenge）。

### Step 2：读取文章 + 识别作者

```bash
curl -sL "<url>" -H "User-Agent: Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
```

提取：
- `文章标题` — `<meta property="og:title">` 或 `<title>` 标签
- `文章正文` — `id="js_content"` div
- `公众号名称（作者）` — 按以下优先级查找：
  1. 源码中 `var author = "..."`（**作者字段，最权威**）
  2. 源码中 `var nickname = "..."`（公众号名）
  3. 源码中 `nickname : "..."`
  4. 正文首行「本文来自微信公众号：XXX」中的 XXX
  5. 正文末尾署名 / 专栏名（如文末出现「数字作家专栏」→ YinoCho；「观点 / 刘润 主笔」→ 刘润）
  6. 如果以上都找不到，从文章内容推断（如首段提及的作者名）

**⚠️ 作者识别铁律（用户明确纠正过）：**
- **绝不凭文风猜测作者**——本会话曾把 YinoCho 的文章（《处于上升期的人要避免被观测》，文末「数字作家专栏」）误归给请辩，用户指出必须爬取源码确认
- **先查 `var author` 字段**（html 源码里 `var author = "..."`），再查 `var nickname`、正文署名/专栏名
- **新作者≠已有作者**：用户发来的链接作者可能是 Obsidian 里没有的新人，识别到新名字就建新文件夹，不要塞进已有作者（如请辩）文件夹
- 拿不准时，把文章开头/结尾署名片段给用户确认，再写入

### Step 2b：沉淀后弹出 Obsidian 给用户看

**每次成功写入后必须执行**（用户明确要求：存完要弹出 Obsidian 界面让她看到）：

```bash
ssh empower@100.95.151.32 "open -a Obsidian 'obsidian://open?vault=obsidian本地仓库【不可删除】&file=me%2F05-People%2F作者名%2F文章标题'"
```

- 用 `open -a Obsidian` 在 Mac 上唤起 Obsidian 并定位到刚存的笔记
- 若 `open -a Obsidian` 失败，退化为 `open -a Obsidian`（唤起应用即可）
- 然后告诉用户「已存入 X 文件夹，Obsidian 已弹出，可以看看内容」

### Step 3：确定路径

映射到 `me/05-People/` 下已有文件夹。不在列表中则新建。

**作者映射表见 `references/author-mappings.md`，新增作者时先查该文件。**

**❗ 文件夹命名必须匹配已有命名规范（大小写、顺序均需一致）：**

| 公众号/作者 | 文件夹 | 常见错误（勿用） |
|------------|--------|----------------|
| 请辩 / 蔡垒磊 | `me/05-People/请辩` | 几乎每周更新 |
| Yino / YinoCho / Yino漫游宇宙 | `me/05-People/Yino宇宙漫游 1` | ❌ 勿写成 `yino漫游宇宙`；⚠️ 实际文件夹带数字后缀「 1」；**作者字段是 `YinoCho`**，文末常带「数字作家专栏」推广 |
| 刘润 | `me/05-People/刘润` | 转载文格式「观点 / 刘润 主笔」 |
| 不懂经 | `me/05-People/不懂经` | 作者：不懂经也叔的Rust |
| 猫和她的她 | `me/05-People/猫和她的她` | — |
| Preston | `me/05-People/Preston` | — |
| 老王 | `me/05-People/老王` | — |
| Ali Abdaal | `me/05-People/Ali Abdaal` | — |
| DAN KOE | `me/05-People/DAN KOE` | — |
| Zara Zhang | `me/05-People/Zara Zhang` | — |

- 先检查 `me/05-People/` 下是否已有该作者文件夹，有则直接用
- 若无则新建
- **绝对不在 `me/05-People` 之外新建作者文件夹**
- **例外：用户明确指定了目标文件夹时（如「放在 10-Health/the knowledge of sports」），直接按用户指定路径存放**，不套用 05-People 规则。此时文件名仍为纯标题、仍带 frontmatter 和正文可点击链接，只是路径不同。

### Step 4：提取原文（⚠️ 最关键一步）

**使用 html2text 库提取，禁止手动解析 HTML。**

```python
import re
import html2text
h = html2text.HTML2Text()
h.body_width = 0          # 不自动换行
h.ignore_links = True     # 去掉链接标记
h.ignore_images = True
h.ignore_emphasis = False  # 保留加粗/斜体等格式
h.ignore_tables = True
h.unicode_snob = True

text = h.handle(raw_html)

# 截掉无关内容
for marker in ['相关推荐', '阅读原文', '喜欢此内容的人还喜欢']:
    i = text.find(marker)
    if i > 50: text = text[:i]; break

text = text.strip()

# 压缩多余空行（保留段落分隔，去掉连续3行以上的空白）
text = re.sub(r'\n[ \t]*\n[ \t]*\n+', '\n\n', text)
```

### Step 5：逐字对比验证（⚡ 必须执行）

```python
# 1. 用完全相同的方法重新抓取+提取一次
# 2. 与待写入文本逐字符对比
# 3. 完全一致（含空行、空格位置）才通过
# 4. 不通过则修正，重新验证
```

**验证不通过绝对不允许写入。**

### Step 6：生成 Markdown 文件

```markdown
---
date: 2026-07-23 08:41
tags: [标签1, 标签2, 标签3]
source: 公众号名称
---

> 链接：[文章标题](https://mp.weixin.qq.com/s/xxx)

**相关笔记：** [[其他文章标题]] · [[另一篇相关文章]]

---

原文正文，一字不改，保留原标题的层级结构（大标题、小标题、正文段落均保留）
```

**文件名：** `文章标题.md`（不带日期）

### Step 7：打标签

根据内容选 2-4 个：`#认知` `#赚钱` `#AI` `#投资` `#成长` `#阅读` `#写作` `#心理` `#社会` `#效率` `#生活`

### Step 8：打双链

关联同作者其他文章或相关主题，用 `[[wikilinks]]` 格式。

### Step 9：写入 Mac

```bash
base64 <local_file> | ssh empower@100.95.151.32 "base64 -d > '${OBSIDIAN_PATH}/me/05-People/作者名/文件名.md'"
```

确认 `wc -c` > 0。

### Step 10：最终自查清单

- [ ] 原文每个字都保留，没有任何改动
- [ ] **自然段结构保留，绝无编号**（检查：没有 `^数字. ` 开头的段落）
- [ ] **重点句已加粗 2-5 处**（核心金句/观点）
- [ ] 逐字对比验证通过
- [ ] 文件名为纯标题，不带日期
- [ ] frontmatter 有 date 字段
- [ ] source_url 在正文中，是 `[标题](url)` 格式
- [ ] 标签 2-4 个
- [ ] 双链 1-3 个
- [ ] 文件在 `me/05-People/` 内
- [ ] SSH 连接正常
- [ ] 写入成功（文件大小 > 0）
- [ ] **已执行 Step 2b 弹出 Obsidian**（`open -a Obsidian` 定位到刚存笔记）
