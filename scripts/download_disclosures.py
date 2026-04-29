"""Download bank General Disclosure Statement PDFs.

Downloads all confirmed disclosure statement PDFs for each bank configured in
``config/sources.yaml``.  For every PDF a sidecar metadata file is written
alongside it, recording provenance for debugging and auditing:

  ``data/raw/financial_disclosures/<bank_id>/<bank_id>-disclosure-<period_end>.pdf``
  ``data/raw/financial_disclosures/<bank_id>/<bank_id>-disclosure-<period_end>.meta.json``

The script is **idempotent**: if a PDF already exists and its SHA-256 checksum
matches the value in the sidecar file, the download is skipped.  Pass
``--force`` to re-download all files regardless.

For PDFs that were placed manually (e.g. downloaded on a local machine because
the server blocks cloud IPs), run with ``--backfill-metadata`` to generate the
sidecar without re-downloading.  The ``source_url`` is read from
``config/sources.yaml``; ``downloaded_at`` is set to the file's modification
time.

Usage::

    python scripts/download_disclosures.py [--force] [--bank <bank_id>]
    python scripts/download_disclosures.py --backfill-metadata [--bank <bank_id>]

Exit codes
----------
0 — all downloads succeeded (or were already present / backfilled)
1 — one or more downloads failed (partial success is allowed)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml

from src.logger import get_logger

logger = get_logger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_CONFIG_PATH = Path("config/sources.yaml")
_OUTPUT_ROOT = Path("data/raw/financial_disclosures")
_DOWNLOAD_TIMEOUT = 180


def load_banks() -> list[dict[str, Any]]:
    """Return bank configs from ``config/sources.yaml``."""
    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg["financial_disclosures"]["banks"]


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 digest of the file at *path*."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_path_for(bank_id: str, period_end: str) -> Path:
    """Return the expected local PDF path for the given bank and period."""
    return _OUTPUT_ROOT / bank_id / f"{bank_id}-disclosure-{period_end}.pdf"


def meta_path_for(bank_id: str, period_end: str) -> Path:
    """Return the expected sidecar metadata path for the given bank and period."""
    return _OUTPUT_ROOT / bank_id / f"{bank_id}-disclosure-{period_end}.meta.json"


def read_meta(meta_path: Path) -> dict[str, Any] | None:
    """Return the sidecar metadata dict, or ``None`` if the file does not exist."""
    if not meta_path.exists():
        return None
    with meta_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_meta(
    meta_path: Path,
    *,
    bank_id: str,
    bank_name: str,
    period_end: str,
    period_type: str,
    source_url: str,
    downloaded_at: str,
    file_size_bytes: int,
    sha256: str,
) -> None:
    """Write provenance metadata alongside a downloaded PDF."""
    meta: dict[str, Any] = {
        "bank_id": bank_id,
        "bank_name": bank_name,
        "period_end": period_end,
        "period_type": period_type,
        "source_url": source_url,
        "downloaded_at": downloaded_at,
        "file_size_bytes": file_size_bytes,
        "sha256": sha256,
    }
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    logger.info("Metadata written to %s", meta_path)


def download_pdf(url: str, dest: Path) -> None:
    """Download *url* to *dest* using a browser User-Agent.

    Raises
    ------
    RuntimeError
        On HTTP error (non-200 response).
    requests.exceptions.RequestException
        On network failure.
    """
    logger.info("Downloading %s → %s", url, dest)
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})
    response = session.get(url, timeout=_DOWNLOAD_TIMEOUT, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code} for {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        for chunk in response.iter_content(chunk_size=65536):
            fh.write(chunk)
    logger.info("Saved %d bytes to %s", dest.stat().st_size, dest)


def _is_fresh(pdf: Path, meta: dict[str, Any]) -> bool:
    """Return True if *pdf* exists and its checksum matches the sidecar."""
    if not pdf.exists():
        return False
    return sha256_file(pdf) == meta.get("sha256", "")


def download_bank(
    bank: dict[str, Any],
    *,
    force: bool = False,
) -> tuple[int, int]:
    """Download all confirmed reports for *bank*.

    Returns
    -------
    (ok, failed)
        Counts of successful and failed downloads.
    """
    bank_id = bank["id"]
    bank_name = bank.get("rbnz_entity_name", bank_id)
    confirmed = [r for r in bank.get("reports", []) if r.get("status") == "confirmed"]
    if not confirmed:
        logger.info("%s: no confirmed reports — skipping", bank_id)
        return 0, 0

    ok = failed = 0
    for report in confirmed:
        period_end = str(report["period_end"])
        period_type = str(report.get("period_type", ""))
        url = report["url"]

        pdf = pdf_path_for(bank_id, period_end)
        meta_p = meta_path_for(bank_id, period_end)
        existing_meta = read_meta(meta_p)

        if not force and existing_meta and _is_fresh(pdf, existing_meta):
            logger.info(
                "%s %s: already present and checksum matches — skipping",
                bank_id,
                period_end,
            )
            ok += 1
            continue

        try:
            download_pdf(url, pdf)
        except Exception as exc:
            logger.warning("%s %s: download failed — %s", bank_id, period_end, exc)
            failed += 1
            continue

        checksum = sha256_file(pdf)
        downloaded_at = datetime.now(UTC).isoformat()
        write_meta(
            meta_p,
            bank_id=bank_id,
            bank_name=bank_name,
            period_end=period_end,
            period_type=period_type,
            source_url=url,
            downloaded_at=downloaded_at,
            file_size_bytes=pdf.stat().st_size,
            sha256=checksum,
        )
        ok += 1

    return ok, failed


def backfill_bank_metadata(bank: dict[str, Any]) -> tuple[int, int]:
    """Generate sidecar metadata for manually-placed PDFs that have no sidecar.

    This is useful for PDFs that were downloaded on a local machine because the
    server blocks cloud/CI IP ranges.  The ``source_url`` is read from
    ``config/sources.yaml``; ``downloaded_at`` is derived from the file's
    modification time.

    Parameters
    ----------
    bank:
        Bank configuration dict from ``config/sources.yaml``.

    Returns
    -------
    (backfilled, skipped)
        Count of sidecars written and PDFs already having a valid sidecar.
    """
    bank_id = bank["id"]
    bank_name = bank.get("rbnz_entity_name", bank_id)
    all_reports = bank.get("reports", [])

    # Build a lookup from period_end → report config for url / period_type
    report_lookup: dict[str, dict[str, Any]] = {str(r["period_end"]): r for r in all_reports}

    bank_dir = _OUTPUT_ROOT / bank_id
    if not bank_dir.is_dir():
        return 0, 0

    backfilled = skipped = 0
    for pdf in sorted(bank_dir.glob(f"{bank_id}-disclosure-*.pdf")):
        # Derive period_end from filename: <bank_id>-disclosure-<period_end>.pdf
        stem = pdf.stem  # e.g. "anz-disclosure-2024-09-30"
        period_end = stem[len(f"{bank_id}-disclosure-") :]

        meta_p = meta_path_for(bank_id, period_end)
        existing_meta = read_meta(meta_p)
        if existing_meta and _is_fresh(pdf, existing_meta):
            logger.info(
                "%s %s: sidecar already valid — skipping",
                bank_id,
                period_end,
            )
            skipped += 1
            continue

        report = report_lookup.get(period_end, {})
        source_url = report.get("url", "")
        period_type = str(report.get("period_type", ""))

        # Use file mtime as a proxy for download time
        mtime = datetime.fromtimestamp(pdf.stat().st_mtime, tz=UTC)
        downloaded_at = mtime.isoformat()

        checksum = sha256_file(pdf)
        write_meta(
            meta_p,
            bank_id=bank_id,
            bank_name=bank_name,
            period_end=period_end,
            period_type=period_type,
            source_url=source_url,
            downloaded_at=downloaded_at,
            file_size_bytes=pdf.stat().st_size,
            sha256=checksum,
        )
        logger.info("%s %s: sidecar backfilled", bank_id, period_end)
        backfilled += 1

    return backfilled, skipped


def main(argv: list[str] | None = None) -> int:
    """Entry point: download all confirmed disclosure statement PDFs.

    Returns
    -------
    0
        All downloads succeeded (or were already present / backfilled).
    1
        One or more downloads failed.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download PDFs even if already present and checksum matches.",
    )
    parser.add_argument(
        "--bank",
        metavar="BANK_ID",
        help="Only download reports for the specified bank ID.",
    )
    parser.add_argument(
        "--backfill-metadata",
        action="store_true",
        help=(
            "Generate sidecar .meta.json files for PDFs that were placed manually "
            "(e.g. downloaded locally because the server blocks cloud IPs). "
            "Does not attempt any network download."
        ),
    )
    args = parser.parse_args(argv)

    banks = load_banks()
    if args.bank:
        banks = [b for b in banks if b["id"] == args.bank]
        if not banks:
            logger.error("No bank found with id %r", args.bank)
            return 1

    if args.backfill_metadata:
        total_backfilled = total_skipped = 0
        for bank in banks:
            backfilled, skipped = backfill_bank_metadata(bank)
            total_backfilled += backfilled
            total_skipped += skipped
        logger.info(
            "Backfill complete: %d sidecars written, %d already valid",
            total_backfilled,
            total_skipped,
        )
        return 0

    total_ok = total_failed = 0
    for bank in banks:
        ok, failed = download_bank(bank, force=args.force)
        total_ok += ok
        total_failed += failed

    if total_failed:
        logger.error("Download complete: %d succeeded, %d failed", total_ok, total_failed)
        return 1

    logger.info("Download complete: %d succeeded, %d failed", total_ok, total_failed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
