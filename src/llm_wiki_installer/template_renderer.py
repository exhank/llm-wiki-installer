from __future__ import annotations

import re
from importlib import resources
from typing import Mapping


def render_template(name: str, context: Mapping[str, str]) -> str:
    template = (
        resources.files(__package__)
        .joinpath("templates")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )
    rendered = template

    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", value)

    unresolved = sorted(set(re.findall(r"{{[A-Z0-9_]+}}", rendered)))
    if unresolved:
        raise ValueError(
            f"unresolved template tokens in {name}: {', '.join(unresolved)}"
        )

    return rendered
