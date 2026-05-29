from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional

from .command_runner import command_output, run
from .errors import InstallerError
from .path_safety import reject_path_symlink
from .terminal_ui import select_options

UPSTREAM_REPOS = (
    (
        "https://github.com/Ar9av/obsidian-wiki",
        "Ar9av/obsidian-wiki",
        "Ar9av",
        "347e85704c52474d13470a3919e4a5cd7e3809cb",
    ),
    (
        "https://github.com/kepano/obsidian-skills",
        "kepano/obsidian-skills",
        "kepano",
        "553ef99aa3306dd23f268e1ba9af752577684f69",
    ),
)

UPSTREAM_SKILL_OPTIONS = (
    (
        "Ar9av",
        "Ar9av/obsidian-wiki",
        "Upstream Obsidian wiki skills copied as third-party artifacts",
    ),
    (
        "kepano",
        "kepano/obsidian-skills",
        "Upstream Obsidian skills copied as third-party artifacts",
    ),
)


@dataclass(frozen=True)
class UpstreamInstall:
    repo_url: str
    pinned_commit: str
    commit: str
    skill_count: int
    result: str = "installed"


def select_upstream_skills(interactive: bool) -> tuple[str, ...]:
    return select_options(
        "Select upstream skill sources to install",
        UPSTREAM_SKILL_OPTIONS,
        interactive=interactive,
    )


def install_upstream_skills(
    target: Path, selected_skills: Iterable[str]
) -> Mapping[str, UpstreamInstall]:
    results: dict[str, UpstreamInstall] = {}
    selected = set(selected_skills)

    with tempfile.TemporaryDirectory(prefix="llm-wiki-upstream.") as tmp:
        tmp_base = Path(tmp)
        for repo_url, repo_slug, target_name, pinned_commit in UPSTREAM_REPOS:
            install_target = target / ".agents/skills/upstream" / target_name
            reject_path_symlink(install_target, target)
            if target_name not in selected:
                if install_target.exists():
                    shutil.rmtree(install_target)
                results[target_name] = UpstreamInstall(
                    repo_url=repo_url,
                    pinned_commit=pinned_commit,
                    commit="skipped",
                    skill_count=0,
                    result="skipped",
                )
                continue

            clone_target = tmp_base / repo_slug.replace("/", "-")
            commit = install_one_upstream_repo(
                repo_url, repo_slug, pinned_commit, install_target, clone_target
            )
            skill_count = count_skill_dirs(install_target)
            results[target_name] = UpstreamInstall(
                repo_url=repo_url,
                pinned_commit=pinned_commit,
                commit=commit,
                skill_count=skill_count,
            )

    return results


def install_one_upstream_repo(
    repo_url: str, repo_slug: str, pinned_commit: str, target: Path, tmp_dir: Path
) -> str:
    run(
        ["git", "clone", "--no-checkout", "--depth", "1", "--", repo_url, str(tmp_dir)],
        quiet=True,
        error=(
            f"failed to clone upstream Skill source {repo_slug}. Check network "
            "access, or re-run with --skills none."
        ),
    )
    run(
        ["git", "-C", str(tmp_dir), "fetch", "--depth", "1", "origin", pinned_commit],
        quiet=True,
        error=(f"failed to fetch pinned commit for upstream Skill source {repo_slug}."),
    )
    run(
        ["git", "-C", str(tmp_dir), "checkout", "--detach", pinned_commit],
        quiet=True,
        error=f"failed to check out pinned commit for upstream Skill source {repo_slug}.",
    )
    resolved_commit = command_output(["git", "-C", str(tmp_dir), "rev-parse", "HEAD"])
    if resolved_commit != pinned_commit:
        raise InstallerError(
            f"{repo_slug} resolved to {resolved_commit or 'unknown'}, "
            f"expected pinned commit {pinned_commit}."
        )

    source_dir = upstream_skill_source(tmp_dir)
    if source_dir is None:
        raise InstallerError(f"{repo_slug} has no .skills/ or skills/ directory.")
    reject_upstream_symlinks(source_dir, repo_slug)

    if not has_discovered_skill_file(source_dir):
        raise InstallerError(f"{repo_slug} has no discovered SKILL.md files.")

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    copy_directory_contents(source_dir, target)

    return resolved_commit


def upstream_skill_source(repo_dir: Path) -> Optional[Path]:
    for name in (".skills", "skills"):
        candidate = repo_dir / name
        if candidate.is_dir():
            return candidate
    return None


def has_discovered_skill_file(source_dir: Path) -> bool:
    for path in source_dir.rglob("SKILL.md"):
        depth = len(path.relative_to(source_dir).parts)
        if depth <= 2:
            return True
    return False


def reject_upstream_symlinks(source_dir: Path, repo_slug: str) -> None:
    if source_dir.is_symlink():
        raise InstallerError(f"{repo_slug} has a symlinked skill source directory.")
    for path in source_dir.rglob("*"):
        if path.is_symlink():
            relative = path.relative_to(source_dir)
            raise InstallerError(
                f"{repo_slug} contains a symlink in its skill source: {relative}"
            )


def copy_directory_contents(source: Path, target: Path) -> None:
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(child, destination)


def count_skill_dirs(directory: Path) -> int:
    return sum(
        1
        for child in directory.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )
