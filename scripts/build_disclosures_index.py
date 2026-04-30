"""Build docs/data/processed/disclosures.json from .meta.json sidecars.

Reads every <bank_id>/*.meta.json file under data/raw/financial_disclosures/
and writes a single JSON array to docs/data/processed/disclosures.json, sorted
by (bank_id, period_end).  The output is consumed by docs/disclosures.html.

Usage:
    python scripts/build_disclosures_index.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw" / "financial_disclosures"
OUT_PATH = ROOT / "docs" / "data" / "processed" / "disclosures.json"


def load_sidecars(raw_dir: Path) -> list[dict]:
    """Return a list of sidecar dicts, sorted by (bank_id, period_end).

    Internal fields (source_url, sha256, downloaded_at, file_size_bytes) are
    stripped — only public coverage metadata is included in the frontend JSON.
    """
    _internal_fields = {"source_url", "sha256", "downloaded_at", "file_size_bytes"}
    records: list[dict] = []
    for sidecar in sorted(raw_dir.glob("**/*.meta.json")):
        try:
            data = json.loads(sidecar.read_text())
        except json.JSONDecodeError as exc:
            logger.warning("skipping malformed sidecar %s: %s", sidecar, exc)
            continue
        public = {k: v for k, v in data.items() if k not in _internal_fields}
        records.append(public)
        logger.info("loaded %s / %s", data.get("bank_id"), data.get("period_end"))

    records.sort(key=lambda r: (r.get("bank_id", ""), r.get("period_end", "")))
    return records


def write_index(records: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, indent=2) + "\n")
    logger.info("wrote %d records to %s", len(records), out_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_DIR,
        help="Root directory containing per-bank sidecar files",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_PATH,
        help="Output JSON path",
    )
    args = parser.parse_args(argv)

    records = load_sidecars(args.raw_dir)
    if not records:
        logger.error("no sidecar files found under %s", args.raw_dir)
        return 1

    write_index(records, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
