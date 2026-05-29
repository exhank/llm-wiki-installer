from __future__ import annotations

import json

import pytest


@pytest.fixture
def template_context() -> dict[str, str]:
    context = {
        "TODAY": "2026-05-28",
        "RETRIEVAL_TOOLS": "rg, or fzf",
        "SEARCH_COMMANDS": (
            'rg "keyword" wiki raw inbox outputs archives\n' "rg --files | fzf"
        ),
        "UPSTREAM_SKILL_POLICY": (
            "- Install pinned upstream skills from `Ar9av/obsidian-wiki`.\n"
            "- Install pinned upstream skills from `kepano/obsidian-skills`."
        ),
    }
    return context | {
        f"{key}_JSON": json.dumps(value) for key, value in context.items()
    }
