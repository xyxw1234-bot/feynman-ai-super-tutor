#!/usr/bin/env python3
"""Professional QA for feynman-ai-super-tutor public release."""
import json, os, re, sys, tempfile, importlib, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'plugins'))
import feynman_super_tutor.schemas as schemas
import feynman_super_tutor.tools as tools

failures=[]
warnings=[]

def check(cond, msg):
    if not cond:
        failures.append(msg)

def warn(cond, msg):
    if not cond:
        warnings.append(msg)

skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
plugin=(ROOT/'plugins/feynman_super_tutor/plugin.yaml').read_text(encoding='utf-8')

# 1. Public surface checks
for needle in ['version: 1.3.5','超级学伴宽入口协议','学科训练与提分增强协议','轻问诊与高效提分体验协议','官方课程教材定位与知识点对齐协议','快速定位与性能协议','学习报告与阶段评估协议','空白图片与假交付事故防线','视觉互动增强协议']:
    check(needle in skill, f'SKILL missing {needle}')
for bad in ['保证'+'提分','盗版'+'教材库','YOUR'+'_TOKEN','api'+'_key=','TO'+'DO']:
    check(bad not in skill, f'bad term in SKILL: {bad}')
check('version: "1.3.5"' in plugin, 'plugin manifest not v1.3.5')
for tool_name in ['feynman_triage_broad_learning_goal','feynman_plan_curriculum_lookup','feynman_generate_subject_study_plan','feynman_generate_exam_paper_blueprint','feynman_check_resource_source','feynman_align_curriculum_topic','feynman_generate_learning_report','feynman_check_visual_asset']:
    check(tool_name in skill and tool_name in plugin, f'tool not public-listed: {tool_name}')

# 2. Schema registration shape
for name in ['BROAD_GOAL_TRIAGE','CURRICULUM_LOOKUP_PLAN','STUDY_PLAN','PAPER_BLUEPRINT','RESOURCE_SOURCE_CHECK','CURRICULUM_TOPIC_ALIGN','LEARNING_REPORT','VISUAL_ASSET_CHECK']:
    check(hasattr(schemas, name), f'schema missing {name}')

# 3. Tool scenarios
os.environ['HERMES_HOME']=tempfile.mkdtemp(prefix='feynman-prof-qa-')
scenarios=[]

def call(name, fn, args, expect_success=True):
    try:
        out=json.loads(fn(args))
    except Exception as e:
        failures.append(f'{name} exception {e}')
        return {}
    scenarios.append((name,out))
    if expect_success:
        check(out.get('success') is True, f'{name} not success: {out}')
    return out

# 宽入口：新学期预习
s1=call('new_semester_preview', tools.feynman_triage_broad_learning_goal, {'learner_message':'我刚结束初一，下学期初二数学怎么预习前几课？'})
check(s1.get('intent')=='预习', f'preview intent wrong: {s1}')
check('教材版本或课本目录/封面' in s1.get('missing_context',[]), 'preview should ask textbook')

# 宽入口：期中复习
s2=call('midterm_review', tools.feynman_triage_broad_learning_goal, {'learner_message':'我马上期中考试了，帮我规划一下初二数学复习','known_grade':'初二','known_subject':'数学','time_available':'14天'})
check(s2.get('intent')=='期中', f'midterm intent wrong: {s2}')

# 宽入口：出卷
s3=call('paper_request_triage', tools.feynman_triage_broad_learning_goal, {'learner_message':'给我出一套七年级语文期中考试卷'})
check(s3.get('intent')=='出卷' and s3.get('exam_type')=='期中' and s3.get('exact_grade')=='七年级', f'paper triage intent/grade weak: {s3}')
check(any('教材' in q or '范围' in q for q in s3.get('ask_next',[])), 'paper triage should ask textbook/scope')


# 缺关键信息时不能生成正式计划/卷子
missing_plan=call('missing_plan_guard', tools.feynman_generate_subject_study_plan, {'subject':'数学','goal_type':'期中'}, expect_success=False)
check(missing_plan.get('needs_clarification') is True and not missing_plan.get('daily_plan'), 'missing context should block formal study plan')
missing_paper=call('missing_paper_guard', tools.feynman_generate_exam_paper_blueprint, {'subject':'数学'}, expect_success=False)
check(missing_paper.get('needs_clarification') is True and not missing_paper.get('blueprint'), 'missing context should block formal paper blueprint')

# 课程资源合法检索
s4=call('curriculum_lookup', tools.feynman_plan_curriculum_lookup, {'grade':'初二','subject':'数学','textbook_version':'人教版','book':'上册','scope':'前两章'})
check(any('basic.smartedu.cn' in x for x in s4.get('preferred_sources',[])), 'missing SmartEdu preferred source')
check(any('不批量复制' in x for x in s4.get('safe_usage',[])), 'missing copyright safe rule')


# 来源校验：官方可标，非官方不能标真题
src_ok=call('source_verification_official', tools.feynman_check_resource_source, {'url':'https://basic.smartedu.cn/syncClassroom','title':'国家中小学智慧教育平台'})
check(src_ok.get('verified_official') is True, 'official source not verified')
src_bad=call('source_verification_unverified', tools.feynman_check_resource_source, {'url':'https://example.com/zhenti','title':'中考真题转载'})
check(src_bad.get('can_label_as_official_exam') is False, 'unverified source allowed as official')

# 长材料版权闸门
long_bad=call('material_rights_guard', tools.feynman_ingest_material, {'title':'整本教辅全部题目','source_type':'不明','text':'版权不明材料。'*2000}, expect_success=False)
check(long_bad.get('needs_rights_confirmation') or long_bad.get('error_code') in {'rights_confirmation_required','copyright_boundary'}, 'long copyrighted material not blocked')


