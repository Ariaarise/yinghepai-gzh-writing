#!/usr/bin/env python3
"""把已校验的公众号正文片段（纯 <section>）包成带「复制」按钮的浏览器预览页。

用户打开预览页 → 点右上角「复制到公众号」→ 按钮选中并复制里面渲染后的富文本
（等价手动 Ctrl+A/Ctrl+C，样式全保留）→ 到公众号编辑器 Ctrl+V 粘贴即可。

按钮和 JS 只存在于预览外壳里，**不在被复制的 section 内**，所以粘进公众号的
仍是干净合规的正文，不含 <script>/<button>。

用法:
    wrap_preview.py <section.html> [output.html]
    wrap_preview.py <section.html> --skip-validation   # 显式跳过前置校验

默认行为:
    生成前先跑 validate_gzh_html.py 校验；有 ERROR 则拒绝生成并提示。
    默认输出 <section去扩展名>_预览.html
"""

import os
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print("用法: wrap_preview.py <section.html> [output.html] [--skip-validation]")
        sys.exit(1)

    args = sys.argv[1:]
    skip_validation = "--skip-validation" in args
    args = [a for a in args if a != "--skip-validation"]

    src = args[0]
    if not os.path.isfile(src):
        print(f"✗ 找不到文件: {src}")
        sys.exit(1)

    # ── 前置校验（默认强制）─────────────────────────────
    if not skip_validation:
        validator = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "validate_gzh_html.py")
        r = subprocess.run([sys.executable, validator, src],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            print("✗ 校验未通过，拒绝生成预览页（这是防呆：未校验的 HTML 直接发布会丢样式）。")
            print("  请先修复以下问题，或确认无误后加 --skip-validation 强制生成：\n")
            print(r.stdout[-2000:])
            sys.exit(1)

    content = open(src, encoding="utf-8").read().strip()
    tpl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "assets", "preview-template.html")
    tpl = open(tpl_path, encoding="utf-8").read()

    title = os.path.splitext(os.path.basename(src))[0]
    out_html = tpl.replace("{{TITLE}}", title).replace("<!--GZH_CONTENT-->", content)

    out = args[1] if len(args) > 1 else os.path.splitext(src)[0] + "_预览.html"
    open(out, "w", encoding="utf-8").write(out_html)
    print(f"✓ 校验通过，已生成带「复制」按钮的预览页: {out}")
    print("  用浏览器打开它，点右上角「复制到公众号」，再去公众号编辑器 Ctrl/⌘+V 粘贴。")


if __name__ == "__main__":
    main()
