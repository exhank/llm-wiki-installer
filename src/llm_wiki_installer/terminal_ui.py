from __future__ import annotations

import sys
import termios
import tty
from typing import Sequence

from .errors import InstallerError


def select_options(
    title: str, options: Sequence[tuple[str, str, str]], interactive: bool
) -> tuple[str, ...]:
    if not interactive or not can_prompt():
        return tuple(key for key, _, _ in options)
    return prompt_multiselect(title, options)


def can_prompt() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def prompt_multiselect(
    title: str, options: Sequence[tuple[str, str, str]]
) -> tuple[str, ...]:
    selected = {key for key, _, _ in options}
    cursor = 0
    line_count = len(options) + 4
    first_render = True

    while True:
        if not first_render:
            sys.stdout.write(f"\x1b[{line_count}A")
        first_render = False
        render_multiselect(title, options, selected, cursor)

        key = read_key()
        if key in ("\r", "\n"):
            break
        if key == "\x03":
            raise InstallerError("installation cancelled.")
        cursor, selected = apply_multiselect_key(key, options, cursor, selected)

    sys.stdout.write("\n")
    sys.stdout.flush()
    return tuple(key for key, _, _ in options if key in selected)


def render_multiselect(
    title: str,
    options: Sequence[tuple[str, str, str]],
    selected: set[str],
    cursor: int,
) -> None:
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
        sys.stdout.write(f"\x1b[2K{line}\n")
    sys.stdout.flush()


def read_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":
            key += sys.stdin.read(2)
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
