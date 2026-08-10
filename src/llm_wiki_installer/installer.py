from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .command_runner import command_output, run
from .errors import InstallerError
from .install_options import Options
from .target_layout import (
    GENERATED_FILES,
    REQUIRED_DIRECTORIES,
    prepare_target,
    template_context,
    write_generated_files,
)
from .toolchain import (
    DEPENDENCY_TOOL_OPTIONS,
    check_required_tools,
    select_dependency_tools,
)
from .upstream_skills import (
    DEFAULT_SKILL_SELECTION,
    install_upstream_skills,
    select_upstream_skills,
)

# Entries that may already exist in a target directory without the installer
# treating it as non-empty.
HARMLESS_TARGET_ENTRIES = {".git", ".DS_Store", ".localized", ".obsidian"}


def run_install(options: Options) -> None:
    source_root_path = source_root()
    target_path = Path(options.target_input or os.getcwd()).expanduser().resolve()
    today = date.today().isoformat()
    install_timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    install_timestamp = install_timestamp.replace("+00:00", "Z")

    reject_generator_target(target_path, source_root_path)
    target = target_path

    selected_tools = resolve_dependency_tools(options)
    selected_skills = resolve_upstream_skills(options)

    if options.dry_run:
        emit_install_plan(options, target, selected_tools, selected_skills)
        return

    if options.offline and selected_skills:
        raise InstallerError(
            "offline mode cannot install upstream Skills. Re-run with "
            "--skills none, or disable --offline."
        )

    target = absolute_directory(target)
    ensure_safe_target(target, force=options.force, quiet=options.json_output)

    log("Check tools", quiet=options.json_output)
    check_required_tools(selected_tools)

    log("Prepare target", quiet=options.json_output)
    prepare_target(target)

    log("Install upstream skills", quiet=options.json_output)
    upstream = install_upstream_skills(target, selected_skills)

    log("Generate target files", quiet=options.json_output)
    context = template_context(today, install_timestamp, upstream, selected_tools)
    write_generated_files(
        target, context, force=options.force, quiet=options.json_output
    )

    log("Verify target", quiet=options.json_output)
    verify_target(target, quiet=options.json_output)

    log("Done", quiet=options.json_output)
    result = {
        "action": "install",
        "target": str(target),
        "force": options.force,
        "offline": options.offline,
        "selectedTools": list(selected_tools),
        "selectedSkills": list(selected_skills),
    }
    if options.json_output:
        print(json.dumps(result, sort_keys=True), flush=True)
    else:
        print(f"Generated llm-wiki knowledge vault at: {target}", flush=True)


def verify_target(target: Path, quiet: bool = False) -> None:
    """Run the generated vault checks without failing the install.

    The checks report on the vault's current working tree, which may contain
    legitimate pre-existing user changes on re-install. The install itself has
    already succeeded by this point, so check findings are advisory here.
    """
    issues = False
    for script in (".scripts/postrun.sh", ".scripts/check-index-log.sh"):
        result = run(["bash", script], cwd=target, check=False, quiet=quiet)
        if result.returncode != 0:
            issues = True
    run(
        ["git", "--no-pager", "diff", "--stat"],
        cwd=target,
        check=False,
        quiet=quiet,
    )
    if issues and not quiet:
        print(
            "note: vault checks reported issues above; the install itself "
            "succeeded. Review and fix them before the next commit.",
            flush=True,
        )


