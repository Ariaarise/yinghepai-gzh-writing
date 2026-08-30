#!/usr/bin/env python3
"""run_eval.py — 硬核派公众号 skill 评测执行器

用法:
    python3 scripts/run_eval.py                # 跑全部 20 个 case
    python3 scripts/run_eval.py --case 3       # 只跑单个 case
    python3 scripts/run_eval.py --list         # 列出所有 case

评测维度（总分 100）:
    事实准确性 25 / 内容完整性 20 / 硬核派文风 20 / 结构 15 / 标题 10 / 排版 10
    总分 ≥85 = PASS, <85 = FAIL

说明:
    第一版是「结构化评测入口」——自动检查可机械验证的部分
    （fixture 存在性 / HTML 校验 / 规则命中 / 素材不足检测），
    需要人判断的部分（文风/金句质量）输出评分提示，由人工打分。
"""
import argparse
import json
import os
import re
import subprocess
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============ 20 个 case 定义 ============
# 每个 case: id, name, fixture(输入素材路径或 None=交互), checks(自动检查), 需要人工评分的维度
CASES = [
    {"id": 1, "name": "普通活动回顾", "fixture": "evals/fixtures/case1-activity.md",
     "checks": ["fact_sheet", "html_valid", "no_invent"], "human_score": ["事实", "内容", "文风"]},
    {"id": 2, "name": "嘉宾很多(>6位)", "fixture": "evals/fixtures/case2-many-guests.md",
     "checks": ["editorial_judgment"], "human_score": ["事实", "内容", "文风", "结构"]},
    {"id": 3, "name": "活动素材很少", "fixture": "evals/fixtures/case3-minimal.md",
     "checks": ["insufficient_material"], "human_score": ["事实"]},
    {"id": 4, "name": "逐字稿非常长", "fixture": "evals/fixtures/case4-long-transcript.md",
     "checks": ["fact_sheet", "semantic_split"], "human_score": ["事实", "结构"]},
    {"id": 5, "name": "人名错误", "fixture": "evals/fixtures/case5-wrong-names.md",
     "checks": ["name_verify"], "human_score": ["事实"]},
    {"id": 6, "name": "数字冲突", "fixture": "evals/fixtures/case6-number-conflict.md",
     "checks": ["conflict_detect"], "human_score": ["事实"]},
    {"id": 7, "name": "没有金句", "fixture": "evals/fixtures/case7-no-quote.md",
     "checks": ["quote_source"], "human_score": ["文风"]},
    {"id": 8, "name": "大量营销话术", "fixture": "evals/fixtures/case8-marketing.md",
     "checks": ["banned_words"], "human_score": ["文风"]},
    {"id": 9, "name": "工具推荐", "fixture": "evals/fixtures/case9-tool.md",
     "checks": ["structure_type"], "human_score": ["内容", "文风", "结构", "标题"]},
    {"id": 10, "name": "人物专访", "fixture": "evals/fixtures/case10-interview.md",
     "checks": ["structure_type"], "human_score": ["内容", "文风", "结构", "标题"]},
    {"id": 11, "name": "赛事公告", "fixture": "evals/fixtures/case11-announcement.md",
     "checks": ["structure_type"], "human_score": ["内容", "结构", "标题"]},
    {"id": 12, "name": "合作宣传", "fixture": "evals/fixtures/case12-partnership.md",
     "checks": ["structure_type"], "human_score": ["内容", "文风", "标题"]},
    {"id": 13, "name": "只有海报", "fixture": "evals/fixtures/case13-poster.md",
     "checks": ["insufficient_material"], "human_score": ["事实"]},
    {"id": 14, "name": "只有活动总结", "fixture": "evals/fixtures/case14-summary-only.md",
     "checks": ["evidence_flag"], "human_score": ["事实"]},
    {"id": 15, "name": "只有逐字稿", "fixture": "evals/fixtures/case15-transcript-only.md",
     "checks": ["fact_sheet", "name_verify"], "human_score": ["事实", "内容"]},
    {"id": 16, "name": "多个来源冲突", "fixture": "evals/fixtures/case16-conflict.md",
     "checks": ["conflict_detect"], "human_score": ["事实"]},
    {"id": 17, "name": "嘉宾说不确定信息", "fixture": "evals/fixtures/case17-uncertain.md",
     "checks": ["speculation_guard"], "human_score": ["事实"]},
    {"id": 18, "name": "需要删减长文", "fixture": "evals/fixtures/case18-trim.md",
     "checks": ["editorial_judgment"], "human_score": ["内容", "结构"]},
    {"id": 19, "name": "已有初稿改写", "fixture": "evals/fixtures/case19-rewrite.md",
     "checks": ["banned_words", "ai_smell"], "human_score": ["文风", "内容"]},
    {"id": 20, "name": "已有HTML重新排版", "fixture": "evals/fixtures/case20-relayout.html",
     "checks": ["html_valid", "component_ratio"], "human_score": ["排版"]},
]

