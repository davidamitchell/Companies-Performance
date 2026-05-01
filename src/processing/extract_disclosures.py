"""Extract quantitative metrics from bank disclosure PDFs.

Processing layer responsibility: open raw PDFs, extract text with pdfplumber,
match metric patterns, normalise values, and return canonical rows in the schema:

    entity  — institution name matching RBNZ entity (e.g. "Kiwibank")
    metric  — canonical metric name from glossary (e.g. "Net Interest Income")
    value   — numeric value in NZDm, or percentage for capital ratios
    period  — quarter string derived from period_end in meta.json (e.g. "2024-Q2")
    source  — "disclosure-{bank_id}" (e.g. "disclosure-kiwibank")

Only PDFs with a matching ``.meta.json`` sidecar are processed.  PDFs without
a sidecar are skipped with a WARNING.

Unit normalisation:
- Text containing "$ millions", "NZ$m", "NZDm" → values already in NZDm (scale = 1.0)
- Text containing "$'000", "$000", "NZD thousand", "thousands" → divide by 1000

Capital ratio extraction uses percentage detection (second ``%`` value on the line
is the current-period ratio; the first is the minimum regulatory requirement).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pdfplumber  # type: ignore[import-untyped]

from src.logger import get_logger
from src.processing.parse import _to_quarter

logger = get_logger(__name__)

_SOURCE_PREFIX = "disclosure"

# ── Metric patterns ──────────────────────────────────────────────────────────
# Tuples of (canonical_name, [regex patterns], extraction_strategy)
# extraction_strategy: "first_value" | "second_pct"
_INCOME_METRICS: list[tuple[str, list[str], str]] = [
    ("Net Interest Income", [r"net interest income\b"], "first_value"),
    (
        "Total Operating Income",
        [r"total operating income\b", r"^operating income\b"],
        "first_value",
    ),
    ("Operating Expenses", [r"operating expenses?\b"], "first_value"),
    (
        "Profit After Tax",
        [
            r"profit after tax\b",
            r"profit for the (?:year|period|half[- ]year)\b",
            r"net profit after tax\b",
        ],
        "first_value",
    ),
]

_BALANCE_METRICS: list[tuple[str, list[str], str]] = [
    ("Total Assets", [r"total assets\b"], "first_value"),
    (
        "Net Loans and Advances",
        [r"(?:net )?loans and advances\b", r"advances to customers\b"],
        "first_value",
    ),
    ("Deposits", [r"^deposits\b"], "first_value"),
    (
        "Equity",
        [r"total equity\b", r"total shareholders'?\s+equity\b"],
        "first_value",
    ),
]

_CAPITAL_METRICS: list[tuple[str, list[str], str]] = [
    (
        "CET1 Ratio",
        [r"common equity tier\s*1\s+capital ratio\b", r"cet\s*1\s+capital ratio\b"],
        "second_pct",
    ),
    ("Total Capital Ratio", [r"total capital ratio\b"], "second_pct"),
]

_ALL_METRICS = _INCOME_METRICS + _BALANCE_METRICS + _CAPITAL_METRICS

# ── Unit detection ───────────────────────────────────────────────────────────
_MILLIONS_RE = re.compile(
    r"\$\s*millions?\b|NZ\$m\b|NZD\s*m\b|NZD\s*million|in millions",
    re.IGNORECASE,
)
_THOUSANDS_RE = re.compile(
    r"\$'?000\b|\$\s*thousands?\b|NZD\s*thousands?\b|NZD000\b|in thousands",
    re.IGNORECASE,
)

# Numeric token patterns
_NUMBER_RE = re.compile(
    r"""
    \([\d,]+(?:\.\d+)?\)   # bracketed negative:  (1,234) or (12.3)
    |
    [\d,]+\.\d+            # decimal with commas: 1,234.5 or 12.5
    |
    [\d,]{1,}              # integer with commas: 1,234  or bare integer 5
    """,
    re.VERBOSE,
)

# Percentage token pattern
_PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def extract_disclosures(
    raw_dir: Path,
    sources_config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract metrics from all bank disclosure PDFs found under ``raw_dir``.

    Parameters
    ----------
    raw_dir:
        Path to ``data/raw/financial_disclosures/``.  Each sub-directory is
        treated as a bank and matched against ``sources_config``.
    sources_config:
        Loaded ``config/sources.yaml``.  Used to resolve
        ``rbnz_entity_name`` for each bank.

    Returns
    -------
    list[dict]
        Canonical rows with keys: entity, metric, value, period, source.
    """
    entity_map = _build_entity_map(sources_config)

    output: list[dict[str, Any]] = []
    for bank_dir in sorted(raw_dir.iterdir()):
        if not bank_dir.is_dir():
            continue
        bank_id = bank_dir.name
        rows = _process_bank(bank_dir, bank_id, entity_map)
        logger.info("bank=%s: extracted %d rows", bank_id, len(rows))
        output.extend(rows)

    logger.info("Total disclosure rows extracted: %d", len(output))
    return output


def _build_entity_map(sources_config: dict[str, Any]) -> dict[str, str]:
    """Build a ``bank_id → rbnz_entity_name`` mapping from sources config."""
    result: dict[str, str] = {}
    banks = (sources_config.get("financial_disclosures") or {}).get("banks") or []
    for bank in banks:
        bank_id = bank.get("id", "")
        entity = bank.get("rbnz_entity_name", "")
        if bank_id and entity:
            result[bank_id] = entity
    return result


