from __future__ import annotations

import builtins
from contextlib import nullcontext

import pytest

from llm_wiki_installer.errors import InstallerError
from llm_wiki_installer.terminal_ui import (
    apply_multiselect_key,
    can_prompt,
    prompt_multiselect,
    read_key,
    render_multiselect,
    select_options,
)


def test_select_options_defaults_to_all_when_not_interactive() -> None:
    options = (
        ("one", "One", "First option"),
        ("two", "Two", "Second option"),
    )

    assert select_options("Pick", options, interactive=False) == ("one", "two")


def test_select_options_honors_explicit_defaults_when_not_interactive() -> None:
    options = (
        ("one", "One", "First option"),
        ("two", "Two", "Second option"),
    )

    assert select_options(
        "Pick", options, interactive=False, default_keys=("two",)
    ) == ("two",)


def test_select_options_delegates_to_prompt_when_interactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    options = (("one", "One", "First option"),)
    monkeypatch.setattr("llm_wiki_installer.terminal_ui.can_prompt", lambda: True)
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.prompt_multiselect",
        lambda _title, _options, _defaults: ("one",),
    )

    assert select_options("Pick", options, interactive=True) == ("one",)


def test_can_prompt_requires_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeStream:
        def __init__(self, tty: bool) -> None:
            self.tty = tty

        def isatty(self) -> bool:
            return self.tty

    monkeypatch.setattr("llm_wiki_installer.terminal_ui.sys.stdin", FakeStream(True))
    monkeypatch.setattr("llm_wiki_installer.terminal_ui.sys.stdout", FakeStream(False))
    monkeypatch.setattr(
        builtins,
        "open",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("no tty")),
    )

    assert not can_prompt()


def test_can_prompt_uses_dev_tty_for_piped_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeStream:
        def __init__(self, tty: bool) -> None:
            self.tty = tty

        def isatty(self) -> bool:
            return self.tty

    class FakeTty:
        def __enter__(self) -> "FakeTty":
            return self

        def __exit__(self, *_exc: object) -> None:
            return None

    opened: list[tuple[str, str]] = []

    def fake_open(path: str, mode: str, **_kwargs: object) -> FakeTty:
        opened.append((path, mode))
        return FakeTty()

    monkeypatch.setattr("llm_wiki_installer.terminal_ui.sys.stdin", FakeStream(False))
    monkeypatch.setattr("llm_wiki_installer.terminal_ui.sys.stdout", FakeStream(True))
    monkeypatch.setattr(builtins, "open", fake_open)

    assert can_prompt()
    assert opened == [("/dev/tty", "r")]


def test_prompt_multiselect_toggles_and_accepts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    keys = iter((" ", "\r"))
    options = (
        ("one", "One", "First option"),
        ("two", "Two", "Second option"),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.prompt_stream",
        lambda stream, _mode: nullcontext(stream),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.read_key", lambda *_args: next(keys)
    )

    assert prompt_multiselect("Pick", options) == ("two",)
    assert "Use Up/Down to move" in capsys.readouterr().out


def test_prompt_multiselect_starts_from_default_selection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    options = (
        ("one", "One", "First option"),
        ("two", "Two", "Second option"),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.prompt_stream",
        lambda stream, _mode: nullcontext(stream),
    )
    monkeypatch.setattr("llm_wiki_installer.terminal_ui.read_key", lambda *_args: "\r")

    assert prompt_multiselect("Pick", options, default_keys=("two",)) == ("two",)
    rendered = capsys.readouterr().out
    assert "[ ] One" in rendered
    assert "[x] Two" in rendered


def test_prompt_multiselect_reports_cancel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.prompt_stream",
        lambda stream, _mode: nullcontext(stream),
    )
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.read_key", lambda *_args: "\x03"
    )

    with pytest.raises(InstallerError, match="installation cancelled"):
        prompt_multiselect("Pick", (("one", "One", "First option"),))


def test_render_multiselect_marks_cursor_and_selection(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_multiselect(
        "Pick",
        (("one", "One", "First option"), ("two", "Two", "Second option")),
        {"two"},
        1,
    )

    rendered = capsys.readouterr().out
    assert "  [ ] One - First option" in rendered
    assert "> [x] Two - Second option" in rendered


def test_read_key_reads_escape_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeStdin:
        def __init__(self) -> None:
            self.chars = iter(("\x1b", "[", "A"))

        def fileno(self) -> int:
            return 9

        def read(self, size: int) -> str:
            return "".join(next(self.chars) for _ in range(size))

    setraw_calls: list[int] = []
    setattrs: list[object] = []

    monkeypatch.setattr("llm_wiki_installer.terminal_ui.sys.stdin", FakeStdin())
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.termios.tcgetattr", lambda fd: ["old", fd]
    )
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.tty.setraw", setraw_calls.append
    )
    monkeypatch.setattr(
        "llm_wiki_installer.terminal_ui.termios.tcsetattr",
        lambda fd, when, settings: setattrs.extend([fd, when, settings]),
    )

    assert read_key() == "\x1b[A"
    assert setraw_calls == [9]
    assert setattrs[0] == 9


def test_apply_multiselect_key_moves_and_toggles_selection() -> None:
    options = (
        ("one", "One", "First option"),
        ("two", "Two", "Second option"),
    )

    cursor, selected = apply_multiselect_key("\x1b[B", options, 0, {"one", "two"})
    assert cursor == 1
    assert selected == {"one", "two"}

    cursor, selected = apply_multiselect_key(" ", options, cursor, selected)
    assert cursor == 1
    assert selected == {"one"}

    cursor, selected = apply_multiselect_key("\x1b[A", options, cursor, selected)
    assert cursor == 0
    assert selected == {"one"}

    cursor, selected = apply_multiselect_key(" ", options, cursor, set())
    assert cursor == 0
    assert selected == {"one"}
