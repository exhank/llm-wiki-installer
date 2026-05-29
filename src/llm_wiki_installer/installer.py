from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any

from .command_runner import run
from .errors import InstallerError
from .install_options import Options
from .qmd_setup import initialize_qmd
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
    tool_versions,
)
from .upstream_skills import install_upstream_skills, select_upstream_skills


def run_install(options: Options) -> None:
    source_root_path = source_root()
    target_path = Path(options.target_input or os.getcwd()).expanduser().resolve()
    today = date.today().isoformat()

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

    log("Check tools", quiet=options.json_output)
    check_required_tools(
        selected_tools,
        install_missing=options.install_tools,
        quiet=options.json_output,
    )
    versions = tool_versions(selected_tools)

    log("Prepare target", quiet=options.json_output)
    prepare_target(target)

    log("Install upstream skills", quiet=options.json_output)
    upstream = install_upstream_skills(target, selected_skills)

    log("Generate target files", quiet=options.json_output)
    context = template_context(target, today, versions, upstream, selected_tools)
    write_generated_files(
        target, context, force=options.force, quiet=options.json_output
    )

    if "qmd" in selected_tools:
        log("Initialize qmd", quiet=options.json_output)
        initialize_qmd(target, quiet=options.json_output)
    else:
        log("Skip qmd", quiet=options.json_output)
        if not options.json_output:
            print("qmd was not selected; skipping collection initialization.")

    log("Verify target", quiet=options.json_output)
    run(["bash", ".scripts/postrun.sh"], cwd=target, quiet=options.json_output)
    run(
        ["bash", ".scripts/check-index-log.sh"],
        cwd=target,
        quiet=options.json_output,
    )
    run(["git", "diff", "--stat"], cwd=target, check=False, quiet=options.json_output)

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
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"Generated llm-wiki knowledge vault at: {target}")


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
        print(f"== {message} ==")


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
        return ("Ar9av", "kepano")
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
        "installMissingTools": options.install_tools,
        "selectedTools": list(selected_tools),
        "selectedSkills": list(selected_skills),
        "wouldCreateDirectories": list(REQUIRED_DIRECTORIES),
        "wouldWriteFiles": [relative_path for relative_path, _ in GENERATED_FILES],
        "wouldRunNetworkSteps": network_steps(
            selected_tools, selected_skills, options.install_tools, options.offline
        ),
    }


def emit_install_plan(
    options: Options,
    target: Path,
    selected_tools: tuple[str, ...],
    selected_skills: tuple[str, ...],
) -> None:
    plan = install_plan(options, target, selected_tools, selected_skills)
    if options.json_output:
        print(json.dumps(plan, sort_keys=True))
        return

    print("Dry run: no files were written and no network steps were run.")
    print(f"Target: {plan['target']}")
    print(f"Tools: {', '.join(selected_tools) if selected_tools else 'none'}")
    print(
        f"Upstream Skills: {', '.join(selected_skills) if selected_skills else 'none'}"
    )
    print(f"Install missing tools: {str(options.install_tools).lower()}")
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


def network_steps(
    selected_tools: tuple[str, ...],
    selected_skills: tuple[str, ...],
    install_tools: bool,
    offline: bool,
) -> list[str]:
    if offline:
        return []
    steps = []
    if "qmd" in selected_tools and install_tools:
        steps.append("npm install -g @tobilu/qmd if qmd is missing")
    for skill in selected_skills:
        steps.append(f"git clone pinned upstream Skill source: {skill}")
    return steps
