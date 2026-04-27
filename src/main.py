"""CLI entry point for the Companies Performance pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from src.config import load_sources
from src.ingestion.fetch import download_file
from src.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_RAW_DIR = Path(__file__).parent.parent / "data" / "raw"


def main() -> None:
    """Main entry point.

    Parses command-line arguments and dispatches to the appropriate subcommand.
    Exits non-zero on any error.
    """
    parser = argparse.ArgumentParser(
        prog="companies-performance",
        description="Companies Performance data pipeline",
    )
    subparsers = parser.add_subparsers(dest="command")

    _register_fetch_subparser(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    logger.info("command=%s", args.command)

    if args.command == "fetch":
        _dispatch_fetch(args)


def _register_fetch_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``fetch`` sub-command and its children."""
    fetch_parser: argparse.ArgumentParser = subparsers.add_parser(
        "fetch", help="Fetch raw data files from configured sources"
    )
    fetch_sub = fetch_parser.add_subparsers(dest="fetch_command")

    rbnz = fetch_sub.add_parser("rbnz", help="Download the RBNZ XLSX source file(s)")
    rbnz.add_argument(
        "--dest",
        metavar="PATH",
        default=None,
        help=(
            "Override the output file path. "
            "Defaults to the path declared in config/sources.yaml (output_file), "
            "or data/raw/<name>.xlsx if output_file is absent."
        ),
    )
    rbnz.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be downloaded without actually downloading.",
    )


def _dispatch_fetch(args: argparse.Namespace) -> None:
    """Dispatch parsed ``fetch`` args to the correct handler."""
    cmd = getattr(args, "fetch_command", None)
    if cmd == "rbnz":
        _fetch_rbnz(args)
    else:
        print("Usage: companies-performance fetch <rbnz>", file=sys.stderr)
        sys.exit(1)


def _fetch_rbnz(args: argparse.Namespace) -> None:
    """Download RBNZ XLSX source file(s) declared in ``config/sources.yaml``.

    Parameters
    ----------
    args:
        Parsed argument namespace.  Relevant attributes:

        - ``dest`` — optional override for the output file path.
        - ``dry_run`` — when ``True``, log intent but skip the download.
    """
    try:
        config: dict[str, Any] = load_sources()
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Failed to load sources config: %s", exc)
        sys.exit(1)

    rbnz_cfg: dict[str, Any] = config.get("rbnz") or {}
    sources: list[dict[str, Any]] = rbnz_cfg.get("xlsx_sources") or []

    if not sources:
        logger.error("No rbnz.xlsx_sources found in config/sources.yaml")
        sys.exit(1)

    raw_dir = _DEFAULT_RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)

    dest_override: str | None = getattr(args, "dest", None)
    dry_run: bool = getattr(args, "dry_run", False)

    for source in sources:
        url: str = source["url"]
        name: str = source["name"]

        if dest_override is not None:
            dest = Path(dest_override)
        elif "output_file" in source:
            dest = Path(source["output_file"])
        else:
            safe_name = name.lower().replace(" ", "-")
            dest = raw_dir / f"{safe_name}.xlsx"

        dest.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            logger.info("[dry-run] Would download %s -> %s", url, dest)
            print(f"[dry-run] {url} -> {dest}")
            continue

        logger.info("Fetching '%s'", name)
        try:
            download_file(url, dest)
        except Exception as exc:
            logger.error("Failed to download '%s' from %s: %s", name, url, exc)
            sys.exit(1)


if __name__ == "__main__":
    main()
