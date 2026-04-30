"""Parse the RBNZ B2 Official Cash Rate (OCR) XLSX.

Processing layer responsibility: read the RBNZ B2 monthly-close XLSX,
locate the OCR column, convert monthly observations to quarterly (last
value in each calendar quarter), and return canonical rows:

    entity  — always "RBNZ"
    metric  — always "OCR"
    value   — OCR rate as a float percentage (e.g. 5.5)
    period  — quarter string using quarter-end month (e.g. "2024-Q2")
    source  — always "rbnz-ocr"

Monthly → quarterly conversion: for each calendar quarter
(Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec), take the
last available monthly value (i.e. March, June, September, December).

The XLSX is expected at the path declared in ``config/sources.yaml``
under ``ocr.xlsx_sources[0].output_file``.  If that file is absent, the
module falls back to any ``rbnz-ocr*.xlsx`` in ``data/raw/``.
"""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

import openpyxl  # type: ignore[import-untyped]

from src.logger import get_logger
from src.processing.parse import _to_quarter

logger = get_logger(__name__)

_ENTITY = "RBNZ"
_METRIC = "OCR"
_SOURCE = "rbnz-ocr"

# Column header patterns that identify the OCR series
_OCR_HEADER_PATTERNS = ("OCR", "Official Cash Rate", "official cash rate")


