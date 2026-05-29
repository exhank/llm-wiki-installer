from __future__ import annotations

import json

from llm_wiki_installer.target_layout import template_context
from llm_wiki_installer.template_renderer import render_template
from llm_wiki_installer.upstream_skills import UpstreamInstall


def test_template_context_maps_retrieval_tools_and_upstream_installs() -> None:
    context = template_context(
        "2026-05-28",
        {
            "Ar9av": UpstreamInstall(
                "https://example.test/ar9av", "a" * 40, "a" * 40, 1
            ),
            "kepano": UpstreamInstall(
                "https://example.test/kepano", "b" * 40, "b" * 40, 2
            ),
        },
        ("rg", "fzf"),
    )

    assert context["RETRIEVAL_TOOLS"] == "rg, or fzf"
    assert (
        "Install pinned upstream skills from `Ar9av/obsidian-wiki`"
        in context["UPSTREAM_SKILL_POLICY"]
    )


def test_template_context_maps_skipped_upstream_skills() -> None:
    context = template_context(
        "2026-05-28",
        {
            "Ar9av": UpstreamInstall(
                "https://example.test/ar9av", "a" * 40, "skipped", 0, "skipped"
            ),
            "kepano": UpstreamInstall(
                "https://example.test/kepano", "b" * 40, "b" * 40, 2
            ),
        },
        ("rg",),
    )

    assert context["RETRIEVAL_TOOLS"] == "rg"
    assert "Ar9av/obsidian-wiki` was not selected" in context["UPSTREAM_SKILL_POLICY"]


def test_render_jsonl_log_template(template_context: dict[str, str]) -> None:
    rendered = render_template("wiki-log.jsonl", template_context)

    entries = [json.loads(line) for line in rendered.splitlines()]

    assert entries == [
        {
            "date": "2026-05-28",
            "type": "schema-update",
            "scope": "llm-wiki initial repository artifacts",
            "reason": (
                "Generated fixed llm-wiki repository-root artifacts from "
                "llm-wiki generator."
            ),
            "review": "self-reviewed",
            "impact": {
                "index_updated": True,
                "references_checked": True,
            },
            "files": [
                "AGENTS.md",
                "README.md",
                "wiki/index.md",
                "wiki/log.jsonl",
                ".codex/config.toml",
                ".scripts/postrun.sh",
                ".scripts/check-index-log.sh",
                ".gitignore",
            ],
        }
    ]
    assert "{{" not in rendered
