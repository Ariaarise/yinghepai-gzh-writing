#!/usr/bin/env python3
"""微信公众号 HTML 合规校验器。

把 SKILL.md 里"必须遵守的平台限制"从模型自觉变成确定性兜底。
排版生成后必跑：检查禁用标签/属性/样式，并核查文字节点是否用
<span leaf=""> 包裹（公众号编辑器粘贴后保持样式的关键）。

用法:
    validate_gzh_html.py <file.html>
    validate_gzh_html.py --stdin < file.html

退出码: 1 = 有 ERROR（会被公众号过滤或粘贴后样式丢失）; 0 = 通过。
"""

import argparse
import re
import sys
from html.parser import HTMLParser

# (正则, 级别, 说明) —— ERROR 会被公众号编辑器过滤掉或导致样式失效
FORBIDDEN = [
    (re.compile(r"<style[\s>]", re.I), "ERROR", "<style> 标签会被过滤，样式必须内联"),
    (re.compile(r"<script[\s>]", re.I), "ERROR", "<script> 标签会被过滤"),
    (re.compile(r"</?div[\s>]", re.I), "ERROR", "<div> 会被改写，请用 <section>"),
    (re.compile(r"<link[\s>]", re.I), "ERROR", "外部 <link>（CSS/字体）会被过滤"),
    (re.compile(r"\sclass\s*=", re.I), "ERROR", "class 属性会被剥离，请用内联 style"),
    (re.compile(r"\sid\s*=", re.I), "ERROR", "id 属性会被剥离"),
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "ERROR",
     "position fixed/absolute/sticky 不被支持"),
    (re.compile(r"float\s*:", re.I), "ERROR", "float 不被支持"),
    (re.compile(r"@media", re.I), "ERROR", "@media 媒体查询不被支持"),
    (re.compile(r"@keyframes", re.I), "ERROR", "@keyframes 动画不被支持"),
    (re.compile(r"@import", re.I), "ERROR", "@import 不被支持"),
    (re.compile(r"display\s*:\s*grid", re.I), "ERROR", "display:grid 不被支持，请用 flex"),
    (re.compile(r"var\s*\(\s*--", re.I), "ERROR", "CSS 变量 var(--x) 不被支持，请写死值"),
    (re.compile(r"url\s*\(\s*['\"]?https?://[^)]*\.(woff2?|ttf|otf|eot)", re.I),
     "ERROR", "外部字体不被支持"),
]

CJK = re.compile(r"[一-鿿㐀-䶿]")
SKIP_TAGS = {"head", "title", "style", "script"}  # 不参与公众号正文粘贴的区域
# 中文字后紧跟半角逗号/分号/叹号/问号（应改全角）；只查"中文在前"避免中英混排误伤
HALF_PUNCT = re.compile(r"[一-鿿㐀-䶿][,;!?]")
ASCII_QUOTE = re.compile(r"[\"']")
# 代码区特征：等宽字体或 white-space:pre —— 其内半角符号是正常的
CODE_STYLE = re.compile(r"monospace|white-space\s*:\s*pre|courier|consolas|sf mono", re.I)


