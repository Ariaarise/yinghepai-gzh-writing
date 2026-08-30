# Design 层加载索引（按需加载，不要一次性读全部）

> ⚠️ 核心原则：**用哪个组件，读哪个文件**。禁止把 theme-graphite-minimal.md（700+行）
> 和 common-components.md 一次性全读进上下文。按下面索引按需取用。

## 加载规则

| 我需要… | 读这个文件 | 取什么 |
|---------|-----------|--------|
| 文章整体骨架/章节结构 | `theme-graphite-minimal.md` 的「章节标题」部分 | 01/02/03 编号标题样式 |
| 引言卡（金句）| `theme-graphite-minimal.md` 的「引言卡」部分 | QUOTE 卡 + 品牌黄下划线 |
| 普通正文段落 | `common-components.md` 的「正文」部分 | span leaf 段落 + 石墨下划线 |
| 强调/金句锚点 | `common-components.md` 的「Highlight」部分 | 品牌黄 #FFFB00 锚点 |
| 数据/数字呈现 | `common-components.md` 的「数据卡」部分 | Data Card 组件 |
| 嘉宾/人物介绍 | `common-components.md` 的「药丸标签/Profile」部分 | Pill / Profile |
| 时间线/流程 | `common-components.md` 的「Timeline」部分 | Timeline 组件 |
| 收尾 END 线 | `common-components.md` 的「END」部分 | END 线 + 署名区（不署名）|
| 品牌色/VI | `hardcore-brand.md` | 品牌黄/石墨灰/署名规则 |

## 上下文预算（防膨胀）

- 一次写作任务，Design 层最多读 **2 个文件的相关片段**（不是全文）
- theme-graphite-minimal.md：**只读需要的章节**，不读全文
- 完整范本 example-3rd-session.html：**当「对答案」用**——写某个部分前，先看范本对应部分怎么写，不全文读

## 示例：写「引言卡」时

```
只做这一步：
1. 打开 common-components.md 或 theme-graphite-minimal.md 的「引言卡」章节
2. 取引言卡 HTML 骨架
3. 替换成自己的金句
4. 校验

不要做：
❌ 把 theme 700 行 + common 346 行 + example 1361 行全读一遍
```

## 组件比例（防堆组件）

- 普通段落：~70%
- 强调组件（下划线/药丸）：~20%
- 特殊组件（引言卡/数据卡/timeline）：~10%
- **不要为了「好看」把所有组件用一遍**