def source_root() -> Path:
    env_root = os.environ.get("LLM_WIKI_INSTALLER_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "src/llm_wiki_installer/__main__.py").is_file():
            return candidate
    return Path(__file__).resolve().parents[2]


def absolute_directory(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def ensure_safe_target(target: Path, force: bool, quiet: bool = False) -> None:
    """Refuse surprising targets unless --force is passed.

    Re-running inside an already generated vault is always allowed. Otherwise
    a non-empty directory, or a directory nested inside another Git
    repository, needs an explicit --force.
    """
    if (target / "AGENTS.md").is_file() and (target / "wiki").is_dir():
        return

    entries = {entry.name for entry in target.iterdir()}
    unexpected = sorted(entries - HARMLESS_TARGET_ENTRIES)
    if unexpected and not force:
        preview = ", ".join(unexpected[:5])
        raise InstallerError(
            f"target directory is not empty (found: {preview}). Choose an "
            "empty directory, or re-run with --force to install here anyway."
        )

    enclosing = enclosing_git_root(target)
    if enclosing is not None:
        if not force:
            raise InstallerError(
                f"target is inside an existing Git repository ({enclosing}). "
                "Installing would create a nested repository. Choose a "
                "directory outside that repository, or re-run with --force."
            )
        if not quiet:
            print(
                f"warning: creating a nested Git repository inside {enclosing}.",
                flush=True,
            )


def enclosing_git_root(target: Path) -> Path | None:
    if (target / ".git").exists():
        return None
    output = command_output(["git", "-C", str(target), "rev-parse", "--show-toplevel"])
    if not output:
        return None
    toplevel = Path(output)
    if (
        toplevel.is_absolute()
        and toplevel != target
        and target.is_relative_to(toplevel)
    ):
        return toplevel
    return None


def reject_generator_target(target: Path, source_root_path: Path) -> None:
    source_root_path = source_root_path.expanduser().resolve()
    target = target.expanduser().resolve()

    if target == source_root_path or target.is_relative_to(source_root_path):
        raise InstallerError(
            "target must not be this generator repository or one of its "
            f"child paths: {source_root_path}"
        )

    if (target / "docs/llm-wiki-generation-guide.md").is_file() and (
        target / "docs/technical-design.md"
    ).is_file():
        raise InstallerError(
            f"target looks like the llm-wiki generator repository: {target}"
        )


def log(message: str, quiet: bool = False) -> None:
    if not quiet:
        print(f"== {message} ==", flush=True)


def resolve_dependency_tools(options: Options) -> tuple[str, ...]:
    if options.tools is not None:
        return options.tools
    if options.dry_run:
        return tuple(option[0] for option in DEPENDENCY_TOOL_OPTIONS)
    return select_dependency_tools(options.interactive)


def resolve_upstream_skills(options: Options) -> tuple[str, ...]:
    if options.skills is not None:
        return options.skills
    if options.offline:
        return ()
    if options.dry_run:
        return DEFAULT_SKILL_SELECTION
    return select_upstream_skills(options.interactive)


def install_plan(
    options: Options,
    target: Path,
    selected_tools: tuple[str, ...],
    selected_skills: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "action": "dry-run",
        "target": str(target),
        "force": options.force,
        "offline": options.offline,
        "selectedTools": list(selected_tools),
        "selectedSkills": list(selected_skills),
        "wouldCreateDirectories": list(REQUIRED_DIRECTORIES),
        "wouldWriteFiles": [relative_path for relative_path, _ in GENERATED_FILES],
        "wouldRunNetworkSteps": network_steps(selected_skills, options.offline),
    }


def emit_install_plan(
    options: Options,
    target: Path,
    selected_tools: tuple[str, ...],
    selected_skills: tuple[str, ...],
) -> None:
    plan = install_plan(options, target, selected_tools, selected_skills)
    if options.json_output:
        print(json.dumps(plan, sort_keys=True), flush=True)
        return

    print("Dry run: no files were written and no network steps were run.")
    print(f"Target: {plan['target']}")
    print(f"Tools: {', '.join(selected_tools) if selected_tools else 'none'}")
    print(
        f"Upstream Skills: {', '.join(selected_skills) if selected_skills else 'none'}"
    )
    print(f"Offline: {str(options.offline).lower()}")
    print("Would create directories:")
    for path in plan["wouldCreateDirectories"]:
        print(f"  - {path}")
    print("Would write generated files:")
    for path in plan["wouldWriteFiles"]:
        print(f"  - {path}")
    print("Would run network steps:")
    for step in plan["wouldRunNetworkSteps"] or ["none"]:
        print(f"  - {step}")


def network_steps(selected_skills: tuple[str, ...], offline: bool) -> list[str]:
    if offline:
        return []
    return [
        f"git clone pinned upstream Skill source: {skill}" for skill in selected_skills
    ]
