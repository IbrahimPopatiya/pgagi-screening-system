ROLE_COLLECTIONS = {
    "ai_ml_engineer": "ml_engineer_kb",
    # add more roles here once their books are ingested, e.g.:
    # "data_scientist": "data_scientist_kb",
}

# Canonical topic checklist per role, used only to compute a coverage % for the
# summary screen — a lightweight proxy for "how broadly did this interview probe
# the role's core areas," not an exhaustive syllabus.
ROLE_CORE_TOPICS = {
    "ai_ml_engineer": [
        "Supervised Learning",
        "Deep Learning",
        "Neural Networks",
        "Overfitting",
        "Regularization",
        "Reinforcement Learning",
        "Generative AI",
        "Model Evaluation",
    ],
}
