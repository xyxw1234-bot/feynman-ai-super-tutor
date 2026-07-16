#!/usr/bin/env python3
import json, os, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["SKILL.md", "README.md", "INSTALL.md", "CHANGELOG.md", "LICENSE", "plugins/feynman_super_tutor/plugin.yaml", "plugins/feynman_super_tutor/__init__.py"]
BAD = ["~/.claude/skills", "保证提分", "盗版教材库", "伪按钮", "TODO", "YOUR_TOKEN", "api_key="]


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

for f in REQUIRED:
    if not (ROOT/f).exists(): fail(f"missing {f}")

skill = (ROOT/'SKILL.md').read_text(encoding='utf-8')
if not skill.startswith('---\n'): fail('SKILL.md frontmatter missing')
if len(skill) > 100000: fail('SKILL.md too large')
if 'name: feynman-ai-super-tutor' not in skill: fail('skill name wrong')
if 'description:' not in skill: fail('description missing')
if '## 零、自动安装与启用协议' not in skill: fail('auto install protocol missing')
if 'hermes plugins install xyxw1234-bot/feynman-ai-super-tutor/plugins/feynman_super_tutor --force --enable' not in (ROOT/'README.md').read_text(encoding='utf-8') + (ROOT/'INSTALL.md').read_text(encoding='utf-8') + skill: fail('plugin install command missing')
if '版权' not in skill or '未成年人' not in skill: fail('safety/copyright boundary missing')

scan_files = []
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix not in {'.md','.py','.yaml','.yml','.txt'}:
        continue
    if p.name == 'acceptance.py':
        continue
    scan_files.append(p)
all_text='\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in scan_files)
for bad in BAD:
    if bad in all_text: fail(f'bad text found: {bad}')

# plugin import and tool smoke test
sys.path.insert(0, str(ROOT/'plugins'))
import feynman_super_tutor.tools as tools
with tempfile.TemporaryDirectory() as td:
    os.environ['HERMES_HOME']=td
    r=json.loads(tools.feynman_save_learning_card({'subject':'数学','topic':'一次函数','mastered':['会画图'],'misconceptions':['斜率和截距混淆'],'current_boundary':'能背定义但变式不稳','next_questions':['一次函数图像为什么是一条直线？']}))
    if not r.get('success'): fail('save tool failed')
    prof=json.loads(tools.feynman_read_learning_profile({'subject':'数学'}))
    if prof.get('total_cards') != 1: fail('read profile failed')
    plan=json.loads(tools.feynman_generate_review_plan({'subject':'数学','days':3}))
    if len(plan.get('plan',[])) != 3: fail('review plan failed')
    mat=json.loads(tools.feynman_ingest_material({'title':'测试材料','text':'一次函数是形如y=kx+b的函数。它的图像是一条直线。k影响倾斜程度，b影响与y轴交点。'}))
    if not mat.get('success'): fail('ingest failed')

print('PASS: package acceptance checks passed')
