#!/usr/bin/env python3
import json, os, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md", "README.md", "INSTALL.md", "CHANGELOG.md", "LICENSE",
    "plugins/feynman_super_tutor/plugin.yaml", "plugins/feynman_super_tutor/__init__.py",
    "plugins/feynman_super_tutor/schemas.py", "plugins/feynman_super_tutor/tools.py",
    "references/visual-interactive-learning.md", "templates/h5-brief.md",
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
    "version: 1.1.0",
    "## 零、自动安装与启用协议",
    "视觉互动增强协议",
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
]
for name in required_schema_names:
    if not hasattr(schemas, name):
        fail(f"schema missing {name}")

with tempfile.TemporaryDirectory() as td:
    os.environ["HERMES_HOME"] = td
    r = json.loads(tools.feynman_save_learning_card({"subject": "数学", "topic": "一次函数", "mastered": ["会画图"], "misconceptions": ["斜率和截距混淆"], "current_boundary": "能背定义但变式不稳", "next_questions": ["一次函数图像为什么是一条直线？"]}))
    if not r.get("success"):
        fail("save tool failed")
    prof = json.loads(tools.feynman_read_learning_profile({"subject": "数学"}))
    if prof.get("total_cards") != 1:
        fail("read profile failed")
    plan = json.loads(tools.feynman_generate_review_plan({"subject": "数学", "days": 3}))
    if len(plan.get("plan", [])) != 3:
        fail("review plan failed")
    mat = json.loads(tools.feynman_ingest_material({"title": "测试材料", "text": "一次函数是形如y=kx+b的函数。它的图像是一条直线。k影响倾斜程度，b影响与y轴交点。"}))
    if not mat.get("success"):
        fail("ingest failed")
    assess = json.loads(tools.feynman_assess_visual_need({"subject": "物理", "topic": "浮力", "learner_message": "我不懂浮力和排开体积的关系", "observed_gap": "变量关系不清", "last_attempts": ["浮力就是往上"]}))
    if assess.get("recommended_asset") not in {"interactive_h5", "step_diagram_or_h5", "diagram"}:
        fail("visual assessment failed")
    brief = json.loads(tools.feynman_generate_interactive_h5_brief({"topic": "浮力", "learning_goal": "理解浮力变量", "learner_gap": "变量关系不清", "asset_type": "interactive_h5"}))
    if not brief.get("success"):
        fail("h5 brief failed")
    generated = json.loads(tools.feynman_create_interactive_h5({"title": "浮力互动小实验", "subject": "物理", "topic": "浮力", "learning_goal": "观察液体密度和排开体积对浮力的影响", "interaction_type": "buoyancy"}))
    if not generated.get("success"):
        fail("h5 generation failed")
    check = json.loads(tools.feynman_check_visual_asset({"file_path": generated["file_path"], "expected_interactions": ["rho", "vol"]}))
    if not check.get("passed"):
        fail(f"h5 static check failed: {check}")
    assets = json.loads(tools.feynman_list_visual_assets({"topic": "浮力"}))
    if assets.get("count", 0) < 1:
        fail("asset listing failed")

print("PASS: package acceptance checks passed")
