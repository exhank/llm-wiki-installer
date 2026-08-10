from __future__ import annotations

import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from llm_wiki_installer import cli
from llm_wiki_installer.command_runner import (
    command_output,
    run,
)
from llm_wiki_installer.errors import InstallerError
from llm_wiki_installer.install_options import Options, parse_options
from llm_wiki_installer.installer import (
    absolute_directory,
    enclosing_git_root,
    ensure_safe_target,
    reject_generator_target,
    run_install,
    source_root,
    verify_target,
)
from llm_wiki_installer.target_layout import (
    EXECUTABLE_FILES,
    GENERATED_FILES,
    REQUIRED_DIRECTORIES,
    prepare_target,
    retrieval_tools_text,
    search_commands_text,
    write_file,
    write_generated_files,
)
from llm_wiki_installer.template_renderer import render_template
from llm_wiki_installer.toolchain import (
    check_required_tools,
    require_executable,
)
from llm_wiki_installer.upstream_skills import (
    UpstreamInstall,
    copy_directory_contents,
    count_skill_dirs,
    flatten_skill_dirs,
    has_discovered_skill_file,
    install_one_upstream_repo,
    install_upstream_skills,
    upstream_skill_source,
)

# pylint: disable=too-many-lines


@pytest.mark.parametrize(
    ("argv", "force", "target_input", "show_help"),
    [
        ([], False, None, False),
        (["--force"], True, None, False),
        (["--no-interactive"], False, None, False),
        (["/tmp/vault"], False, "/tmp/vault", False),
        (["--force", "/tmp/vault"], True, "/tmp/vault", False),
        (["--help"], False, None, True),
    ],
)
def test_parse_options(
    argv: list[str], force: bool, target_input: str | None, show_help: bool
) -> None:
    options = parse_options(argv)

    assert options.force is force
    assert options.target_input == target_input
    assert options.show_help is show_help


def test_parse_options_disables_interactive_mode() -> None:
    assert not parse_options(["--no-interactive"]).interactive
    assert not parse_options(["--yes"]).interactive


def test_parse_options_accepts_explicit_tools_and_skills() -> None:
    options = parse_options(
        [
            "--tools",
            "rg,fzf",
            "--skills=kepano",
            "--offline",
            "--dry-run",
            "--json",
            "/tmp/vault",
        ]
    )

    assert options.tools == ("rg", "fzf")
    assert options.skills == ("kepano",)
    assert options.offline
    assert options.dry_run
    assert options.json_output
    assert options.target_input == "/tmp/vault"


def test_parse_options_rejects_removed_no_install_tools_flag() -> None:
    with pytest.raises(InstallerError, match="unknown argument: --no-install-tools"):
        parse_options(["--no-install-tools"])


def test_parse_options_accepts_none_selection() -> None:
    options = parse_options(["--tools=none", "--skills", "none"])

    assert options.tools == ()
    assert options.skills == ()


def test_parse_options_accepts_all_selection() -> None:
    options = parse_options(["--tools=all", "--skills=all"])

    assert options.tools == ("rg", "fzf")
    assert options.skills == ("Ar9av", "kepano")


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--bad"], "unknown argument: --bad"),
        (["one", "two"], "only one target path is allowed"),
        (["--tools", "bad"], "--tools contains unknown value"),
        (["--tools"], "--tools requires"),
        (["--tools="], "--tools requires a non-empty value"),
        (["--skills"], "--skills requires"),
    ],
)
def test_parse_options_rejects_invalid_arguments(argv: list[str], message: str) -> None:
    with pytest.raises(InstallerError, match=message):
        parse_options(argv)


def test_cli_main_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["--help"]) == 0

    captured = capsys.readouterr()
    assert "Usage: bash install.sh [options]" in captured.out
    assert captured.err == ""


def test_cli_main_runs_installer(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Options] = []

    def fake_run_install(options: Options) -> None:
        seen.append(options)

    monkeypatch.setattr(cli, "run_install", fake_run_install)

    assert cli.main(["--force", "/tmp/vault"]) == 0
    assert seen == [Options(force=True, target_input="/tmp/vault")]