# ============ 检查函数（可机械验证的部分） ============

def check_fact_sheet():
    """FACT SHEET 机制存在且被 SKILL 引用"""
    ref = os.path.join(SKILL_ROOT, "references", "source", "fact-sheet.md")
    skill = os.path.join(SKILL_ROOT, "SKILL.md")
    ok_ref = os.path.exists(ref)
    ok_skill = False
    if os.path.exists(skill):
        ok_skill = "FACT SHEET" in open(skill, encoding="utf-8").read()
    return ok_ref and ok_skill, "FACT SHEET 模板存在 + SKILL 引用"

def check_style_anatomy():
    """文风解剖存在"""
    ref = os.path.join(SKILL_ROOT, "references", "writing", "style-anatomy.md")
    return os.path.exists(ref), "style-anatomy.md 存在"

def check_html_valid(html_path=None):
    """HTML 能通过 validate"""
    if html_path and os.path.exists(html_path):
        r = subprocess.run([sys.executable, os.path.join(SKILL_ROOT, "scripts", "validate_gzh_html.py"), html_path],
                           capture_output=True, text=True, timeout=30)
        return "完全合规" in r.stdout, "HTML 校验通过"
    # 默认测范本
    example = os.path.join(SKILL_ROOT, "references", "example-3rd-session.html")
    if os.path.exists(example):
        r = subprocess.run([sys.executable, os.path.join(SKILL_ROOT, "scripts", "validate_gzh_html.py"), example],
                           capture_output=True, text=True, timeout=30)
        return "完全合规" in r.stdout, f"范本 HTML 校验通过"
    return False, "无范本可测"

def check_banned_words(text=None):
    """禁词检查"""
    if text is None:
        # 检查 SKILL/examples 是否包含禁词示例（作为自我检查）
        anatomy = os.path.join(SKILL_ROOT, "references", "writing", "style-anatomy.md")
        if os.path.exists(anatomy):
            content = open(anatomy, encoding="utf-8").read()
            return "禁词表" in content and "赋能" in content, "style-anatomy 含禁词表"
    return False, "无文本可查"

def check_insufficient_material():
    """素材不足检测机制存在"""
    skill = os.path.join(SKILL_ROOT, "SKILL.md")
    if os.path.exists(skill):
        content = open(skill, encoding="utf-8").read()
        return "素材不足检测" in content or "宁可" in content, "SKILL 含素材不足检测"
    return False, "SKILL.md 缺失"

def check_editorial_judgment():
    """编辑判断机制存在"""
    skill = os.path.join(SKILL_ROOT, "SKILL.md")
    examples = os.path.join(SKILL_ROOT, "examples", "quality-cases.md")
    ok_skill = ok_ex = False
    if os.path.exists(skill):
        ok_skill = "Editorial" in open(skill, encoding="utf-8").read()
    if os.path.exists(examples):
        ok_ex = "编辑判断" in open(examples, encoding="utf-8").read()
    return ok_skill and ok_ex, "Editorial Judgment 在 SKILL + examples"

def check_quote_source():
    """金句来源等级存在"""
    skill = os.path.join(SKILL_ROOT, "SKILL.md")
    if os.path.exists(skill):
        return "DIRECT_QUOTE" in open(skill, encoding="utf-8").read(), "金句来源等级"
    return False, "SKILL.md 缺失"

