#!/usr/bin/env python3
import json, os, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md", "README.md", "INSTALL.md", "CHANGELOG.md", "LICENSE",
    "plugins/feynman_super_tutor/plugin.yaml", "plugins/feynman_super_tutor/__init__.py",
    "plugins/feynman_super_tutor/schemas.py", "plugins/feynman_super_tutor/tools.py",
    "references/visual-interactive-learning.md", "templates/h5-brief.md",
    "references/subject-training-and-resource-policy.md", "references/visual-asset-delivery-qa.md", "references/broad-learning-companion-protocol.md", "references/china-k12-official-curriculum-source-map.md", "templates/practice-set.md", "templates/study-plan.md", "templates/exam-paper-blueprint.md", "templates/learning-report.md",
]
BAD = ["~/" + ".claude/skills", "保证" + "提分", "盗版" + "教材库", "伪" + "按钮", "TO" + "DO", "YOUR" + "_TOKEN", "api" + "_key="]


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

for f in REQUIRED:
    if not (ROOT / f).exists():
        fail(f"missing {f}")

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
if not skill.startswith("---\n"):
    fail("SKILL.md frontmatter missing")
if len(skill) > 100000:
    fail("SKILL.md too large")
for needle in [
    "name: feynman-ai-super-tutor",
    "version: 1.3.5",
    "## 零、自动安装与启用协议",
    "视觉互动增强协议",
    "学科训练与提分增强协议",
    "空白图片与假交付事故防线",
    "超级学伴宽入口协议",
    "feynman_triage_broad_learning_goal",
    "feynman_generate_subject_study_plan",
    "feynman_generate_exam_paper_blueprint",
    "feynman_map_subject_training",
    "feynman_generate_practice_set",
    "feynman_assess_visual_need",
    "feynman_create_interactive_h5",
    "feynman_check_visual_asset",
    "版权",
    "未成年人",
]:
    if needle not in skill:
        fail(f"skill missing {needle}")

combined_install = (ROOT / "README.md").read_text(encoding="utf-8") + (ROOT / "INSTALL.md").read_text(encoding="utf-8") + skill
if "hermes plugins install xyxw1234-bot/feynman-ai-super-tutor/plugins/feynman_super_tutor --force --enable" not in combined_install:
    fail("plugin install command missing")

plugin_yaml = (ROOT / "plugins/feynman_super_tutor/plugin.yaml").read_text(encoding="utf-8")
if 'version: "1.3.5"' not in plugin_yaml:
    fail("plugin version not v1.3.5")
for tool_name in ["feynman_map_subject_training", "feynman_plan_resource_lookup", "feynman_check_resource_source",
    "feynman_align_curriculum_topic", "feynman_generate_learning_report", "feynman_generate_practice_set", "feynman_save_practice_attempt", "feynman_triage_broad_learning_goal", "feynman_plan_curriculum_lookup", "feynman_generate_subject_study_plan", "feynman_generate_exam_paper_blueprint"]:
    if tool_name not in plugin_yaml:
        fail(f"plugin.yaml missing {tool_name}")

scan_files = []
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix not in {".md", ".py", ".yaml", ".yml", ".txt"}:
        continue
    if p.name == "acceptance.py":
        continue
    scan_files.append(p)
all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in scan_files)
for bad in BAD:
    if bad in all_text:
        fail(f"bad text found: {bad}")

sys.path.insert(0, str(ROOT / "plugins"))
import importlib
schemas = importlib.import_module("feynman_super_tutor.schemas")
tools = importlib.import_module("feynman_super_tutor.tools")

