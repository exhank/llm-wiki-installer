from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from .command_runner import run
from .path_safety import reject_path_symlink
from .template_renderer import render_template
from .upstream_skills import UpstreamInstall

REQUIRED_DIRECTORIES = (
    "inbox",
    "raw",
    "attachments",
    "wiki/maps",
    "outputs",
    "archives",
    "schema",
    ".agents/skills",
    ".claude",
    ".scripts",
    ".obsidian/plugins/obsidian-git",
    ".obsidian/themes/Things",
)

# Empty contract directories receive a .gitkeep placeholder so the layout
# survives commit, push, and clone.
GITKEEP_DIRECTORIES = (
    "inbox",
    "raw",
    "attachments",
    "wiki/maps",
    "outputs",
    "archives",
)

GENERATED_FILES = (
    ("AGENTS.md", "AGENTS.md"),
    ("CLAUDE.md", "CLAUDE.md"),
    ("README.md", "README.md"),
    ("wiki/index.md", "wiki-index.md"),
    ("wiki/tags.md", "wiki-tags.md"),
    ("wiki/log.jsonl", "wiki-log.jsonl"),
    ("schema/workflow.md", "schema/workflow.md"),
    ("schema/log.md", "schema/log.md"),
    ("schema/wiki-page.md", "schema/wiki-page.md"),
    ("schema/map.md", "schema/map.md"),
    (".codex/config.toml", "codex-config.toml"),
    (".codex/hooks.json", "codex-hooks.json"),
    (".scripts/postrun.sh", "postrun.sh"),
    (".scripts/check-index-log.sh", "check-index-log.sh"),
    (".obsidian/app.json", "obsidian/app.json"),
    (".obsidian/appearance.json", "obsidian/appearance.json"),
    (".obsidian/backlink.json", "obsidian/backlink.json"),
    (".obsidian/community-plugins.json", "obsidian/community-plugins.json"),
    (".obsidian/core-plugins.json", "obsidian/core-plugins.json"),
    (".obsidian/graph.json", "obsidian/graph.json"),
    (".obsidian/hotkeys.json", "obsidian/hotkeys.json"),
    (
        ".obsidian/plugins/obsidian-git/data.json",
        "obsidian/plugins/obsidian-git/data.json",
    ),
    (
        ".obsidian/plugins/obsidian-git/main.js",
        "obsidian/plugins/obsidian-git/main.js",
    ),
    (
        ".obsidian/plugins/obsidian-git/manifest.json",
        "obsidian/plugins/obsidian-git/manifest.json",
    ),
    (
        ".obsidian/plugins/obsidian-git/obsidian_askpass.sh",
        "obsidian/plugins/obsidian-git/obsidian_askpass.sh",
    ),
    (
        ".obsidian/plugins/obsidian-git/styles.css",
        "obsidian/plugins/obsidian-git/styles.css",
    ),
    (
        ".obsidian/themes/Things/manifest.json",
        "obsidian/themes/Things/manifest.json",
    ),
    (".obsidian/themes/Things/theme.css", "obsidian/themes/Things/theme.css"),
    (".gitignore", "gitignore"),
) + tuple((f"{directory}/.gitkeep", "gitkeep") for directory in GITKEEP_DIRECTORIES)

EXECUTABLE_FILES = (
    ".scripts/postrun.sh",
    ".scripts/check-index-log.sh",
    ".obsidian/plugins/obsidian-git/obsidian_askpass.sh",
)


def prepare_target(target: Path) -> None:
    for relative in REQUIRED_DIRECTORIES:
        destination = target / relative
        reject_path_symlink(destination, target)
        destination.mkdir(parents=True, exist_ok=True)

    link_claude_skills(target)

    if not (target / ".git").is_dir():
        run(["git", "-C", str(target), "init"], quiet=True)


def link_claude_skills(target: Path) -> None:
    """Expose .agents/skills to Claude Code via its .claude/skills path."""
    claude_skills = target / ".claude/skills"
    if claude_skills.is_symlink() or claude_skills.exists():
        return
    claude_skills.symlink_to(Path("../.agents/skills"))


def template_context(
    today: str,
    install_timestamp: str,
    upstream: Mapping[str, UpstreamInstall],
    selected_tools: Iterable[str],
) -> Mapping[str, str]:
    selected = set(selected_tools)
    context = {
        "TODAY": today,
        "INSTALL_TIMESTAMP": install_timestamp,
        "RETRIEVAL_TOOLS": retrieval_tools_text(selected),
        "SEARCH_COMMANDS": search_commands_text(selected),
        "UPSTREAM_SKILL_POLICY": upstream_skill_policy_text(upstream),
    }
    return context | {
        f"{key}_JSON": json.dumps(value) for key, value in context.items()
    }


def retrieval_tools_text(selected_tools: set[str]) -> str:
    labels = []
    if "rg" in selected_tools:
        labels.append("rg")
    if "fzf" in selected_tools:
        labels.append("fzf")
    if not labels:
        return "the files recorded in `wiki/index.md` and `wiki/maps/`"
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + f", or {labels[-1]}"


def search_commands_text(selected_tools: set[str]) -> str:
    commands = []
    if "rg" in selected_tools:
        commands.append('rg "keyword" wiki raw inbox outputs archives')
    if "fzf" in selected_tools:
        commands.append("rg --files | fzf")
    if not commands:
        commands.append("# Open wiki/index.md and follow links to relevant maps/pages.")
    return "\n".join(commands)


def upstream_skill_policy_text(upstream: Mapping[str, UpstreamInstall]) -> str:
    lines = []
    for key, label in (
        ("Ar9av", "Ar9av/obsidian-wiki"),
        ("kepano", "kepano/obsidian-skills"),
    ):
        result = upstream[key].result
        if result == "installed":
            lines.append(f"- Install pinned upstream skills from `{label}`.")
        else:
            lines.append(f"- `{label}` was not selected during installation.")
    return "\n".join(lines)


def write_generated_files(
    target: Path, context: Mapping[str, str], force: bool, quiet: bool = False
) -> None:
    for relative_path, template_name in GENERATED_FILES:
        destination = target / relative_path
        content = render_template(template_name, context)
        write_file(destination, content, target=target, force=force, quiet=quiet)

    for relative_path in EXECUTABLE_FILES:
        path = target / relative_path
        reject_path_symlink(path, target)
        path.chmod(path.stat().st_mode | 0o755)


def write_file(
    path: Path, content: str, target: Path, force: bool, quiet: bool = False
) -> None:
    reject_path_symlink(path, target)
    relative = path.relative_to(target)
    if path.exists() and not force:
        if not quiet:
            print(f"keep existing {relative}", flush=True)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if not quiet:
        print(f"wrote {relative}", flush=True)
