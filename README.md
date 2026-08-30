# 硬核派公众号写作标准（yinghepai-gzh-writing）

> 让硬核派的任何一位小伙伴写公众号文章，都能达到阿梨同款质量——排版、格式、内容风格完全统一。

## 📦 这是什么

一个 **AI 写作 skill**（标准技能包），定义了硬核派公众号文章从「素材处理」到「交付」的完整规范：

- **素材处理**：必须逐字读妙记/逐字稿、人名确认铁律
- **内容结构**：3 种类型模板（活动回顾/工具推荐/人物采访）
- **文风规范**：自然有温度、朋友口吻、金句提炼、标题 20 字内
- **排版规范**：gzh-design 石墨极简主题 + 品牌黄 + 校验流程
- **交付检查**：12 项自查清单

## 🚀 怎么用

### 方式一：给 AI 用（推荐）
把 `SKILL.md` 内容作为写作规范 prompt 提供给任何 AI（Claude/GPT/Hermes 等），它会按硬核派标准输出文章。

### 方式二：Hermes Agent 用户
复制到你的 skills 目录：
```bash
cp -r yinghepai-gzh-writing ~/.hermes/skills/content-creation/
```

## 📁 文件结构

```
yinghepai-gzh-writing/
├── SKILL.md                          # 主规范（写作方法论）
└── references/
    ├── activity-review-template.md   # 活动回顾文真实范本（第一期图书馆）
    └── feishu-minutes-scrape.md      # 飞书妙记抓取方法
```

## ✍️ 核心规范速览

| 维度 | 规范 |
|------|------|
| 素材 | 逐字读妙记/逐字稿，不看总结 |
| 人名 | 以用户确认名单为准（语音转文字必错）|
| 文风 | 自然有温度、朋友口吻、段落 3-5 句 |
| 标题 | ≤20 字、去专业术语、不夸大 |
| 排版 | gzh-design 石墨极简 + 品牌黄 #FFFB00 ≤3 处 |
| 署名 | 一律不署名 |
| 校验 | gzh-design validate 脚本 0 ERROR |

## 📄 License
MIT
