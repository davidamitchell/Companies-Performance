"""Tests for scripts/validate_disclosure_urls.py."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from scripts.validate_disclosure_urls import _check_url, _dump_yaml, _load_yaml, main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sources(bank_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a minimal sources dict containing one bank with the given reports."""
    return {
        "rbnz": {},
        "financial_disclosures": {
            "banks": [
                {
                    "id": "testbank",
                    "rbnz_entity_name": "Test Bank",
                    "reports": bank_reports,
                }
            ]
        },
    }


def _make_report(
    period_end: str = "2024-09-30",
    period_type: str = "full_year",
    url: str = "https://example.com/report.pdf",
    status: str = "confirmed",
) -> dict[str, Any]:
    return {
        "period_end": period_end,
        "period_type": period_type,
        "url": url,
        "status": status,
    }


def _make_mock_response(status_code: int) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    return resp


# ---------------------------------------------------------------------------
# _check_url unit tests
# ---------------------------------------------------------------------------


def test_check_url_200_returns_confirmed() -> None:
    """A 200 response resolves to confirmed."""
    import requests as req

    session = MagicMock(spec=req.Session)
    session.head.return_value = _make_mock_response(200)

    http_status, resolved_status = _check_url(session, "https://example.com/ok.pdf")

    assert http_status == 200
    assert resolved_status == "confirmed"


def test_check_url_404_returns_not_found() -> None:
    """A 404 response resolves to not_found."""
    import requests as req

    session = MagicMock(spec=req.Session)
    session.head.return_value = _make_mock_response(404)

    http_status, resolved_status = _check_url(session, "https://example.com/missing.pdf")

    assert http_status == 404
    assert resolved_status == "not_found"


def test_check_url_500_returns_not_found() -> None:
    """A 5xx response also resolves to not_found."""
    import requests as req

    session = MagicMock(spec=req.Session)
    session.head.return_value = _make_mock_response(500)

    http_status, resolved_status = _check_url(session, "https://example.com/error.pdf")

    assert http_status == 500
    assert resolved_status == "not_found"


def test_check_url_connection_error_returns_not_reachable() -> None:
    """A ConnectionError resolves to not_reachable with None http_status."""
    import requests as req

    session = MagicMock(spec=req.Session)
    session.head.side_effect = req.exceptions.ConnectionError("refused")

    http_status, resolved_status = _check_url(session, "https://example.com/unreachable.pdf")

    assert http_status is None
    assert resolved_status == "not_reachable"


def test_check_url_timeout_returns_not_reachable() -> None:
    """A Timeout resolves to not_reachable with None http_status."""
    import requests as req

    session = MagicMock(spec=req.Session)
    session.head.side_effect = req.exceptions.Timeout("timed out")

    http_status, resolved_status = _check_url(session, "https://example.com/slow.pdf")

    assert http_status is None
    assert resolved_status == "not_reachable"


# ---------------------------------------------------------------------------
# main() integration tests (all I/O mocked)
# ---------------------------------------------------------------------------


def test_main_200_updates_status_to_confirmed(tmp_path: Path) -> None:
    """main() sets status=confirmed for a 200 URL."""
    sources = _make_sources([_make_report(status="pending")])
    sources_path = tmp_path / "sources.yaml"
    results_path = tmp_path / "url_validation.json"

    mock_response = _make_mock_response(200)

    with (
        patch("scripts.validate_disclosure_urls._SOURCES_PATH", sources_path),
        patch("scripts.validate_disclosure_urls._RESULTS_PATH", results_path),
        patch("scripts.validate_disclosure_urls._load_yaml", return_value=sources),
        patch("scripts.validate_disclosure_urls._dump_yaml") as mock_dump,
        patch("requests.Session") as mock_session_cls,
    ):
        mock_session = MagicMock()
        mock_session.head.return_value = mock_response
        mock_session_cls.return_value = mock_session
        results_path.parent.mkdir(parents=True, exist_ok=True)

        result = main()

    assert result == 0
    saved_sources = mock_dump.call_args[0][0]
    report = saved_sources["financial_disclosures"]["banks"][0]["reports"][0]
    assert report["status"] == "confirmed"


def test_main_404_updates_status_to_not_found(tmp_path: Path) -> None:
    """main() sets status=not_found for a 404 URL."""
    sources = _make_sources([_make_report(status="confirmed")])
    results_path = tmp_path / "url_validation.json"

    mock_response = _make_mock_response(404)

    with (
        patch("scripts.validate_disclosure_urls._load_yaml", return_value=sources),
        patch("scripts.validate_disclosure_urls._dump_yaml") as mock_dump,
        patch("scripts.validate_disclosure_urls._RESULTS_PATH", results_path),
        patch("requests.Session") as mock_session_cls,
    ):
        mock_session = MagicMock()
        mock_session.head.return_value = mock_response
        mock_session_cls.return_value = mock_session
        results_path.parent.mkdir(parents=True, exist_ok=True)

        result = main()

    assert result == 0
    saved_sources = mock_dump.call_args[0][0]
    report = saved_sources["financial_disclosures"]["banks"][0]["reports"][0]
    assert report["status"] == "not_found"