# 具体教材/章节/知识点定位
align=call('curriculum_topic_alignment', tools.feynman_align_curriculum_topic, {'grade':'四年级','subject':'数学','textbook_version':'人教版','book':'上册','chapter':'混合运算','topic':'加减乘除混合运算'})
card=align.get('curriculum_card',{})
check('数与代数' in card.get('standard_domain',''), 'mixed-operation alignment should map to 数与代数')
check(any('运算顺序' in x for x in card.get('exam_points',[])), 'mixed-operation alignment missing exam points')
check('https://basic.smartedu.cn/syncClassroom/auto' in align.get('official_lookup_plan',{}).get('smartedu_course_channel',''), 'alignment missing SmartEdu course channel')

# 学习计划
s5=call('study_plan_preview', tools.feynman_generate_subject_study_plan, {'grade':'初二','subject':'数学','textbook_version':'人教版','scope':'前两章','goal_type':'预习','days':7,'daily_minutes':35})
check(len(s5.get('daily_plan',[]))==7, 'study plan days mismatch')
check(all('feynman_check' in d for d in s5.get('daily_plan',[])), 'study plan missing Feynman checks')

# 试卷蓝图
s6=call('paper_blueprint', tools.feynman_generate_exam_paper_blueprint, {'grade':'七年级','subject':'语文','textbook_version':'统编版','scope':'第一二单元','exam_type':'期中','duration_minutes':120,'total_score':100})
check(s6.get('blueprint'), 'paper blueprint empty')
check('不得伪称官方真题' in s6.get('generation_rules',[]), 'paper blueprint missing truthfulness rule')

# 原创变式
s7=call('practice_set', tools.feynman_generate_practice_set, {'stage':'初中','subject':'物理','topic':'浮力','difficulty':'考试表达','count':3})
check('原创' in s7.get('copyright_status',''), 'practice set not marked original')
check(len(s7.get('items',[]))>=2, 'practice set too small')

# H5 generation/static QA/blank guard
h5=call('h5_generate', tools.feynman_create_interactive_h5, {'title':'浮力互动小实验','subject':'物理','topic':'浮力','learning_goal':'观察液体密度和排开体积对浮力的影响','interaction_type':'buoyancy'})
file_path=h5.get('internal_only',{}).get('file_path','')
check(file_path and Path(file_path).exists(), 'H5 file not generated')
qa=call('h5_static_check', tools.feynman_check_visual_asset, {'file_path':file_path,'expected_interactions':['rho','vol']})
check(qa.get('passed') is True, f'H5 static QA failed: {qa}')

generic=call('h5_generic_generate', tools.feynman_create_interactive_h5, {'title':'通用互动','topic':'未知主题','learning_goal':'测试','interaction_type':'generic_slider'})
generic_file=generic.get('internal_only',{}).get('file_path','')
generic_qa=call('h5_generic_static_check', tools.feynman_check_visual_asset, {'file_path':generic_file}, expect_success=True)
check(generic.get('requires_subject_customization') is True and generic_qa.get('passed') is False, 'generic H5 should require customization and fail final QA')
if file_path and Path(file_path).exists():
    html=Path(file_path).read_text(encoding='utf-8')
    for term in ['write_file','browser_navigate','/opt/data','TO'+'DO','debug']:
        check(term not in html, f'H5 leaks internal term: {term}')
    check(len(re.sub(r'<[^>]+>','',html).strip())>80, 'H5 appears text-empty')
    check('回到聊天' in html and ('滑块' in html or '拖动' in html), 'H5 missing learner task')

# 学习档案/错因保存
card=call('save_card', tools.feynman_save_learning_card, {'subject':'数学','topic':'一次函数','mastered':['知道k影响斜率'],'misconceptions':['把截距当斜率'],'current_boundary':'会代入但解释图像不稳','next_questions':['k变化图像怎么变？'],'user_confirmed':True})

report=call('learning_report_student', tools.feynman_generate_learning_report, {'audience':'学生','subject':'数学','topic':'一次函数','use_saved_records_confirmed':True})
check(report.get('report',{}).get('next_training_plan'), 'learning report missing next training plan')
check(report.get('report',{}).get('evidence',{}).get('learning_cards',0)>=1, 'learning report missing evidence')

attempt=call('save_attempt', tools.feynman_save_practice_attempt, {'subject':'物理','topic':'浮力','question_type':'实验探究题','learner_answer':'越深浮力越大','lost_points':['没有区分完全浸没前后'],'misconception':'把深度当唯一变量','next_variant':'完全浸没变式','review_priority':'高','user_confirmed':True})

# 4. Repository hygiene
import shutil
shutil.rmtree(ROOT / 'plugins/feynman_super_tutor/__pycache__', ignore_errors=True)
for p in ROOT.rglob('*'):
    if p.is_file():
        rel=p.relative_to(ROOT).as_posix()
        check('__pycache__' not in rel and not rel.endswith('.pyc'), f'cache file present: {rel}')
        if p.suffix in {'.md','.py','.yaml','.yml','.txt'} and p.name!='professional_qa.py':
            txt=p.read_text(encoding='utf-8',errors='ignore')
            for bad in ['保证'+'提分','盗版'+'教材库','YOUR'+'_TOKEN','api'+'_key=']:
                check(bad not in txt, f'{bad} found in {rel}')

print(json.dumps({'success': not failures, 'failures': failures, 'warnings': warnings, 'scenario_count': len(scenarios), 'scenarios': [name for name,_ in scenarios]}, ensure_ascii=False, indent=2))
if failures:
    sys.exit(1)