def parse_ocr(
    xlsx_path: Path | None = None,
    sources_config: dict[str, Any] | None = None,
    raw_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Parse the RBNZ B2 XLSX and return quarterly OCR rows.

    Parameters
    ----------
    xlsx_path:
        Direct path to the XLSX file.  When provided, ``sources_config``
        and ``raw_dir`` are ignored.
    sources_config:
        Loaded ``config/sources.yaml``.  Used to resolve the ``output_file``
        path from ``ocr.xlsx_sources[0]``.  Ignored when ``xlsx_path`` is
        given.
    raw_dir:
        Base directory for the fallback glob (``data/raw/``).  Defaults to
        ``data/raw/`` relative to the repo root if ``None``.

    Returns
    -------
    list[dict]
        Canonical rows with keys: entity, metric, value, period, source.

    Raises
    ------
    FileNotFoundError
        If no OCR XLSX file can be found.
    ValueError
        If no column matching "OCR" or "Official Cash Rate" is found in the
        XLSX.
    """
    path = _resolve_xlsx_path(xlsx_path, sources_config, raw_dir)

    logger.info("Opening OCR XLSX: %s", path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb.active
        if ws is None:
            raise ValueError(f"XLSX has no active sheet: {path}")
        all_rows: list[tuple[Any, ...]] = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()

    if not all_rows:
        raise ValueError(f"XLSX is empty: {path}")

    ocr_col = _find_ocr_column(all_rows)
    date_col = _find_date_column(all_rows)

    logger.info("OCR column index: %d, Date column index: %d", ocr_col, date_col)

    monthly: list[tuple[Any, float]] = _extract_monthly(all_rows, date_col, ocr_col)
    logger.info("Extracted %d monthly OCR observations", len(monthly))

    quarterly = _monthly_to_quarterly(monthly)
    logger.info("Converted to %d quarterly observations", len(quarterly))

    rows = [
        {
            "entity": _ENTITY,
            "metric": _METRIC,
            "value": value,
            "period": period,
            "source": _SOURCE,
        }
        for period, value in quarterly
    ]
    return rows


def _resolve_xlsx_path(
    xlsx_path: Path | None,
    sources_config: dict[str, Any] | None,
    raw_dir: Path | None,
) -> Path:
    """Resolve the XLSX file path from the given inputs.

    Raises ``FileNotFoundError`` if no file can be located.
    """
    if xlsx_path is not None:
        if not xlsx_path.exists():
            raise FileNotFoundError(f"OCR XLSX not found: {xlsx_path}")
        return xlsx_path

    # Try path from sources_config
    if sources_config is not None:
        output_file = (
            (sources_config.get("ocr") or {}).get("xlsx_sources", [{}])[0].get("output_file")
        )
        if output_file:
            candidate = Path(output_file)
            if candidate.exists():
                return candidate

    # Fallback: glob in raw_dir
    base = raw_dir or Path(__file__).parent.parent.parent / "data" / "raw"
    matches = sorted(glob.glob(str(base / "rbnz-ocr*.xlsx")))
    if matches:
        logger.info("Using fallback OCR XLSX: %s", matches[0])
        return Path(matches[0])

    raise FileNotFoundError(
        "No OCR XLSX found.  Run the fetch-data workflow or place rbnz-ocr.xlsx in data/raw/."
    )


def _find_ocr_column(rows: list[tuple[Any, ...]]) -> int:
    """Scan header rows to find the column index containing the OCR series.

    Parameters
    ----------
    rows:
        All rows from the XLSX sheet (values only).

    Returns
    -------
    int
        Zero-based column index.

    Raises
    ------
    ValueError
        If no OCR column header is found in the first 10 rows.
    """
    for row in rows[:10]:
        for col_idx, cell in enumerate(row):
            if cell is None:
                continue
            cell_str = str(cell).strip()
            for pattern in _OCR_HEADER_PATTERNS:
                if pattern.lower() in cell_str.lower():
                    return col_idx
    raise ValueError(
        "No OCR column found in XLSX header rows.  "
        f"Expected a column containing one of: {_OCR_HEADER_PATTERNS}"
    )


def _find_date_column(rows: list[tuple[Any, ...]]) -> int:
    """Return the index of the date column (first column with date-like values).

    Scans data rows (after headers) for the first column whose non-null
    values have ``month`` and ``year`` attributes (i.e. ``datetime``).
    Falls back to column 0 if none found.
    """
    for row in rows[5:15]:
        for col_idx, cell in enumerate(row):
            if hasattr(cell, "month") and hasattr(cell, "year"):
                return col_idx
    return 0


def _extract_monthly(
    rows: list[tuple[Any, ...]],
    date_col: int,
    ocr_col: int,
) -> list[tuple[Any, float]]:
    """Extract (date, ocr_value) tuples from data rows.

    Rows with non-date date cells or non-numeric OCR values are skipped
    with a DEBUG log.
    """
    result: list[tuple[Any, float]] = []
    for row in rows:
        if len(row) <= max(date_col, ocr_col):
            continue
        date_cell = row[date_col]
        ocr_cell = row[ocr_col]

        if not hasattr(date_cell, "month"):
            continue
        if ocr_cell is None:
            logger.debug("Skipping row with null OCR at %s", date_cell)
            continue
        try:
            value = float(ocr_cell)
        except (TypeError, ValueError):
            logger.debug("Skipping non-numeric OCR value %r at %s", ocr_cell, date_cell)
            continue

        result.append((date_cell, value))

    return result


def _monthly_to_quarterly(
    monthly: list[tuple[Any, float]],
) -> list[tuple[str, float]]:
    """Convert monthly (date, value) pairs to quarterly by taking the last value.

    For each calendar quarter (Q1 = Jan–Mar, Q2 = Apr–Jun, etc.), the last
    monthly observation within that quarter is used as the quarterly value.
    This corresponds to the end-of-quarter OCR setting.

    Parameters
    ----------
    monthly:
        List of ``(date, value)`` tuples ordered chronologically.

    Returns
    -------
    list[tuple[str, float]]
        List of ``(period, value)`` tuples, e.g. ``[("2024-Q2", 5.5), ...]``,
        sorted by period.
    """
    # Group by year+quarter, keeping only the last observation per quarter
    quarters: dict[str, float] = {}
    for date, value in monthly:
        period = _to_quarter(date)
        # Overwrite: later months in the same quarter replace earlier ones
        quarters[period] = value

    return sorted(quarters.items())
