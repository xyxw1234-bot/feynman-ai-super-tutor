from pathlib import Path
from . import schemas, tools


def register(ctx):
    ctx.register_tool(name="feynman_save_learning_card", toolset="feynman_super_tutor", schema=schemas.SAVE_LEARNING_CARD, handler=tools.feynman_save_learning_card)
    ctx.register_tool(name="feynman_read_learning_profile", toolset="feynman_super_tutor", schema=schemas.READ_PROFILE, handler=tools.feynman_read_learning_profile)
    ctx.register_tool(name="feynman_generate_review_plan", toolset="feynman_super_tutor", schema=schemas.REVIEW_PLAN, handler=tools.feynman_generate_review_plan)
    ctx.register_tool(name="feynman_ingest_material", toolset="feynman_super_tutor", schema=schemas.INGEST_MATERIAL, handler=tools.feynman_ingest_material)
    skill_md = Path(__file__).resolve().parents[1].parents[1] / "SKILL.md"
    if skill_md.exists():
        ctx.register_skill("feynman-ai-super-tutor", skill_md)
