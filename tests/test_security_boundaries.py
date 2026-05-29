from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from llm_wiki_installer import upstream_skills
from llm_wiki_installer.errors import InstallerError
from llm_wiki_installer.install_options import Options
from llm_wiki_installer.installer import run_install
from llm_wiki_installer.path_safety import reject_path_symlink
from llm_wiki_installer.target_layout import prepare_target, write_file
from llm_wiki_installer.upstream_skills import (
    install_one_upstream_repo,
    install_upstream_skills,
    reject_upstream_symlinks,
)


def test_prepare_target_rejects_symlinked_layout_path(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / ".agents").symlink_to(outside, target_is_directory=True)

    with pytest.raises(InstallerError, match="refusing to write through symlink"):
        prepare_target(tmp_path)


def test_reject_path_symlink_rejects_file_and_parent_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    symlinked_parent = tmp_path / "nested"
    symlinked_parent.symlink_to(outside, target_is_directory=True)

    with pytest.raises(InstallerError, match="refusing to write through symlink"):
        reject_path_symlink(symlinked_parent / "file.txt", tmp_path)

    target_file = tmp_path / "file.txt"
    target_file.symlink_to(outside / "file.txt")

    with pytest.raises(InstallerError, match="refusing to write through symlink"):
        reject_path_symlink(target_file, tmp_path)


def test_write_file_rejects_symlink_destination(tmp_path: Path) -> None:
    outside = tmp_path / "outside.txt"
    destination = tmp_path / "README.md"
    destination.symlink_to(outside)

    with pytest.raises(InstallerError, match="refusing to write through symlink"):
        write_file(destination, "body", target=tmp_path, force=True)


def test_install_one_upstream_repo_uses_git_option_separator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    commands: list[list[str]] = []

    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        commands.append(command)
        if command[:2] == ["git", "clone"]:
            skill_file = Path(command[-1], ".skills", "new", "SKILL.md")
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("# New\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    def fake_command_output(_command: list[str], fallback: str = "") -> str:
        del fallback
        return "abc123"

    monkeypatch.setattr(upstream_skills, "run", fakerun)
    monkeypatch.setattr(upstream_skills, "command_output", fake_command_output)

    repo_url = "https://example.test/repo"
    clone_target = tmp_path / "clone"

    install_one_upstream_repo(
        repo_url, "example/repo", "abc123", tmp_path / "target", clone_target
    )

    assert commands[0] == [
        "git",
        "clone",
        "--no-checkout",
        "--depth",
        "1",
        "--",
        repo_url,
        str(clone_target),
    ]


def test_reject_upstream_symlinks_rejects_nested_symlink(tmp_path: Path) -> None:
    source = tmp_path / ".skills"
    skill = source / "skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    (skill / "linked").symlink_to(tmp_path / "outside")

    with pytest.raises(InstallerError, match="contains a symlink"):
        reject_upstream_symlinks(source, "example/repo")


def test_install_upstream_skills_rejects_symlinked_install_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    install_target = tmp_path / ".agents/skills/upstream/kepano"
    install_target.parent.mkdir(parents=True)
    install_target.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.install_one_upstream_repo",
        lambda _repo_url, _repo_slug, _pinned_commit, target, _tmp_dir: target.mkdir(
            parents=True
        )
        or _pinned_commit,
    )

    with pytest.raises(InstallerError, match="refusing to write through symlink"):
        install_upstream_skills(tmp_path, ("Ar9av",))


def test_run_install_rejects_source_child_before_creating_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    target = source / "generated-vault"

    monkeypatch.setattr("llm_wiki_installer.installer.source_root", lambda: source)

    with pytest.raises(InstallerError, match="child paths"):
        run_install(Options(force=False, target_input=str(target), interactive=False))

    assert not target.exists()