def test_cli_main_reports_installer_errors(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_run_install(_options: Options) -> None:
        raise InstallerError("boom")

    monkeypatch.setattr(cli, "run_install", fake_run_install)

    assert cli.main(["/tmp/vault"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_main_module_exits_with_cli_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "main", lambda: 7)

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("llm_wiki_installer.__main__", run_name="__main__")

    assert excinfo.value.code == 7


def test_source_root_prefers_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = tmp_path / "src/llm_wiki_installer/__main__.py"
    module.parent.mkdir(parents=True)
    module.write_text("print('ok')\n", encoding="utf-8")
    monkeypatch.setenv("LLM_WIKI_INSTALLER_ROOT", str(tmp_path))

    assert source_root() == tmp_path.resolve()


def test_source_root_defaults_to_project_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_WIKI_INSTALLER_ROOT", raising=False)

    assert (source_root() / "pyproject.toml").is_file()


def test_absolute_directory_creates_and_resolves_path(tmp_path: Path) -> None:
    target = tmp_path / "new" / "vault"

    assert absolute_directory(target) == target.resolve()
    assert target.is_dir()


def test_reject_generator_target_rejects_source_root(tmp_path: Path) -> None:
    with pytest.raises(InstallerError, match="target must not be"):
        reject_generator_target(tmp_path, tmp_path)


def test_reject_generator_target_rejects_source_child(tmp_path: Path) -> None:
    with pytest.raises(InstallerError, match="child paths"):
        reject_generator_target(tmp_path / "nested" / "vault", tmp_path)


def test_reject_generator_target_rejects_lookalike(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "llm-wiki-generation-guide.md").write_text("", encoding="utf-8")
    (docs / "technical-design.md").write_text("", encoding="utf-8")

    with pytest.raises(InstallerError, match="target looks like"):
        reject_generator_target(tmp_path, tmp_path / "source")


def test_reject_generator_target_allows_normal_target(tmp_path: Path) -> None:
    reject_generator_target(tmp_path, tmp_path / "source")


def test_ensure_safe_target_allows_empty_directory(tmp_path: Path) -> None:
    ensure_safe_target(tmp_path, force=False)


def test_ensure_safe_target_allows_harmless_entries(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".DS_Store").write_text("", encoding="utf-8")

    ensure_safe_target(tmp_path, force=False)


def test_ensure_safe_target_allows_existing_vault(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("policy\n", encoding="utf-8")
    (tmp_path / "wiki").mkdir()
    (tmp_path / "notes.md").write_text("existing\n", encoding="utf-8")

    ensure_safe_target(tmp_path, force=False)


def test_ensure_safe_target_rejects_non_empty_directory(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("existing\n", encoding="utf-8")

    with pytest.raises(InstallerError, match="target directory is not empty"):
        ensure_safe_target(tmp_path, force=False)

    ensure_safe_target(tmp_path, force=True)


def test_ensure_safe_target_rejects_nested_git_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outer = tmp_path
    target = outer / "notes"
    target.mkdir()
    monkeypatch.setattr(
        "llm_wiki_installer.installer.command_output",
        lambda _command, fallback="": str(outer),
    )

    with pytest.raises(InstallerError, match="inside an existing Git repository"):
        ensure_safe_target(target, force=False)

    ensure_safe_target(target, force=True)


def test_enclosing_git_root_ignores_own_repo_and_non_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "llm_wiki_installer.installer.command_output",
        lambda _command, fallback="": "not-an-absolute-path",
    )
    assert enclosing_git_root(tmp_path) is None

    (tmp_path / ".git").mkdir()
    assert enclosing_git_root(tmp_path) is None


def test_run_install_dry_run_does_not_create_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "vault"

    run_install(
        Options(
            force=False,
            target_input=str(target),
            interactive=False,
            dry_run=True,
        )
    )

    assert not target.exists()
    output = capsys.readouterr().out
    assert "Dry run: no files were written" in output
    assert "Would write generated files" in output


def test_run_install_dry_run_json_outputs_plan(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "vault"

    run_install(
        Options(
            force=False,
            target_input=str(target),
            interactive=False,
            tools=("rg",),
            skills=(),
            dry_run=True,
            json_output=True,
        )
    )

    plan = json.loads(capsys.readouterr().out)
    assert plan["action"] == "dry-run"
    assert plan["target"] == str(target.resolve())
    assert plan["selectedTools"] == ["rg"]
    assert plan["selectedSkills"] == []
    assert "schema" in plan["wouldCreateDirectories"]
    assert "schema/workflow.md" in plan["wouldWriteFiles"]
    assert "schema/log.md" in plan["wouldWriteFiles"]
    assert "schema/wiki-page.md" in plan["wouldWriteFiles"]
    assert "schema/map.md" in plan["wouldWriteFiles"]


def test_run_install_offline_dry_run_defaults_to_no_upstream_skills(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "vault"

    run_install(
        Options(
            force=False,
            target_input=str(target),
            interactive=False,
            offline=True,
            dry_run=True,
            json_output=True,
        )
    )

    plan = json.loads(capsys.readouterr().out)
    assert plan["offline"]
    assert plan["selectedSkills"] == []
    assert plan["wouldRunNetworkSteps"] == []


def test_run_install_offline_rejects_explicit_upstream_skills(tmp_path: Path) -> None:
    with pytest.raises(InstallerError, match="offline mode cannot install upstream"):
        run_install(
            Options(
                force=False,
                target_input=str(tmp_path / "vault"),
                interactive=False,
                tools=(),
                skills=("kepano",),
                offline=True,
            )
        )


def test_require_executable_rejects_missing_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("llm_wiki_installer.toolchain.shutil.which", lambda _name: None)

    with pytest.raises(InstallerError, match="missing tool"):
        require_executable("missing", "missing tool")


def test_check_required_tools_skips_unselected_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "llm_wiki_installer.toolchain.shutil.which",
        lambda name: "/bin/git" if name == "git" else None,
    )

    check_required_tools(())


def test_check_required_tools_reports_missing_selected_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "llm_wiki_installer.toolchain.shutil.which",
        lambda name: None if name == "rg" else f"/bin/{name}",
    )
    with pytest.raises(InstallerError, match="rg is required but not installed"):
        check_required_tools(("rg", "fzf"))

    monkeypatch.setattr(
        "llm_wiki_installer.toolchain.shutil.which",
        lambda name: None if name == "fzf" else f"/bin/{name}",
    )
    with pytest.raises(InstallerError, match="fzf is required but not installed"):
        check_required_tools(("rg", "fzf"))


def test_verify_target_reports_issues_without_failing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def failing_run(
        command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        code = 1 if command[0] == "bash" else 0
        return subprocess.CompletedProcess(command, code)

    monkeypatch.setattr("llm_wiki_installer.installer.run", failing_run)

    verify_target(tmp_path)

    out = capsys.readouterr().out
    assert "vault checks reported issues" in out
    assert "the install itself succeeded" in out


def test_prepare_target_creates_layout_and_initializes_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("llm_wiki_installer.target_layout.run", fakerun)

    prepare_target(tmp_path)

    for relative in REQUIRED_DIRECTORIES:
        assert (tmp_path / relative).is_dir()
    claude_skills = tmp_path / ".claude/skills"
    assert claude_skills.is_symlink()
    assert claude_skills.resolve() == (tmp_path / ".agents/skills").resolve()
    assert calls == [["git", "-C", str(tmp_path), "init"]]

    prepare_target(tmp_path)
    assert claude_skills.is_symlink()


def test_prepare_target_skips_git_init_when_repo_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".git").mkdir()
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "llm_wiki_installer.target_layout.run",
        lambda command, **_kwargs: calls.append(command),
    )

    prepare_target(tmp_path)

    assert not calls


def test_dynamic_template_text_matches_selected_tools() -> None:
    assert retrieval_tools_text({"rg"}) == "rg"
    assert retrieval_tools_text({"rg", "fzf"}) == "rg, or fzf"
    assert 'rg "keyword"' in search_commands_text({"rg", "fzf"})
    assert "Open wiki/index.md" in search_commands_text(set())


def test_render_template_rejects_missing_context() -> None:
    with pytest.raises(ValueError, match="unresolved template tokens"):
        render_template("wiki-log.jsonl", {})


def test_command_output_returns_fallback_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="")

    monkeypatch.setattr("llm_wiki_installer.command_runner.run", fakerun)

    assert command_output(["bad"], fallback="fallback") == "fallback"


def test_command_output_returns_trimmed_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        return subprocess.CompletedProcess(command, 0, stdout=" value \n", stderr="")

    monkeypatch.setattr("llm_wiki_installer.command_runner.run", fakerun)

    assert command_output(["ok"], fallback="fallback") == "value"


def test_run_captures_stdout() -> None:
    result = run(
        [sys.executable, "-c", "print('hello')"],
        capture=True,
    )

    assert result.stdout == "hello\n"


def test_run_quiet_suppresses_stdout_and_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = run(
        [
            sys.executable,
            "-c",
            "import sys; print('visible stdout'); print('visible stderr', file=sys.stderr)",
        ],
        quiet=True,
    )

    captured = capsys.readouterr()
    assert result.returncode == 0
    assert captured.out == ""
    assert captured.err == ""


def test_run_raises_installer_error_on_nonzero_exit() -> None:
    with pytest.raises(InstallerError, match="custom failure"):
        run(
            [sys.executable, "-c", "raise SystemExit(3)"],
            capture=True,
            error="custom failure",
        )


def test_run_raises_installer_error_for_missing_command() -> None:
    with pytest.raises(InstallerError, match="definitely-missing is required"):
        run(["definitely-missing"])


@pytest.mark.parametrize(
    "template_name", [template_name for _, template_name in GENERATED_FILES]
)
def test_all_generated_templates_render_without_unresolved_tokens(
    template_name: str,
    template_context: dict[str, str],
) -> None:
    rendered = render_template(template_name, template_context)

    assert not re.findall(r"{{[A-Z0-9_]+}}", rendered)


def test_write_generated_files_preserves_existing_files_without_force(
    tmp_path: Path,
    template_context: dict[str, str],
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("custom readme\n", encoding="utf-8")

    write_generated_files(tmp_path, template_context, force=False)

    assert readme.read_text(encoding="utf-8") == "custom readme\n"
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / "CLAUDE.md").is_file()
    assert (tmp_path / "inbox/.gitkeep").is_file()
    assert (tmp_path / "raw/.gitkeep").is_file()
    assert (tmp_path / "wiki/maps/.gitkeep").is_file()
    assert (tmp_path / "wiki/tags.md").is_file()
    assert (tmp_path / "schema/workflow.md").is_file()
    assert (tmp_path / "schema/log.md").is_file()
    assert (tmp_path / "schema/wiki-page.md").is_file()
    assert (tmp_path / "schema/map.md").is_file()
    assert not (tmp_path / ".agents/skill-manifest.md").exists()
    assert not (tmp_path / ".agents/skill-manifest.json").exists()
    assert (tmp_path / ".codex/hooks.json").is_file()
    assert not (tmp_path / ".codex/hooks").exists()
    assert (tmp_path / ".obsidian/app.json").is_file()
    assert (tmp_path / ".obsidian/plugins/obsidian-git/main.js").is_file()
    assert not (tmp_path / ".obsidian/workspace.json").exists()
    assert not (tmp_path / ".obsidian/workspaces.json").exists()


def test_write_generated_files_overwrites_existing_files_with_force(
    tmp_path: Path,
    template_context: dict[str, str],
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("custom readme\n", encoding="utf-8")

    write_generated_files(tmp_path, template_context, force=True)

    assert readme.read_text(encoding="utf-8").startswith("# Knowledge Vault")


@pytest.mark.parametrize("relative_path", EXECUTABLE_FILES)
def test_write_generated_files_marks_scripts_executable(
    tmp_path: Path,
    template_context: dict[str, str],
    relative_path: str,
) -> None:
    write_generated_files(tmp_path, template_context, force=True)

    assert (tmp_path / relative_path).stat().st_mode & 0o111


def test_generated_obsidian_plugin_and_theme_assets(
    tmp_path: Path,
    template_context: dict[str, str],
) -> None:
    write_generated_files(tmp_path, template_context, force=True)

    assert json.loads(
        (tmp_path / ".obsidian/community-plugins.json").read_text(encoding="utf-8")
    ) == ["obsidian-git"]
    assert json.loads((tmp_path / ".obsidian/app.json").read_text(encoding="utf-8"))[
        "userIgnoreFilters"
    ] == ["archives"]
    assert '"id": "obsidian-git"' in (
        tmp_path / ".obsidian/plugins/obsidian-git/manifest.json"
    ).read_text(encoding="utf-8")
    assert '"name": "Things"' in (
        tmp_path / ".obsidian/themes/Things/manifest.json"
    ).read_text(encoding="utf-8")
    hotkeys = json.loads(
        (tmp_path / ".obsidian/hotkeys.json").read_text(encoding="utf-8")
    )
    assert hotkeys["switcher:open"] == [{"modifiers": ["Mod"], "key": "P"}]
    assert hotkeys["command-palette:open"] == [
        {"modifiers": ["Mod", "Shift"], "key": "P"}
    ]
    assert hotkeys["global-search:open"] == [
        {"modifiers": ["Mod", "Shift"], "key": "F"}
    ]
    assert hotkeys["file-explorer:new-file"] == [{"modifiers": ["Mod"], "key": "N"}]
    assert hotkeys["workspace:close"] == [{"modifiers": ["Mod"], "key": "W"}]
    assert hotkeys["workspace:undo-close-pane"] == [
        {"modifiers": ["Mod", "Shift"], "key": "T"}
    ]
    assert hotkeys["workspace:split-vertical"] == [{"modifiers": ["Mod"], "key": "\\"}]
    assert hotkeys["editor:open-search"] == [{"modifiers": ["Mod"], "key": "F"}]
    assert hotkeys["editor:open-search-replace"] == [
        {"modifiers": ["Mod", "Alt"], "key": "F"}
    ]
    assert hotkeys["editor:toggle-comment"] == [{"modifiers": ["Mod"], "key": "/"}]
    assert hotkeys["editor:set-heading-1"] == [
        {"modifiers": ["Mod", "Alt"], "key": "1"}
    ]
    assert hotkeys["app:toggle-left-sidebar"] == [{"modifiers": ["Mod"], "key": "0"}]
    assert hotkeys["obsidian-git:pull"] == [{"modifiers": ["Mod", "Shift"], "key": "G"}]


def test_write_file_creates_parent_directories(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_file(tmp_path / "nested/file.txt", "body", target=tmp_path, force=False)

    assert (tmp_path / "nested/file.txt").read_text(encoding="utf-8") == "body"
    assert "wrote nested/file.txt" in capsys.readouterr().out


def test_upstream_skill_source_prefers_dot_skills(tmp_path: Path) -> None:
    dot_skills = tmp_path / ".skills"
    skills = tmp_path / "skills"
    dot_skills.mkdir()
    skills.mkdir()

    assert upstream_skill_source(tmp_path) == dot_skills


def test_upstream_skill_source_falls_back_to_skills(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skills.mkdir()

    assert upstream_skill_source(tmp_path) == skills


def test_upstream_skill_source_returns_none_when_missing(tmp_path: Path) -> None:
    assert upstream_skill_source(tmp_path) is None


def test_has_discovered_skill_file_accepts_direct_skill(tmp_path: Path) -> None:
    skill = tmp_path / "example"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

    assert has_discovered_skill_file(tmp_path)


def test_has_discovered_skill_file_rejects_deep_skill(tmp_path: Path) -> None:
    deep = tmp_path / "nested" / "too-deep" / "skill"
    deep.mkdir(parents=True)
    (deep / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

    assert not has_discovered_skill_file(tmp_path)


def test_copy_directory_contents_merges_files_and_directories(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    (source / "skill").mkdir(parents=True)
    (source / "skill" / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    (source / "README.md").write_text("readme\n", encoding="utf-8")
    target.mkdir()

    copy_directory_contents(source, target)

    assert (target / "skill" / "SKILL.md").read_text(encoding="utf-8") == "# Skill\n"
    assert (target / "README.md").read_text(encoding="utf-8") == "readme\n"


def test_count_skill_dirs_counts_only_top_level_skill_dirs(tmp_path: Path) -> None:
    good = tmp_path / "good"
    nested = tmp_path / "nested" / "child"
    good.mkdir()
    nested.mkdir(parents=True)
    (good / "SKILL.md").write_text("# Good\n", encoding="utf-8")
    (nested / "SKILL.md").write_text("# Nested\n", encoding="utf-8")
    (tmp_path / "plain.txt").write_text("plain\n", encoding="utf-8")

    assert count_skill_dirs(tmp_path) == 1


def test_flatten_skill_dirs_replaces_existing_and_rejects_duplicates(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    skill = source / "skill"
    non_skill = source / "notes"
    skill.mkdir(parents=True)
    non_skill.mkdir()
    (skill / "SKILL.md").write_text("# New\n", encoding="utf-8")
    (non_skill / "README.md").write_text("skip\n", encoding="utf-8")

    target = tmp_path / "target"
    existing = target / ".agents/skills/skill"
    existing.mkdir(parents=True)
    (existing / "SKILL.md").write_text("# Old\n", encoding="utf-8")

    installed: set[str] = set()
    flatten_skill_dirs(
        source, target / ".agents/skills", target, "example/repo", installed
    )

    assert (target / ".agents/skills/skill/SKILL.md").read_text(
        encoding="utf-8"
    ) == "# New\n"
    assert not (target / ".agents/skills/notes").exists()
    assert installed == {"skill"}

    with pytest.raises(InstallerError, match="duplicate upstream Skill name"):
        flatten_skill_dirs(
            source, target / ".agents/skills", target, "example/other", installed
        )


def test_install_one_upstream_repo_copies_skills_and_replaces_existing_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    clone = tmp_path / "clone"
    (target / "old").mkdir(parents=True)
    (target / "old" / "SKILL.md").write_text("# Old\n", encoding="utf-8")

    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        if command[:2] == ["git", "clone"]:
            source = Path(command[-1]) / ".skills" / "new"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("# New\n", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0)
        if command[:2] == ["git", "-C"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr("llm_wiki_installer.upstream_skills.run", fakerun)
    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.command_output",
        lambda _command, fallback="": "abc123",
    )

    assert (
        install_one_upstream_repo(
            "https://example.test/repo", "example/repo", "abc123", target, clone
        )
        == "abc123"
    )
    assert not (target / "old").exists()
    assert (target / "new" / "SKILL.md").read_text(encoding="utf-8") == "# New\n"


def test_install_one_upstream_repo_fails_without_source_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.command_output",
        lambda _command, fallback="": "abc123",
    )

    with pytest.raises(InstallerError, match="has no .skills/ or skills/ directory"):
        install_one_upstream_repo(
            "https://example.test/repo",
            "example/repo",
            "abc123",
            tmp_path / "target",
            tmp_path,
        )


def test_install_one_upstream_repo_fails_without_skill_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        if command[:2] == ["git", "clone"]:
            (Path(command[-1]) / ".skills" / "empty").mkdir(parents=True)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("llm_wiki_installer.upstream_skills.run", fakerun)
    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.command_output",
        lambda _command, fallback="": "abc123",
    )

    with pytest.raises(InstallerError, match="has no discovered SKILL.md files"):
        install_one_upstream_repo(
            "https://example.test/repo",
            "example/repo",
            "abc123",
            tmp_path / "target",
            tmp_path,
        )


def test_install_upstream_skills_records_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_install(
        repo_url: str, repo_slug: str, pinned_commit: str, target: Path, tmp_dir: Path
    ) -> str:
        del repo_slug, tmp_dir
        skill = target / ("ar9av" if "Ar9av" in repo_url else "kepano")
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        assert pinned_commit in {
            "347e85704c52474d13470a3919e4a5cd7e3809cb",
            "553ef99aa3306dd23f268e1ba9af752577684f69",
        }
        return pinned_commit

    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.install_one_upstream_repo", fake_install
    )

    results = install_upstream_skills(tmp_path, ("Ar9av", "kepano"))

    assert results["Ar9av"] == UpstreamInstall(
        "https://github.com/Ar9av/obsidian-wiki",
        "347e85704c52474d13470a3919e4a5cd7e3809cb",
        "347e85704c52474d13470a3919e4a5cd7e3809cb",
        1,
    )
    assert results["kepano"].skill_count == 1
    assert (tmp_path / ".agents/skills/ar9av/SKILL.md").is_file()
    assert (tmp_path / ".agents/skills/kepano/SKILL.md").is_file()


def test_install_upstream_skills_records_skipped_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    stale_skill = tmp_path / ".agents/skills/upstream/kepano/stale/SKILL.md"
    stale_skill.parent.mkdir(parents=True)
    stale_skill.write_text("# Stale\n", encoding="utf-8")

    def fake_install(
        repo_url: str, repo_slug: str, pinned_commit: str, target: Path, tmp_dir: Path
    ) -> str:
        del repo_url, tmp_dir
        skill = target / "skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        calls.append(repo_slug)
        return pinned_commit

    monkeypatch.setattr(
        "llm_wiki_installer.upstream_skills.install_one_upstream_repo", fake_install
    )

    results = install_upstream_skills(tmp_path, ("Ar9av",))

    assert calls == ["Ar9av/obsidian-wiki"]
    assert results["Ar9av"].result == "installed"
    assert results["kepano"] == UpstreamInstall(
        "https://github.com/kepano/obsidian-skills",
        "553ef99aa3306dd23f268e1ba9af752577684f69",
        "skipped",
        0,
        "skipped",
    )
    assert not (tmp_path / ".agents/skills/upstream").exists()


def test_run_install_orchestrates_installer_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    target = tmp_path / "vault"

    monkeypatch.setattr(
        "llm_wiki_installer.installer.source_root", lambda: tmp_path / "source"
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.check_required_tools",
        lambda selected_tools, **_kwargs: calls.append(
            f"tools:{','.join(selected_tools)}"
        ),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.prepare_target",
        lambda _target: calls.append("prepare"),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.install_upstream_skills",
        lambda _target, _selected_skills: {
            "Ar9av": UpstreamInstall(
                "https://example.test/ar9av", "a" * 40, "a" * 40, 1
            ),
            "kepano": UpstreamInstall(
                "https://example.test/kepano", "b" * 40, "b" * 40, 2
            ),
        },
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.write_generated_files",
        lambda _target, _context, force, **_kwargs: calls.append(f"write:{force}"),
    )

    def fakerun(
        command: list[str],
        cwd: Path | None = None,
        capture: bool = False,
        check: bool = True,
        quiet: bool = False,
        error: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, capture, check, quiet, error
        calls.append(" ".join(command))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("llm_wiki_installer.installer.run", fakerun)

    run_install(Options(force=True, target_input=str(target)))

    assert calls == [
        "tools:rg,fzf",
        "prepare",
        "write:True",
        "bash .scripts/postrun.sh",
        "bash .scripts/check-index-log.sh",
        "git --no-pager diff --stat",
    ]
    assert target.is_dir()


def test_generated_review_commands_disable_git_pager(
    template_context: dict[str, str],
) -> None:
    postrun = render_template("postrun.sh", template_context)
    readme = render_template("README.md", template_context)
    agents = render_template("AGENTS.md", template_context)

    assert "git --no-pager diff --stat || true" in postrun
    assert "git --no-pager diff --stat" in readme
    assert "git --no-pager diff" in readme
    assert "bash .scripts/postrun.sh" in agents
    assert "git diff" not in agents


def test_generated_postrun_is_limited_to_hard_boundaries(
    template_context: dict[str, str],
) -> None:
    postrun = render_template("postrun.sh", template_context)

    assert "ALLOW_RAW_CHANGE" in postrun
    assert ".codex/rules" in postrun
    assert "Required Obsidian plugin asset missing" not in postrun
    assert "Unauthorized SKILL.md" not in postrun
    assert "kebab-case" not in postrun


def test_generated_check_index_log_scopes_hard_failures_to_structure(
    template_context: dict[str, str],
) -> None:
    check = render_template("check-index-log.sh", template_context)

    assert "new wiki pages were added but wiki/index.md was not updated." in check
    assert "deleted, moved, renamed, or copied" in check
    assert "WARNING: agent-generated" in check
    assert '"type"' not in check
    assert "raw/ changed" not in check


def test_generated_claude_bridge_imports_agents_policy(
    template_context: dict[str, str],
) -> None:
    claude = render_template("CLAUDE.md", template_context)

    assert "@AGENTS.md" in claude


def test_generated_codex_hooks_run_vault_checks(
    template_context: dict[str, str],
) -> None:
    hooks = json.loads(render_template("codex-hooks.json", template_context))

    stop_hooks = hooks["hooks"]["Stop"][0]["hooks"]
    assert stop_hooks[0]["type"] == "command"
    assert stop_hooks[0]["command"] == "bash .scripts/check-index-log.sh"


def test_generated_tag_policy_removes_frontmatter_type(
    template_context: dict[str, str],
) -> None:
    agents = render_template("AGENTS.md", template_context)
    workflow_schema = render_template("schema/workflow.md", template_context)
    wiki_page_schema = render_template("schema/wiki-page.md", template_context)
    tags = render_template("wiki-tags.md", template_context)

    assert "type: source | entity" not in agents
    assert "type: map" not in agents
    assert "tags: []" not in agents
    assert "wiki/tags.md" in agents
    assert "kebab-case" in agents
    assert "nested slash tags" not in agents
    assert "add it\nto `wiki/tags.md`" not in agents

    assert "wiki/tags.md" in workflow_schema
    assert "kebab-case" in workflow_schema
    assert "nested slash tags" not in workflow_schema
    assert "add it to `wiki/tags.md`" in workflow_schema

    assert "type: source | entity" not in wiki_page_schema
    assert "tags: []" in wiki_page_schema
    assert "wiki/tags.md" in wiki_page_schema
    assert "kebab-case" in wiki_page_schema
    assert "nested slash tags" in wiki_page_schema
    assert "add it\nto `wiki/tags.md`" in wiki_page_schema

    assert "type: source | entity" not in tags
    assert "Use flat tags only; do not use nested tags with `/`." in tags
    assert "Use `kebab-case`" in tags
    assert "type/source" in tags
    assert "model-evaluation" in tags


def test_generated_log_schema_uses_progressive_disclosure(
    template_context: dict[str, str],
) -> None:
    agents = render_template("AGENTS.md", template_context)
    log_schema = render_template("schema/log.md", template_context)

    assert (
        "Use `schema/log.md` for `wiki/log.jsonl` event schemas and examples." in agents
    )
    assert '"type":"ingest"' not in agents
    assert '"type":"schema-update"' not in agents
    assert "# Log Schema" in log_schema
    assert '"type":"ingest"' in log_schema
    assert '"type":"schema-update"' in log_schema


def test_generated_page_templates_use_progressive_disclosure(
    template_context: dict[str, str],
) -> None:
    agents = render_template("AGENTS.md", template_context)
    workflow_schema = render_template("schema/workflow.md", template_context)
    wiki_page_schema = render_template("schema/wiki-page.md", template_context)
    map_schema = render_template("schema/map.md", template_context)

    assert "Use `schema/workflow.md`" in agents
    assert "Use `schema/wiki-page.md`" in agents
    assert "Use `schema/map.md`" in agents
    assert "## Default workflow" not in agents
    assert "## Wiki page template" not in agents
    assert "## Map template" not in agents
    assert "source: `raw/path/to/source`" not in agents
    assert "## Related Outputs" not in agents

    assert "## Default workflow" in workflow_schema
    assert ".agents/skills/<skill-name>/SKILL.md" in workflow_schema

    assert "# Wiki Page Schema" in wiki_page_schema
    assert "source: `raw/path/to/source`" in wiki_page_schema
    assert "# Map Schema" in map_schema
    assert "## Related Outputs" in map_schema


def test_run_install_with_no_selected_tools(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    target = tmp_path / "vault"

    monkeypatch.setattr(
        "llm_wiki_installer.installer.source_root", lambda: tmp_path / "source"
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.select_dependency_tools", lambda _interactive: ()
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.select_upstream_skills", lambda _interactive: ()
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.check_required_tools",
        lambda selected_tools, **_kwargs: calls.append(
            f"tools:{','.join(selected_tools)}"
        ),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.prepare_target",
        lambda _target: calls.append("prepare"),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.install_upstream_skills",
        lambda _target, _selected_skills: {
            "Ar9av": UpstreamInstall(
                "https://example.test/ar9av", "a" * 40, "skipped", 0, "skipped"
            ),
            "kepano": UpstreamInstall(
                "https://example.test/kepano", "b" * 40, "skipped", 0, "skipped"
            ),
        },
    )
    monkeypatch.setattr(
        "llm_wiki_installer.installer.write_generated_files",
        lambda _target, _context, force, **_kwargs: calls.append(f"write:{force}"),
    )

    def fakerun(
        command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        calls.append(" ".join(command))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("llm_wiki_installer.installer.run", fakerun)

    run_install(Options(force=False, target_input=str(target), interactive=False))

    assert calls[:3] == ["tools:", "prepare", "write:False"]
