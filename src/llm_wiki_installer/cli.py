from __future__ import annotations

import sys
from typing import Optional

from .errors import InstallerError
from .install_options import parse_options
from .installer import run_install


def main(argv: Optional[list[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    try:
        options = parse_options(args)
        if options.show_help:
            print(options.usage)
            return 0

        run_install(options)
        return 0
    except InstallerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
