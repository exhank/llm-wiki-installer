from __future__ import annotations

import json

import pytest


@pytest.fixture
def template_context() -> dict[str, str]:
    context = {
        "TODAY": "2026-05-28",
        "TARGET": "/tmp/vault",
        "INSTALLER_VERSION": "0.1.2",
        "INSTALLER_NAME": "llm-wiki-installer",
        "RG_VERSION": "ripgrep 14.1.0",
        "FZF_VERSION": "0.56.0",
        "RG_RESULT": "installed",
        "FZF_RESULT": "installed",
        "RETRIEVAL_TOOLS": "rg, or fzf",
        "SEARCH_COMMANDS": (
            'rg "keyword" wiki raw inbox outputs archive\n' "rg --files | fzf"
        ),
        "UPSTREAM_SKILL_POLICY": (
            "- Install pinned upstream skills from `Ar9av/obsidian-wiki`.\n"
            "- Install pinned upstream skills from `kepano/obsidian-skills`."
        ),
        "AR9AV_PINNED_COMMIT": "a" * 40,
        "AR9AV_COMMIT": "a" * 40,
        "AR9AV_COUNT": "1",
        "AR9AV_RESULT": "installed",
        "KEPANO_PINNED_COMMIT": "b" * 40,
        "KEPANO_COMMIT": "b" * 40,
        "KEPANO_COUNT": "2",
        "KEPANO_RESULT": "installed",
    }
    return context | {
        f"{key}_JSON": json.dumps(value) for key, value in context.items()
    }
