from pathlib import Path
import os
from . import schemas, tools


def register(ctx):
    registrations = [
        ("feynman_save_learning_card", schemas.SAVE_LEARNING_CARD, tools.feynman_save_learning_card),
        ("feynman_read_learning_profile", schemas.READ_PROFILE, tools.feynman_read_learning_profile),
        ("feynman_generate_review_plan", schemas.REVIEW_PLAN, tools.feynman_generate_review_plan),
        ("feynman_ingest_material", schemas.INGEST_MATERIAL, tools.feynman_ingest_material),
        ("feynman_assess_visual_need", schemas.VISUAL_NEED_ASSESS, tools.feynman_assess_visual_need),
        ("feynman_generate_interactive_h5_brief", schemas.INTERACTIVE_H5_BRIEF, tools.feynman_generate_interactive_h5_brief),
        ("feynman_create_interactive_h5", schemas.CREATE_INTERACTIVE_H5, tools.feynman_create_interactive_h5),
        ("feynman_publish_interactive_h5", schemas.PUBLISH_INTERACTIVE_H5, tools.feynman_publish_interactive_h5),
        ("feynman_check_visual_asset", schemas.VISUAL_ASSET_CHECK, tools.feynman_check_visual_asset),
        ("feynman_list_visual_assets", schemas.LIST_VISUAL_ASSETS, tools.feynman_list_visual_assets),
        ("feynman_map_subject_training", schemas.SUBJECT_MAP, tools.feynman_map_subject_training),
        ("feynman_plan_resource_lookup", schemas.RESOURCE_LOOKUP, tools.feynman_plan_resource_lookup),
        ("feynman_check_resource_source", schemas.RESOURCE_SOURCE_CHECK, tools.feynman_check_resource_source),
        ("feynman_align_curriculum_topic", schemas.CURRICULUM_TOPIC_ALIGN, tools.feynman_align_curriculum_topic),
        ("feynman_generate_practice_set", schemas.PRACTICE_SET, tools.feynman_generate_practice_set),
        ("feynman_save_practice_attempt", schemas.SAVE_PRACTICE_ATTEMPT, tools.feynman_save_practice_attempt),
        ("feynman_triage_broad_learning_goal", schemas.BROAD_GOAL_TRIAGE, tools.feynman_triage_broad_learning_goal),
        ("feynman_plan_curriculum_lookup", schemas.CURRICULUM_LOOKUP_PLAN, tools.feynman_plan_curriculum_lookup),
        ("feynman_generate_subject_study_plan", schemas.STUDY_PLAN, tools.feynman_generate_subject_study_plan),
        ("feynman_generate_exam_paper_blueprint", schemas.PAPER_BLUEPRINT, tools.feynman_generate_exam_paper_blueprint),
        ("feynman_generate_learning_report", schemas.LEARNING_REPORT, tools.feynman_generate_learning_report),
    ]
    for name, schema, handler in registrations:
        ctx.register_tool(name=name, toolset="feynman_super_tutor", schema=schema, handler=handler)

    # The plugin can be installed by subdirectory and must not assume a repository root.
    # If the Skill has also been installed in this profile, expose it to plugin-aware runtimes.
    home = Path(os.environ.get("HERMES_HOME") or Path.home()).expanduser()
    candidates = [
        home / "skills" / "education" / "feynman-ai-super-tutor" / "SKILL.md",
        home / "skills" / "feynman-ai-super-tutor" / "SKILL.md",
    ]
    for skill_md in candidates:
        if skill_md.exists():
            ctx.register_skill("feynman-ai-super-tutor", skill_md)
            break
