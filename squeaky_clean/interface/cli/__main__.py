"""Squeaky Clean CLI entrypoint: enables ``python -m squeaky_clean.interface.cli``."""

import sys
from pathlib import Path

from squeaky_clean.infrastructure.config.env_loader import EnvLoader
from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser
from squeaky_clean.interface.cli.squeaky_clean_cli import SqueakyCleanCLI


def main() -> int:
    # Load .env from cwd or repo root if present; both are best-effort.
    for candidate in (Path.cwd() / ".env",
                      Path(__file__).resolve().parents[3].parent / ".env"):
        if candidate.is_file():
            EnvLoader(candidate).load()
            break
    args = CLIArgsParser().parse(sys.argv[1:])
    return SqueakyCleanCLI().run(args)


if __name__ == "__main__":
    raise SystemExit(main())
