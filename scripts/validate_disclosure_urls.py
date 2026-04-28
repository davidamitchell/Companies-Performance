"""Validate disclosure statement URLs in config/sources.yaml.

For every report entry in the ``financial_disclosures`` section this script
performs an HTTP HEAD request and updates the ``status`` field:

- ``confirmed``    — server returned HTTP 200
- ``not_found``    — server returned HTTP 4xx / 5xx
- ``not_reachable``— connection error or timeout (YAML status left as ``pending``)

A JSON results file is written to
``data/raw/financial_disclosures/url_validation.json``.

Usage::

    python scripts/validate_disclosure_urls.py

Exit code is 0 regardless of URL resolution outcomes.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml

from src.logger import get_logger

logger = get_logger(__name__)

_USER_AGENT = "Companies-Performance/1.0 (github.com/davidamitchell/Companies-Performance)"
_TIMEOUT = 10
_RESULTS_PATH = Path("data/raw/financial_disclosures/url_validation.json")
_SOURCES_PATH = Path("config/sources.yaml")


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _dump_yaml(data: Any, path: Path) -> None:
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _check_url(session: requests.Session, url: str) -> tuple[int | None, str]:
    """Perform an HTTP HEAD request and return (http_status, resolved_status).

    resolved_status is one of ``confirmed``, ``not_found``, or ``not_reachable``.
    """
    try:
        response = session.head(url, timeout=_TIMEOUT, allow_redirects=True)
        http_status: int | None = response.status_code
        if response.status_code == 200:
            resolved_status = "confirmed"
        else:
            resolved_status = "not_found"
            logger.warning("Non-200 response %d for %s", response.status_code, url)
    except requests.exceptions.ConnectionError as exc:
        logger.warning("Connection error for %s: %s", url, exc)
        http_status = None
        resolved_status = "not_reachable"
    except requests.exceptions.Timeout as exc:
        logger.warning("Timeout for %s: %s", url, exc)
        http_status = None
        resolved_status = "not_reachable"
    except requests.exceptions.RequestException as exc:
        logger.warning("Request error for %s: %s", url, exc)
        http_status = None
        resolved_status = "not_reachable"

    return http_status, resolved_status


def main() -> int:
    """Validate all disclosure URLs and write results."""
    logging.basicConfig(level=logging.INFO)

    sources = _load_yaml(_SOURCES_PATH)
    banks: list[dict[str, Any]] = sources.get("financial_disclosures", {}).get("banks", [])

    if not banks:
        logger.warning("No banks found under financial_disclosures in %s", _SOURCES_PATH)
        return 0

    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})

    results: list[dict[str, Any]] = []
    total = confirmed = not_found = not_reachable = 0

    for bank in banks:
        bank_id: str = bank.get("id", "unknown")
        for report in bank.get("reports", []):
            url: str = report["url"]
            period_end: str = report["period_end"]
            period_type: str = report["period_type"]

            logger.info("Checking %s %s %s", bank_id, period_end, url)
            http_status, resolved_status = _check_url(session, url)
            total += 1

            if resolved_status == "confirmed":
                confirmed += 1
                report["status"] = "confirmed"
            elif resolved_status == "not_found":
                not_found += 1
                report["status"] = "not_found"
            else:
                not_reachable += 1
                # Leave YAML status as-is (do not overwrite pending with not_reachable)

            results.append(
                {
                    "bank_id": bank_id,
                    "period_end": period_end,
                    "period_type": period_type,
                    "url": url,
                    "http_status": http_status,
                    "resolved_status": resolved_status,
                }
            )

    # Write updated YAML back (preserves structure but not inline comments)
    _dump_yaml(sources, _SOURCES_PATH)
    logger.info("Updated %s", _SOURCES_PATH)

    # Write JSON results
    _RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "validated_at": datetime.now(tz=UTC).isoformat(),
        "results": results,
    }
    _RESULTS_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    logger.info("Wrote validation results to %s", _RESULTS_PATH)

    print(
        f"\nURL validation complete: {total} checked, "
        f"{confirmed} confirmed, {not_found} not_found, {not_reachable} not_reachable"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
