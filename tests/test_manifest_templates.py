from __future__ import annotations

import json
from pathlib import Path

from llm_wiki_installer.target_layout import template_context
from llm_wiki_installer.template_renderer import render_template
from llm_wiki_installer.toolchain import ToolVersions
from llm_wiki_installer.upstream_skills import UpstreamInstall


def test_template_context_maps_versions_and_upstream_installs() -> None:
    context = template_context(
        Path("/tmp/vault"),
        "2026-05-28",
        ToolVersions(
            node="v22.3.0",
            npm="10.8.0",
            qmd="qmd 1.2.3",
            rg="ripgrep 14.1.0",
            fzf="0.56.0",
        ),
        {
            "Ar9av": UpstreamInstall(
                "https://example.test/ar9av", "a" * 40, "a" * 40, 1
            ),
            "kepano": UpstreamInstall(
                "https://example.test/kepano", "b" * 40, "b" * 40, 2
            ),
        },
        ("qmd", "rg", "fzf"),
    )

    assert context["TARGET"] == "/tmp/vault"
    assert context["INSTALLER_NAME"] == "llm-wiki-installer"
    assert context["AR9AV_PINNED_COMMIT"] == "a" * 40
    assert context["AR9AV_COMMIT"] == "a" * 40
    assert context["KEPANO_COUNT"] == "2"
    assert context["QMD_RESULT"] == "installed"
    assert context["TARGET_JSON"] == '"/tmp/vault"'


def test_template_context_records_skipped_tools_and_skills() -> None:
    context = template_context(
        Path("/tmp/vault"),
        "2026-05-28",
        ToolVersions(
            node="skipped",
            npm="skipped",
            qmd="skipped",
            rg="ripgrep 14.1.0",
            fzf="skipped",
        ),
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

    assert context["QMD_RESULT"] == "skipped"
    assert context["RG_RESULT"] == "installed"
    assert context["FZF_RESULT"] == "skipped"
    assert context["AR9AV_RESULT"] == "skipped"
    assert "qmd was not selected" in context["QMD_POLICY"]
    assert "Ar9av/obsidian-wiki` was not selected" in context["UPSTREAM_SKILL_POLICY"]


def test_render_template_replaces_context_tokens(
    template_context: dict[str, str],
) -> None:
    rendered = render_template("skill-manifest.md", template_context)

    assert "Generated: 2026-05-28" in rendered
    assert "| Collection Path | /tmp/vault |" in rendered
    assert "| Name | llm-wiki-installer |" in rendered
    assert "third-party upstream artifact" in rendered
    assert (
        "| obsidian-git plugin | bundled Obsidian community plugin template | 2.38.3 | installed |"
        in rendered
    )
    assert "{{" not in rendered


def test_render_json_manifest_template(
    template_context: dict[str, str],
) -> None:
    rendered = render_template("skill-manifest.json", template_context)

    manifest = json.loads(rendered)

    assert manifest["installer"]["name"] == "llm-wiki-installer"
    assert manifest["target"] == "/tmp/vault"
    assert (
        manifest["upstreamSkills"][0]["sourceType"] == "third-party upstream artifact"
    )
    assert manifest["upstreamSkills"][0]["pinnedCommit"] == "a" * 40
    assert manifest["upstreamSkills"][1]["installedSkills"] == 2
    assert manifest["obsidianAssets"]["plugins"][0]["id"] == "obsidian-git"
    assert (
        ".obsidian/workspace.json"
        in manifest["obsidianAssets"]["excludedVolatileFiles"]
    )
    assert ".obsidian/plugins/obsidian-git/main.js" in manifest["generatedFiles"]
    assert "{{" not in rendered
