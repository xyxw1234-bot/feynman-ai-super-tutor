from pathlib import Path
import os
from . import schemas, tools


def register(ctx):
    ctx.register_tool(name="feynman_save_learning_card", toolset="feynman_super_tutor", schema=schemas.SAVE_LEARNING_CARD, handler=tools.feynman_save_learning_card)
    ctx.register_tool(name="feynman_read_learning_profile", toolset="feynman_super_tutor", schema=schemas.READ_PROFILE, handler=tools.feynman_read_learning_profile)
    ctx.register_tool(name="feynman_generate_review_plan", toolset="feynman_super_tutor", schema=schemas.REVIEW_PLAN, handler=tools.feynman_generate_review_plan)
    ctx.register_tool(name="feynman_ingest_material", toolset="feynman_super_tutor", schema=schemas.INGEST_MATERIAL, handler=tools.feynman_ingest_material)

    # If the Skill is installed in this profile, expose it to plugin-aware builds
    # without assuming a fixed repository layout. The public raw SKILL.md install
    # remains the source of truth; plugin-only installs still provide tools.
    home = Path(os.environ.get("HERMES_HOME") or Path.home()).expanduser()
    candidates = [
        home / "skills" / "education" / "feynman-ai-super-tutor" / "SKILL.md",
        home / "skills" / "feynman-ai-super-tutor" / "SKILL.md",
    ]
    for skill_md in candidates:
        if skill_md.exists():
            ctx.register_skill("feynman-ai-super-tutor", skill_md)
            break