def test_main_connection_error_leaves_status_pending(tmp_path: Path) -> None:
    """main() leaves status=pending when a connection error occurs."""
    import requests as req_module

    sources = _make_sources([_make_report(status="pending")])
    results_path = tmp_path / "url_validation.json"

    with (
        patch("scripts.validate_disclosure_urls._load_yaml", return_value=sources),
        patch("scripts.validate_disclosure_urls._dump_yaml") as mock_dump,
        patch("scripts.validate_disclosure_urls._RESULTS_PATH", results_path),
        patch("requests.Session") as mock_session_cls,
    ):
        mock_session = MagicMock()
        mock_session.head.side_effect = req_module.exceptions.ConnectionError("refused")
        mock_session_cls.return_value = mock_session
        results_path.parent.mkdir(parents=True, exist_ok=True)

        result = main()

    assert result == 0
    saved_sources = mock_dump.call_args[0][0]
    report = saved_sources["financial_disclosures"]["banks"][0]["reports"][0]
    # Status must NOT be overwritten when not_reachable
    assert report["status"] == "pending"


def test_main_writes_json_with_correct_structure(tmp_path: Path) -> None:
    """main() writes a JSON file with the expected fields per URL."""
    report = _make_report(
        period_end="2024-09-30",
        period_type="full_year",
        url="https://example.com/anz-2024.pdf",
        status="pending",
    )
    sources = _make_sources([report])
    results_path = tmp_path / "url_validation.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    mock_response = _make_mock_response(200)

    with (
        patch("scripts.validate_disclosure_urls._load_yaml", return_value=sources),
        patch("scripts.validate_disclosure_urls._dump_yaml"),
        patch("scripts.validate_disclosure_urls._RESULTS_PATH", results_path),
        patch("requests.Session") as mock_session_cls,
    ):
        mock_session = MagicMock()
        mock_session.head.return_value = mock_response
        mock_session_cls.return_value = mock_session

        main()

    assert results_path.exists()
    data = json.loads(results_path.read_text())
    assert "validated_at" in data
    assert "results" in data
    assert len(data["results"]) == 1

    rec = data["results"][0]
    assert rec["bank_id"] == "testbank"
    assert rec["period_end"] == "2024-09-30"
    assert rec["period_type"] == "full_year"
    assert rec["url"] == "https://example.com/anz-2024.pdf"
    assert rec["http_status"] == 200
    assert rec["resolved_status"] == "confirmed"


def test_main_not_reachable_json_has_null_http_status(tmp_path: Path) -> None:
    """main() records http_status=null in JSON when not_reachable."""
    import requests as req_module

    sources = _make_sources([_make_report(status="pending")])
    results_path = tmp_path / "url_validation.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with (
        patch("scripts.validate_disclosure_urls._load_yaml", return_value=sources),
        patch("scripts.validate_disclosure_urls._dump_yaml"),
        patch("scripts.validate_disclosure_urls._RESULTS_PATH", results_path),
        patch("requests.Session") as mock_session_cls,
    ):
        mock_session = MagicMock()
        mock_session.head.side_effect = req_module.exceptions.ConnectionError("refused")
        mock_session_cls.return_value = mock_session

        main()

    data = json.loads(results_path.read_text())
    rec = data["results"][0]
    assert rec["http_status"] is None
    assert rec["resolved_status"] == "not_reachable"


def test_main_no_banks_returns_zero(tmp_path: Path) -> None:
    """main() returns 0 and writes nothing when there are no banks configured."""
    sources: dict[str, Any] = {"rbnz": {}, "financial_disclosures": {"banks": []}}
    results_path = tmp_path / "url_validation.json"

    with (
        patch("scripts.validate_disclosure_urls._load_yaml", return_value=sources),
        patch("scripts.validate_disclosure_urls._dump_yaml"),
        patch("scripts.validate_disclosure_urls._RESULTS_PATH", results_path),
    ):
        result = main()

    assert result == 0
    assert not results_path.exists()


# ---------------------------------------------------------------------------
# _load_yaml / _dump_yaml round-trip
# ---------------------------------------------------------------------------


def test_yaml_round_trip(tmp_path: Path) -> None:
    """_dump_yaml followed by _load_yaml preserves the data."""
    original: dict[str, Any] = {
        "financial_disclosures": {
            "banks": [
                {
                    "id": "anz",
                    "reports": [{"period_end": "2024-09-30", "status": "confirmed"}],
                }
            ]
        }
    }
    yaml_path = tmp_path / "sources.yaml"
    _dump_yaml(original, yaml_path)
    loaded = _load_yaml(yaml_path)
    assert loaded == original
