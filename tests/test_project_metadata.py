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


def test_readme_static_badges_do_not_depend_on_unpublished_pypi_project() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "img.shields.io/pypi/" not in readme
    assert "pypi.org/project/llm-wiki-installer" not in readme


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