def _process_bank(
    bank_dir: Path,
    bank_id: str,
    entity_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Process all PDFs with sidecars in a single bank directory."""
    entity = entity_map.get(bank_id, bank_id.capitalize())
    output: list[dict[str, Any]] = []

    pdf_paths = sorted(bank_dir.glob("*.pdf"))
    for pdf_path in pdf_paths:
        meta_path = pdf_path.with_suffix(".pdf.meta.json")
        if not meta_path.exists():
            # Try alternate naming: <stem>.meta.json
            meta_path = pdf_path.parent / (pdf_path.stem + ".meta.json")
        if not meta_path.exists():
            logger.warning("Sidecar missing for %s — skipping", pdf_path.name)
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to read sidecar %s: %s — skipping", meta_path.name, exc)
            continue

        period_end = meta.get("period_end", "")
        if not period_end:
            logger.warning("No period_end in %s — skipping", meta_path.name)
            continue

        period = _to_quarter(period_end)
        source = f"{_SOURCE_PREFIX}-{bank_id}"

        rows = _extract_pdf_metrics(pdf_path, entity, period, source)
        output.extend(rows)

    return output


def _extract_pdf_metrics(
    pdf_path: Path,
    entity: str,
    period: str,
    source: str,
) -> list[dict[str, Any]]:
    """Extract metrics from a single PDF file.

    Parameters
    ----------
    pdf_path:
        Path to the PDF.
    entity:
        RBNZ entity name (e.g. "Kiwibank").
    period:
        Quarter string (e.g. "2024-Q2").
    source:
        Source identifier (e.g. "disclosure-kiwibank").

    Returns
    -------
    list[dict]
        Canonical rows.  Empty list if the PDF yields no matching metrics.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to open PDF %s: %s", pdf_path.name, exc)
        return []

    if not full_text.strip():
        logger.warning("PDF %s produced no text", pdf_path.name)
        return []

    scale = _detect_unit_scale(full_text)
    output: list[dict[str, Any]] = []

    for canonical_name, patterns, strategy in _ALL_METRICS:
        value = _extract_metric(full_text, patterns, strategy, scale)
        if value is None:
            logger.warning(
                "Metric not found: entity=%s period=%s metric=%r pdf=%s",
                entity,
                period,
                canonical_name,
                pdf_path.name,
            )
            continue
        output.append(
            {
                "entity": entity,
                "metric": canonical_name,
                "value": value,
                "period": period,
                "source": source,
            }
        )

    return output


def _detect_unit_scale(text: str) -> float:
    """Return the scale factor to convert extracted values to NZDm.

    Returns
    -------
    float
        1.0 if values are already in millions; 0.001 if in thousands.
    """
    # Search the first 3000 characters (cover the first few pages)
    sample = text[:3000]
    if _THOUSANDS_RE.search(sample):
        logger.debug("Unit detected: NZD thousands → applying ÷1000 scale")
        return 0.001
    # Default: millions (most NZ bank disclosures use NZ$m or $ millions)
    return 1.0


def _extract_metric(
    text: str,
    patterns: list[str],
    strategy: str,
    scale: float,
) -> float | None:
    """Search ``text`` for the first line matching any pattern and extract a value.

    Parameters
    ----------
    text:
        Full extracted PDF text.
    patterns:
        List of case-insensitive regex patterns to match against each line.
    strategy:
        ``"first_value"`` — extract the first financial value on the matched
        line, skipping small bare integers (likely note references).
        ``"second_pct"`` — extract the second percentage value on the line
        (first percentage is typically the regulatory minimum).
    scale:
        Unit scale factor (1.0 for millions, 0.001 for thousands).

    Returns
    -------
    float | None
        Extracted value in NZDm (or %) or ``None`` if not found.
    """
    combined = re.compile(
        "|".join(patterns),
        re.IGNORECASE | re.MULTILINE,
    )
    for line in text.splitlines():
        if not combined.search(line):
            continue
        if strategy == "second_pct":
            value = _extract_second_pct(line)
        else:
            value = _extract_first_value(line, scale)
        if value is not None:
            return value
    return None


def _extract_first_value(line: str, scale: float) -> float | None:
    """Extract the first financial value from a line, skipping note numbers.

    Note references are small positive integers (≤ 99) without commas that
    appear between the metric label and the financial value columns.

    Parameters
    ----------
    line:
        A single line of extracted PDF text.
    scale:
        Unit scale factor applied to the result.

    Returns
    -------
    float | None
    """
    tokens = _NUMBER_RE.findall(line)
    for tok in tokens:
        negative = tok.startswith("(")
        clean = tok.strip("()")
        # Remove commas for numeric conversion
        value_str = clean.replace(",", "")
        try:
            val = float(value_str)
        except ValueError:
            continue
        # Skip small bare integers that are likely note references.
        # Conditions: positive, no commas in original token, integer value, ≤ 99.
        if not negative and "," not in tok and val == int(val) and val <= 99:
            continue
        result = (-val if negative else val) * scale
        return result
    return None


def _extract_second_pct(line: str) -> float | None:
    """Extract the second percentage value from a line.

    Capital adequacy ratio lines have the form:
    ``<metric label>  <min%>  <current%>  <previous%>``
    We want the second percentage (current period).

    Parameters
    ----------
    line:
        A single line of extracted PDF text.

    Returns
    -------
    float | None
        The percentage value (e.g. 11.9 for 11.9%) or ``None``.
    """
    pct_values = _PCT_RE.findall(line)
    if len(pct_values) >= 2:
        try:
            return float(pct_values[1])
        except ValueError:
            pass
    # Fallback: if only one % value, return it (some formats omit minimum column)
    if len(pct_values) == 1:
        try:
            return float(pct_values[0])
        except ValueError:
            pass
    return None