class LeafChecker(HTMLParser):
    """检查每个非空文本节点是否处于 <span leaf> 内。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []           # [(tag, is_leaf, is_code)]
        self.leaf_depth = 0       # 处于 span[leaf] 内的嵌套计数
        self.code_depth = 0       # 处于代码区（等宽/pre）内的嵌套计数
        self.span_leaf_count = 0  # 全文 span leaf 总数
        self.unwrapped = []       # (文本片段, 父标签) —— 未被 leaf 包裹的中文文本
        self.half_punct = []      # 正文里疑似半角标点的片段

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        is_leaf = tag == "span" and "leaf" in ad
        is_code = bool(CODE_STYLE.search(ad.get("style", "") or ""))
        if is_leaf:
            self.span_leaf_count += 1
            self.leaf_depth += 1
        if is_code:
            self.code_depth += 1
        self.stack.append((tag, is_leaf, is_code))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _, was_leaf, was_code in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                    if was_code:
                        self.code_depth -= 1
                del self.stack[i:]
                break

    def handle_data(self, data):
        text = data.strip()
        if not text or not CJK.search(text):
            return
        if any(t in SKIP_TAGS for t, _, _ in self.stack):
            return  # <head>/<title>/<style>/<script> 内文字不进公众号正文
        if self.leaf_depth == 0:
            parent = self.stack[-1][0] if self.stack else "(root)"
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.unwrapped.append((snippet, parent))
        if self.code_depth == 0 and (HALF_PUNCT.search(text)
                                     or ASCII_QUOTE.search(text)):
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.half_punct.append(snippet)


def validate(html, name="<input>"):
    """返回 (categories, span_leaf_count)：
    categories = {
        "platform": [(level, msg), ...],   # 平台兼容（script/div/class/grid…）
        "style":    [(level, msg), ...],   # 样式保真（span leaf 未包裹）
        "typography": [(level, msg), ...], # 排版规范（半角标点/英文引号）
        "brand":    [(level, msg), ...],   # 品牌规则（预留：品牌黄数量等）
    }
    """
    categories = {"platform": [], "style": [], "typography": [], "brand": []}

    # ── Platform Compatibility（平台兼容性）────────────────
    for rx, level, msg in FORBIDDEN:
        hits = len(rx.findall(html))
        if hits:
            categories["platform"].append(
                (level, f"{msg}（命中 {hits} 处）"))

    # ── Style Preservation（样式保真）──────────────────────
    checker = LeafChecker()
    try:
        checker.feed(html)
    except Exception as e:  # 容错：解析失败不致命，只提示
        categories["typography"].append(("WARNING", f"HTML 解析中断: {e}"))

    has_cjk = bool(CJK.search(html))
    if has_cjk and checker.span_leaf_count == 0:
        categories["style"].append(
            ("ERROR", "全文没有任何 <span leaf=\"\"> 包裹——"
                      "粘贴到公众号后样式会大面积丢失"))
    elif checker.unwrapped:
        # 硬规则：正文中文未包裹 = ERROR（span leaf 是样式保真的关键，
        # 未包裹文本粘贴后样式必然丢失，属于「会坏」而非「可能坏」）
        sample = "；".join(f"「{s}」(在 <{p}> 内)"
                           for s, p in checker.unwrapped[:5])
        categories["style"].append(
            ("ERROR", f"{len(checker.unwrapped)} 处正文中文文本未被 "
                      f"<span leaf> 包裹，粘贴后样式会丢失，必须全部包裹。例：{sample}"))

    # ── Typography（排版规范）──────────────────────────────
    if checker.half_punct:
        sample = "；".join(f"「{s}」" for s in checker.half_punct[:5])
        categories["typography"].append(
            ("WARNING", f"{len(checker.half_punct)} 处正文疑似半角标点/英文引号，"
                        f"应改中文全角（代码块内不计）。例：{sample}"))

    # ── Brand（品牌规则）───────────────────────────────────
    # 预留：品牌黄 #FFFB00 数量检查（≤3 处）
    brand_yellow = len(re.findall(r"#FFFB00", html, re.I))
    if brand_yellow > 3:
        categories["brand"].append(
            ("WARNING", f"品牌黄 #FFFB00 出现 {brand_yellow} 处（规范 ≤3 处）"))

    return categories, checker.span_leaf_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="HTML 文件路径")
    ap.add_argument("--stdin", action="store_true", help="从标准输入读取")
    args = ap.parse_args()

    if args.stdin or not args.file:
        html = sys.stdin.read()
        name = "<stdin>"
    else:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            html = f.read()
        name = args.file

    categories, leaf_n = validate(html, name)

    print(f"📋 公众号 HTML 合规校验: {name}")
    print(f"   span leaf 包裹: {leaf_n} 处")

    # 分类输出：Platform / Style / Typography / Brand
    labels = {
        "platform": "Platform Compatibility（平台兼容）",
        "style": "Style Preservation（样式保真）",
        "typography": "Typography（排版规范）",
        "brand": "Brand Rules（品牌规则）",
    }
    all_errors = []
    has_output = False
    for cat in ["platform", "style", "typography", "brand"]:
        items = categories[cat]
        if not items:
            continue
        has_output = True
        print(f"\n{'❌' if any(lv == 'ERROR' for lv, _ in items) else '⚠️'} {labels[cat]} ×{len(items)}:")
        for lv, msg in items:
            mark = "🔴" if lv == "ERROR" else "🟡"
            print(f"   {mark} [{lv}] {msg}")
            if lv == "ERROR":
                all_errors.append(msg)

    if not all_errors:
        if has_output:
            print("\n✅ 无致命问题，可粘贴（WARNING 请人工确认）")
        else:
            print("\n✅ 完全合规，可直接粘贴到公众号编辑器")

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
