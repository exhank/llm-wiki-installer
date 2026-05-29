from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from . import __version__
from .command_runner import run
from .path_safety import reject_path_symlink
from .template_renderer import render_template
from .toolchain import ToolVersions
from .upstream_skills import UpstreamInstall

REQUIRED_DIRECTORIES = (
    "inbox",
    "raw",
    "wiki/maps",
    "outputs",
    "archive",
    ".agents/skills/upstream",
    ".codex/hooks",
    ".scripts",
    ".obsidian/plugins/obsidian-git",
    ".obsidian/themes/Things",
)

GENERATED_FILES = (
    ("AGENTS.md", "AGENTS.md"),
    ("README.md", "README.md"),
    ("wiki/index.md", "wiki-index.md"),
    ("wiki/log.md", "wiki-log.md"),
    (".agents/skill-manifest.md", "skill-manifest.md"),
    (".agents/skill-manifest.json", "skill-manifest.json"),
    (".codex/config.toml", "codex-config.toml"),
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
)

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

    if not (target / ".git").is_dir():
        run(["git", "-C", str(target), "init"], quiet=True)


def template_context(
    target: Path,
    today: str,
    versions: ToolVersions,
    upstream: Mapping[str, UpstreamInstall],
    selected_tools: Iterable[str],
) -> Mapping[str, str]:
    selected = set(selected_tools)
    context = {
        "TODAY": today,
        "TARGET": str(target),
        "INSTALLER_VERSION": __version__,
        "INSTALLER_NAME": "llm-wiki-installer",
        "NODE_VERSION": versions.node,
        "NPM_VERSION": versions.npm,
        "QMD_VERSION": versions.qmd,
        "RG_VERSION": versions.rg,
        "FZF_VERSION": versions.fzf,
        "QMD_RESULT": "installed" if "qmd" in selected else "skipped",
        "RG_RESULT": "installed" if "rg" in selected else "skipped",
        "FZF_RESULT": "installed" if "fzf" in selected else "skipped",
        "QMD_POLICY": qmd_policy_text("qmd" in selected),
        "QMD_POSTRUN_CHECK": qmd_postrun_check("qmd" in selected),
        "RETRIEVAL_TOOLS": retrieval_tools_text(selected),
        "SEARCH_COMMANDS": search_commands_text(selected),
        "UPSTREAM_SKILL_POLICY": upstream_skill_policy_text(upstream),
        "AR9AV_PINNED_COMMIT": upstream["Ar9av"].pinned_commit,
        "AR9AV_COMMIT": upstream["Ar9av"].commit,
        "AR9AV_COUNT": str(upstream["Ar9av"].skill_count),
        "AR9AV_RESULT": upstream["Ar9av"].result,
        "KEPANO_PINNED_COMMIT": upstream["kepano"].pinned_commit,
        "KEPANO_COMMIT": upstream["kepano"].commit,
        "KEPANO_COUNT": str(upstream["kepano"].skill_count),
        "KEPANO_RESULT": upstream["kepano"].result,
    }
    return context | {
        f"{key}_JSON": json.dumps(value) for key, value in context.items()
    }


def qmd_policy_text(qmd_selected: bool) -> str:
    if qmd_selected:
        return "\n".join(
            (
                "- Use `tobi/qmd`.",
                "- Package: `@tobilu/qmd`.",
                "- Install automatically with `npm install -g @tobilu/qmd` if `qmd` is missing.",
                "- Collection name: `knowledge-vault`.",
                "- Collection path: repository root.",
                "- Index scope: the whole vault.",
                "- If qmd installation, version detection, collection initialization, "
                "update, or embed fails, stop and report failure.",
            )
        )
    return "\n".join(
        (
            "- qmd was not selected during installation.",
            "- Do not assume qmd commands are available in this vault.",
            "- Use installed retrieval tools recorded in `.agents/skill-manifest.md`.",
            "- Re-run the installer and select qmd if Markdown collection indexing is required.",
        )
    )


def qmd_postrun_check(qmd_selected: bool) -> str:
    if not qmd_selected:
        return (
            'echo "qmd was not selected during install; skipping qmd post-run check."'
        )
    return "\n".join(
        (
            'command -v qmd >/dev/null || fail "qmd is required but not found."',
            'qmd --version >/dev/null || fail "qmd exists but qmd --version failed."',
        )
    )


def retrieval_tools_text(selected_tools: set[str]) -> str:
    labels = []
    if "qmd" in selected_tools:
        labels.append("qmd")
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
    if "qmd" in selected_tools:
        commands.append('qmd search "keyword"')
    if "rg" in selected_tools:
        commands.append('rg "keyword" wiki raw inbox outputs archive')
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
            print(f"keep existing {relative}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if not quiet:
        print(f"wrote {relative}")
