from __future__ import annotations

import sys
import termios
import tty
from contextlib import contextmanager
from typing import Iterator, Sequence, TextIO, cast

from .errors import InstallerError


def select_options(
    title: str, options: Sequence[tuple[str, str, str]], interactive: bool
) -> tuple[str, ...]:
    if not interactive or not can_prompt():
        return tuple(key for key, _, _ in options)
    return prompt_multiselect(title, options)


def can_prompt() -> bool:
    return sys.stdout.isatty() and stream_or_tty_available(sys.stdin, "r")


def stream_or_tty_available(stream: TextIO, mode: str) -> bool:
    if stream.isatty():
        return True
    try:
        with open("/dev/tty", mode, encoding="utf-8"):
            return True
    except OSError:
        return False


@contextmanager
def prompt_stream(stream: TextIO, mode: str) -> Iterator[TextIO]:
    if stream.isatty():
        yield stream
        return
    with open("/dev/tty", mode, encoding="utf-8", buffering=1) as tty_stream:
        yield cast(TextIO, tty_stream)


def prompt_multiselect(
    title: str, options: Sequence[tuple[str, str, str]]
) -> tuple[str, ...]:
    selected = {key for key, _, _ in options}
    cursor = 0
    line_count = len(options) + 4
    first_render = True

    with (
        prompt_stream(sys.stdin, "r") as input_stream,
        prompt_stream(sys.stdout, "w") as output_stream,
    ):
        while True:
            if not first_render:
                output_stream.write(f"\x1b[{line_count}A")
            first_render = False
            render_multiselect(title, options, selected, cursor, output_stream)

            key = read_key(input_stream)
            if key in ("\r", "\n"):
                break
            if key == "\x03":
                raise InstallerError("installation cancelled.")
            cursor, selected = apply_multiselect_key(key, options, cursor, selected)

        output_stream.write("\n")
        output_stream.flush()
    return tuple(key for key, _, _ in options if key in selected)


def render_multiselect(
    title: str,
    options: Sequence[tuple[str, str, str]],
    selected: set[str],
    cursor: int,
    output_stream: TextIO | None = None,
) -> None:
    stream = output_stream or sys.stdout
    lines = [
        title,
        "Use Up/Down to move, Space to toggle, Enter to continue. Default: all selected.",
        "",
    ]
    for index, (key, label, description) in enumerate(options):
        pointer = ">" if index == cursor else " "
        marker = "x" if key in selected else " "
        lines.append(f"{pointer} [{marker}] {label} - {description}")
    lines.append("")

    for line in lines:
        stream.write(f"\x1b[2K{line}\n")
    stream.flush()


def read_key(input_stream: TextIO | None = None) -> str:
    stream = input_stream or sys.stdin
    fd = stream.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = stream.read(1)
        if key == "\x1b":
            key += stream.read(2)
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def apply_multiselect_key(
    key: str,
    options: Sequence[tuple[str, str, str]],
    cursor: int,
    selected: set[str],
) -> tuple[int, set[str]]:
    next_selected = set(selected)
    if key in ("\x1b[A", "k"):
        return ((cursor - 1) % len(options), next_selected)
    if key in ("\x1b[B", "j"):
        return ((cursor + 1) % len(options), next_selected)
    if key == " ":
        option_key = options[cursor][0]
        if option_key in next_selected:
            next_selected.remove(option_key)
        else:
            next_selected.add(option_key)
    return (cursor, next_selected)
