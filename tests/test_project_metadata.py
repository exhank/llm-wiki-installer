from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_github_action_badges_target_existing_workflows() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    workflow_badges = set(re.findall(r"actions/workflows/([^/)]+)", readme))

    assert workflow_badges == {"ci.yml", "release.yml"}
    for workflow in workflow_badges:
        assert (REPO_ROOT / ".github" / "workflows" / workflow).is_file()


def test_release_notes_config_exists() -> None:
    assert (REPO_ROOT / ".github" / "release.yml").is_file()


def test_readme_pypi_badge_targets_published_project() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    init_text = (REPO_ROOT / "src/llm_wiki_installer/__init__.py").read_text(
        encoding="utf-8"
    )
    version_match = re.search(r'__version__ = "([^"]+)"', init_text)

    assert version_match
    assert (
        "img.shields.io/badge/dynamic/json"
        "?url=https%3A%2F%2Fpypi.org%2Fpypi%2Fllm-wiki-installer%2F"
        f"{version_match.group(1)}%2Fjson&query=%24.info.version&label=PyPI&prefix=v"
    ) in readme
    assert "https://pypi.org/project/llm-wiki-installer/" in readme


def test_readme_uses_latest_version_placeholders_for_user_commands() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "llm-wiki-installer==0.1.0" not in readme
    assert "raw.githubusercontent.com/exhank/llm-wiki-installer/v0.1.0" not in readme
    assert "llm-wiki-installer==<version>" in readme
    assert "https://github.com/exhank/llm-wiki-installer/releases/latest" in readme
    assert "url_effective" not in readme


def test_streamed_launcher_does_not_hard_code_release_ref() -> None:
    launcher = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")

    assert "LLM_WIKI_INSTALLER_REF:-v0.1.0" not in launcher
    assert "releases/latest" in launcher


def test_github_actions_are_pinned_to_full_commit_shas() -> None:
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / ".github" / "workflows").glob("*.yml")
    )
    action_refs = re.findall(r"uses:\s+[\w.-]+/[\w.-]+@([^\s#]+)", workflow_text)

    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)


def test_release_workflow_uses_pypi_trusted_publishing() -> None:
    release_workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert "environment: pypi" in release_workflow
    assert "id-token: write" in release_workflow
    assert "pypa/gh-action-pypi-publish@" in release_workflow
    assert "password:" not in release_workflow
    assert "api-token" not in release_workflow


def test_release_workflow_creates_release_with_explicit_repository() -> None:
    release_workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert 'gh release create "${GITHUB_REF_NAME}"' in release_workflow
    assert '--repo "${GITHUB_REPOSITORY}"' in release_workflow