required_schema_names = [
    "SAVE_LEARNING_CARD", "READ_PROFILE", "REVIEW_PLAN", "INGEST_MATERIAL",
    "VISUAL_NEED_ASSESS", "INTERACTIVE_H5_BRIEF", "CREATE_INTERACTIVE_H5",
    "VISUAL_ASSET_CHECK", "LIST_VISUAL_ASSETS",
    "SUBJECT_MAP", "RESOURCE_LOOKUP", "PRACTICE_SET", "SAVE_PRACTICE_ATTEMPT",
    "BROAD_GOAL_TRIAGE", "STUDY_PLAN", "PAPER_BLUEPRINT", "CURRICULUM_LOOKUP_PLAN", "RESOURCE_SOURCE_CHECK", "CURRICULUM_TOPIC_ALIGN", "LEARNING_REPORT",
]
for name in required_schema_names:
    if not hasattr(schemas, name):
        fail(f"schema missing {name}")

with tempfile.TemporaryDirectory() as td:
    os.environ["HERMES_HOME"] = td
    r = json.loads(tools.feynman_save_learning_card({"subject": "数学", "topic": "一次函数", "mastered": ["会画图"], "misconceptions": ["斜率和截距混淆"], "current_boundary": "能背定义但变式不稳", "next_questions": ["一次函数图像为什么是一条直线？"], "user_confirmed": True}))
    if not r.get("success"):
        fail("save tool failed")
    prof = json.loads(tools.feynman_read_learning_profile({"subject": "数学"}))
    if prof.get("total_cards") != 1:
        fail("read profile failed")
    plan = json.loads(tools.feynman_generate_review_plan({"subject": "数学", "days": 3}))
    if len(plan.get("plan", [])) != 3:
        fail("review plan failed")
    mat = json.loads(tools.feynman_ingest_material({"title": "测试材料", "source_type": "用户原创", "user_has_rights": True, "text": "一次函数是形如y=kx+b的函数。它的图像是一条直线。k影响倾斜程度，b影响与y轴交点。"}))
    if not mat.get("success"):
        fail("ingest failed")
    long_bad = json.loads(tools.feynman_ingest_material({"title": "整本教辅全部题目", "source_type": "不明", "text": "这是版权不明材料。" * 2000}))
    if not long_bad.get("needs_rights_confirmation") and long_bad.get("error_code") not in {"rights_confirmation_required", "copyright_boundary"}:
        fail("material copyright guard failed")
    src = json.loads(tools.feynman_check_resource_source({"url": "https://basic.smartedu.cn/syncClassroom", "title": "国家中小学智慧教育平台"}))
    if not src.get("verified_official"):
        fail("source verification failed")
    src2 = json.loads(tools.feynman_check_resource_source({"url": "https://example.com/some-paper", "title": "中考真题转载"}))
    if src2.get("can_label_as_official_exam"):
        fail("unverified source should not be official")

    align = json.loads(tools.feynman_align_curriculum_topic({"grade": "四年级", "subject": "数学", "textbook_version": "人教版", "book": "上册", "chapter": "混合运算", "topic": "加减乘除混合运算"}))
    if not align.get("success") or "数与代数" not in align.get("curriculum_card", {}).get("standard_domain", "") or "运算顺序" not in "\n".join(align.get("curriculum_card", {}).get("exam_points", [])):
        fail(f"curriculum topic alignment failed: {align}")
    assess = json.loads(tools.feynman_assess_visual_need({"subject": "物理", "topic": "浮力", "learner_message": "我不懂浮力和排开体积的关系", "observed_gap": "变量关系不清", "last_attempts": ["浮力就是往上"]}))
    if assess.get("recommended_asset") not in {"interactive_h5", "step_diagram_or_h5", "diagram"}:
        fail("visual assessment failed")
    brief = json.loads(tools.feynman_generate_interactive_h5_brief({"topic": "浮力", "learning_goal": "理解浮力变量", "learner_gap": "变量关系不清", "asset_type": "interactive_h5"}))
    if not brief.get("success"):
        fail("h5 brief failed")
    generated = json.loads(tools.feynman_create_interactive_h5({"title": "浮力互动小实验", "subject": "物理", "topic": "浮力", "learning_goal": "观察液体密度和排开体积对浮力的影响", "interaction_type": "buoyancy"}))
    if not generated.get("success"):
        fail("h5 generation failed")
    check = json.loads(tools.feynman_check_visual_asset({"file_path": generated["internal_only"]["file_path"], "expected_interactions": ["rho", "vol"]}))
    if not check.get("passed"):
        fail(f"h5 static check failed: {check}")
    generic = json.loads(tools.feynman_create_interactive_h5({"title": "通用互动", "topic": "未知主题", "learning_goal": "测试", "interaction_type": "generic_slider"}))
    generic_check = json.loads(tools.feynman_check_visual_asset({"file_path": generic["internal_only"]["file_path"]}))
    if generic_check.get("passed") or not generic.get("requires_subject_customization"):
        fail("generic H5 should not pass student-ready QA")
    assets = json.loads(tools.feynman_list_visual_assets({"topic": "浮力"}))
    if assets.get("count", 0) < 1:
        fail("asset listing failed")

    mapped = json.loads(tools.feynman_map_subject_training({"learner_message": "初二物理浮力中考题我不会，尤其是图像和排开体积", "topic": "浮力"}))
    if mapped.get("stage") != "初中" or mapped.get("subject") != "物理":
        fail(f"subject training map failed: {mapped}")
    lookup = json.loads(tools.feynman_plan_resource_lookup({"stage": "初中", "subject": "物理", "topic": "浮力", "exam_goal": "中考"}))
    if not lookup.get("success") or not lookup.get("queries"):
        fail("resource lookup planning failed")
    practice = json.loads(tools.feynman_generate_practice_set({"stage": "初中", "subject": "物理", "topic": "浮力", "difficulty": "考试表达", "count": 2}))
    if practice.get("copyright_status", "").find("原创") < 0 or len(practice.get("items", [])) < 2:
        fail("practice generation failed")
    attempt = json.loads(tools.feynman_save_practice_attempt({"subject": "物理", "topic": "浮力", "question_type": "实验探究题", "learner_answer": "浮力只和深度有关", "lost_points": ["混淆深度和排开体积"], "misconception": "认为越深浮力一定越大", "next_variant": "完全浸没后的变式", "review_priority": "高", "user_confirmed": True}))
    if not attempt.get("saved"):
        fail("practice attempt save failed")

    broad = json.loads(tools.feynman_triage_broad_learning_goal({"learner_message": "我马上期中考试了，帮我规划一下初二数学复习", "known_grade": "初二", "known_subject": "数学", "time_available": "14天"}))
    if broad.get("intent") != "期中" or "教材版本或课本目录/封面" not in broad.get("missing_context", []):
        fail(f"broad goal triage failed: {broad}")
    curr = json.loads(tools.feynman_plan_curriculum_lookup({"grade": "初二", "subject": "数学", "textbook_version": "人教版", "scope": "前三章"}))
    if not curr.get("success") or "basic.smartedu.cn 国家中小学智慧教育平台" not in curr.get("preferred_sources", []):
        fail("curriculum lookup plan failed")
    study = json.loads(tools.feynman_generate_subject_study_plan({"grade": "初二", "subject": "数学", "textbook_version": "人教版", "scope": "前三章", "goal_type": "期中", "days": 5, "daily_minutes": 40}))
    if len(study.get("daily_plan", [])) != 5 or study.get("goal_type") != "期中":
        fail("subject study plan failed")
    paper = json.loads(tools.feynman_generate_exam_paper_blueprint({"grade": "七年级", "subject": "语文", "textbook_version": "统编版", "scope": "第一、二单元", "exam_type": "期中", "duration_minutes": 120, "total_score": 100}))
    if not paper.get("success") or not paper.get("blueprint") or "不得伪称官方真题" not in paper.get("generation_rules", []):
        fail("exam paper blueprint failed")

print("PASS: package acceptance checks passed")