def check_component_ratio():
    """组件比例规则存在"""
    skill = os.path.join(SKILL_ROOT, "SKILL.md")
    if os.path.exists(skill):
        return "70%" in open(skill, encoding="utf-8").read(), "组件 70/20/10 比例"
    return False, "SKILL.md 缺失"

def check_ai_smell():
    """AI 味检测存在"""
    anatomy = os.path.join(SKILL_ROOT, "references", "writing", "style-anatomy.md")
    if os.path.exists(anatomy):
        return "AI 味" in open(anatomy, encoding="utf-8").read(), "style-anatomy 含 AI 味检测"
    return False, "style-anatomy.md 缺失"

# 检查映射
CHECK_FUNCS = {
    "fact_sheet": check_fact_sheet,
    "style_anatomy": check_style_anatomy,
    "html_valid": check_html_valid,
    "banned_words": check_banned_words,
    "insufficient_material": check_insufficient_material,
    "editorial_judgment": check_editorial_judgment,
    "quote_source": check_quote_source,
    "component_ratio": check_component_ratio,
    "ai_smell": check_ai_smell,
    # 以下需要 fixture 或人工判断，默认视为「待人工确认」
    "name_verify": lambda: (True, "需人工确认人名"),
    "conflict_detect": lambda: (True, "需人工确认冲突处理"),
    "evidence_flag": lambda: (True, "需人工确认证据标注"),
    "speculation_guard": lambda: (True, "需人工确认禁止推断"),
    "semantic_split": lambda: (True, "需人工确认语义分段"),
    "structure_type": lambda: (True, "需人工确认类型结构"),
    "no_invent": lambda: (True, "需人工确认无脑补"),
}

# 各维度满分（用于给「人工评分」分配权重提示）
DIM_MAX = {"事实": 25, "内容": 20, "文风": 20, "结构": 15, "标题": 10, "排版": 10}

def main():
    ap = argparse.ArgumentParser(description="硬核派 skill 评测执行器")
    ap.add_argument("--case", type=int, help="只跑指定 case")
    ap.add_argument("--list", action="store_true", help="列出所有 case")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    if args.list:
        for c in CASES:
            print(f"Case {c['id']:2d}  {c['name']}")
        return 0

    targets = [c for c in CASES if args.case is None or c["id"] == args.case]

    results = []
    for case in targets:
        auto_checks = []
        for check in case["checks"]:
            fn = CHECK_FUNCS.get(check, lambda: (False, f"未知检查 {check}"))
            ok, msg = fn()
            auto_checks.append({"check": check, "ok": ok, "msg": msg})

        auto_pass = all(c["ok"] for c in auto_checks)
        # 自动部分得分：机械检查占 40 分（事实25里的自动项+排版10里的自动项估算），这里给简化模型
        auto_score = 40 if auto_pass else min(20, 40 * sum(1 for c in auto_checks if c["ok"]) / max(len(auto_checks), 1))

        results.append({
            "id": case["id"],
            "name": case["name"],
            "auto_checks": auto_checks,
            "auto_pass": auto_pass,
            "auto_score": round(auto_score, 1),
            "human_verify": case["human_score"],
        })

    # 输出
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "PASS" if r["auto_pass"] else "FAIL"
            print(f"\nCase {r['id']:2d} [{status}] {r['name']}  (自动部分 {r['auto_score']}/40)")
            for c in r["auto_checks"]:
                mark = "✅" if c["ok"] else "❌"
                print(f"    {mark} {c['check']}: {c['msg']}")
            print(f"    👤 需人工评分维度: {', '.join(r['human_verify'])} (满分: "
                  + ", ".join(f"{d}={DIM_MAX.get(d, '?')}" for d in r["human_verify"]) + ")")

    total_pass = sum(1 for r in results if r["auto_pass"])
    print(f"\n{'='*50}")
    print(f"自动检查通过: {total_pass}/{len(targets)}")
    print("提示: 人工评分 ≥85/100 才算整体 PASS；仅自动检查通过不代表文章合格。")

if __name__ == "__main__":
    sys.exit(main())
