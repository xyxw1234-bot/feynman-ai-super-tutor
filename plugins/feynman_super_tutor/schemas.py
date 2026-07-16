SAVE_LEARNING_CARD = {
    "name": "feynman_save_learning_card",
    "description": "Save a confirmed Feynman learning card into the current Hermes profile's local learning vault. Use after a learning session when the user has confirmed or clearly wants learning records saved.",
    "parameters": {
        "type": "object",
        "properties": {
            "learner_id": {"type": "string", "description": "Optional learner label; default is 'default'. Do not include sensitive personal data."},
            "subject": {"type": "string"},
            "topic": {"type": "string"},
            "grade": {"type": "string"},
            "mastered": {"type": "array", "items": {"type": "string"}},
            "misconceptions": {"type": "array", "items": {"type": "string"}},
            "current_boundary": {"type": "string"},
            "next_questions": {"type": "array", "items": {"type": "string"}},
            "evidence": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["subject", "topic"]
    }
}

READ_PROFILE = {
    "name": "feynman_read_learning_profile",
    "description": "Read a concise local learning profile summary for a learner, optionally filtered by subject or topic.",
    "parameters": {
        "type": "object",
        "properties": {
            "learner_id": {"type": "string"},
            "subject": {"type": "string"},
            "topic": {"type": "string"},
            "limit": {"type": "integer", "default": 10}
        }
    }
}

REVIEW_PLAN = {
    "name": "feynman_generate_review_plan",
    "description": "Generate a spaced review plan from saved learning cards and misconceptions.",
    "parameters": {
        "type": "object",
        "properties": {
            "learner_id": {"type": "string"},
            "subject": {"type": "string"},
            "days": {"type": "integer", "default": 7}
        }
    }
}

INGEST_MATERIAL = {
    "name": "feynman_ingest_material",
    "description": "Turn user-provided legal text material into a topic map for Feynman learning. This does not fetch copyrighted resources; it only processes text the user provided or the agent legally retrieved.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "source": {"type": "string"},
            "text": {"type": "string"},
            "subject": {"type": "string"},
            "grade": {"type": "string"}
        },
        "required": ["title", "text"]
    }
}
