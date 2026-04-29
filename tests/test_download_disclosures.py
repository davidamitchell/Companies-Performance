"""Tests for scripts/download_disclosures.py."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.download_disclosures import (
    _is_fresh,
    download_bank,
    download_pdf,
    load_banks,
    main,
    meta_path_for,
    pdf_path_for,
    read_meta,
    sha256_file,
    write_meta,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_bank(
    bank_id: str = "testbank",
    reports: list[dict] | None = None,
    bank_name: str = "Test Bank",
) -> dict:
    if reports is None:
        reports = [
            {
                "period_end": "2024-09-30",
                "period_type": "full_year",
                "url": "https://example.com/test.pdf",
                "status": "confirmed",
            }
        ]
    return {"id": bank_id, "rbnz_entity_name": bank_name, "reports": reports}


def _make_mock_response(status_code: int, content: bytes = b"%PDF-1.4 test") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.iter_content = MagicMock(return_value=iter([content]))
    return resp


# ---------------------------------------------------------------------------
# sha256_file
# ---------------------------------------------------------------------------


def test_sha256_file_returns_hex_digest(tmp_path: Path) -> None:
    """sha256_file returns the correct hex SHA-256 of a file."""
    content = b"hello world"
    f = tmp_path / "test.bin"
    f.write_bytes(content)
    expected = hashlib.sha256(content).hexdigest()
    assert sha256_file(f) == expected


# ---------------------------------------------------------------------------
# pdf_path_for / meta_path_for
# ---------------------------------------------------------------------------


def test_pdf_path_for_constructs_correct_path() -> None:
    """pdf_path_for returns the conventional path for a bank + period."""
    p = pdf_path_for("anz", "2024-09-30")
    assert p == Path("data/raw/financial_disclosures/anz/anz-disclosure-2024-09-30.pdf")


def test_meta_path_for_constructs_correct_path() -> None:
    """meta_path_for returns the conventional sidecar path."""
    p = meta_path_for("anz", "2024-09-30")
    assert p == Path("data/raw/financial_disclosures/anz/anz-disclosure-2024-09-30.meta.json")


# ---------------------------------------------------------------------------
# read_meta
# ---------------------------------------------------------------------------


def test_read_meta_returns_none_when_file_missing(tmp_path: Path) -> None:
    """read_meta returns None when the sidecar file does not exist."""
    assert read_meta(tmp_path / "nonexistent.meta.json") is None


def test_read_meta_returns_dict_when_file_exists(tmp_path: Path) -> None:
    """read_meta parses and returns the sidecar JSON."""
    meta_file = tmp_path / "test.meta.json"
    meta_file.write_text(json.dumps({"bank_id": "anz", "sha256": "abc"}))
    result = read_meta(meta_file)
    assert result == {"bank_id": "anz", "sha256": "abc"}


# ---------------------------------------------------------------------------
# write_meta
# ---------------------------------------------------------------------------


def test_write_meta_creates_file_with_correct_fields(tmp_path: Path) -> None:
    """write_meta creates a well-formed JSON sidecar file."""
    meta_path = tmp_path / "anz" / "anz-disclosure-2024-09-30.meta.json"
    write_meta(
        meta_path,
        bank_id="anz",
        bank_name="ANZ",
        period_end="2024-09-30",
        period_type="full_year",
        source_url="https://example.com/anz.pdf",
        downloaded_at="2024-09-30T12:00:00+00:00",
        file_size_bytes=1024,
        sha256="deadbeef",
    )
    assert meta_path.exists()
    data = json.loads(meta_path.read_text())
    assert data["bank_id"] == "anz"
    assert data["bank_name"] == "ANZ"
    assert data["period_end"] == "2024-09-30"
    assert data["period_type"] == "full_year"
    assert data["source_url"] == "https://example.com/anz.pdf"
    assert data["downloaded_at"] == "2024-09-30T12:00:00+00:00"
    assert data["file_size_bytes"] == 1024
    assert data["sha256"] == "deadbeef"


def test_write_meta_creates_parent_dirs(tmp_path: Path) -> None:
    """write_meta creates missing parent directories."""
    meta_path = tmp_path / "deep" / "nested" / "dir" / "file.meta.json"
    write_meta(
        meta_path,
        bank_id="x",
        bank_name="X",
        period_end="2024-01-01",
        period_type="full_year",
        source_url="https://example.com/x.pdf",
        downloaded_at="2024-01-01T00:00:00+00:00",
        file_size_bytes=0,
        sha256="",
    )
    assert meta_path.exists()


# ---------------------------------------------------------------------------
# _is_fresh
# ---------------------------------------------------------------------------


def test_is_fresh_true_when_file_exists_and_checksum_matches(tmp_path: Path) -> None:
    """_is_fresh returns True when the PDF checksum matches the sidecar."""
    content = b"pdf content"
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(content)
    checksum = hashlib.sha256(content).hexdigest()
    assert _is_fresh(pdf, {"sha256": checksum}) is True


def test_is_fresh_false_when_file_missing(tmp_path: Path) -> None:
    """_is_fresh returns False when the PDF does not exist."""
    assert _is_fresh(tmp_path / "missing.pdf", {"sha256": "abc"}) is False


def test_is_fresh_false_when_checksum_mismatch(tmp_path: Path) -> None:
    """_is_fresh returns False when checksum does not match."""
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"different content")
    assert _is_fresh(pdf, {"sha256": "wrongchecksum"}) is False


def test_is_fresh_false_when_meta_missing_sha256(tmp_path: Path) -> None:
    """_is_fresh returns False when the sidecar has no sha256 key."""
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"content")
    assert _is_fresh(pdf, {}) is False


# ---------------------------------------------------------------------------
# download_pdf
# ---------------------------------------------------------------------------


def test_download_pdf_writes_content_to_dest(tmp_path: Path) -> None:
    """download_pdf writes the response body to the destination path."""
    content = b"%PDF-1.4 hello"
    dest = tmp_path / "out.pdf"
    mock_resp = _make_mock_response(200, content)
    with patch("scripts.download_disclosures.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = mock_resp
        download_pdf("https://example.com/test.pdf", dest)
    assert dest.exists()
    assert dest.read_bytes() == content


def test_download_pdf_raises_on_http_error(tmp_path: Path) -> None:
    """download_pdf raises RuntimeError on non-200 status."""
    dest = tmp_path / "out.pdf"
    mock_resp = _make_mock_response(404)
    with patch("scripts.download_disclosures.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = mock_resp
        with pytest.raises(RuntimeError, match="HTTP 404"):
            download_pdf("https://example.com/missing.pdf", dest)


def test_download_pdf_creates_parent_dirs(tmp_path: Path) -> None:
    """download_pdf creates any missing parent directories."""
    content = b"%PDF"
    dest = tmp_path / "subdir" / "nested" / "file.pdf"
    mock_resp = _make_mock_response(200, content)
    with patch("scripts.download_disclosures.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = mock_resp
        download_pdf("https://example.com/test.pdf", dest)
    assert dest.exists()


# ---------------------------------------------------------------------------
# load_banks
# ---------------------------------------------------------------------------


def test_load_banks_returns_list(tmp_path: Path) -> None:
    """load_banks parses the YAML and returns the banks list."""
    cfg = tmp_path / "config" / "sources.yaml"
    cfg.parent.mkdir()
    cfg.write_text(
        "financial_disclosures:\n"
        "  banks:\n"
        "    - id: testbank\n"
        "      rbnz_entity_name: Test Bank\n"
        "      reports: []\n",
        encoding="utf-8",
    )
    with patch("scripts.download_disclosures._CONFIG_PATH", cfg):
        banks = load_banks()
    assert len(banks) == 1
    assert banks[0]["id"] == "testbank"


# ---------------------------------------------------------------------------
# download_bank
# ---------------------------------------------------------------------------


def test_download_bank_skips_pending_reports(tmp_path: Path) -> None:
    """download_bank skips reports with status != confirmed."""
    bank = _make_bank(
        reports=[{"period_end": "2024-09-30", "url": "https://x.com/r.pdf", "status": "pending"}]
    )
    with patch("scripts.download_disclosures._OUTPUT_ROOT", tmp_path):
        ok, failed = download_bank(bank)
    assert ok == 0
    assert failed == 0


def test_download_bank_skips_when_fresh(tmp_path: Path) -> None:
    """download_bank skips download when the PDF is already fresh."""
    content = b"%PDF fresh"
    bank = _make_bank()
    pdf = tmp_path / "testbank" / "testbank-disclosure-2024-09-30.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(content)
    checksum = hashlib.sha256(content).hexdigest()
    meta_p = tmp_path / "testbank" / "testbank-disclosure-2024-09-30.meta.json"
    meta_p.write_text(json.dumps({"sha256": checksum}))

    with (
        patch("scripts.download_disclosures._OUTPUT_ROOT", tmp_path),
        patch("scripts.download_disclosures.download_pdf") as mock_dl,
    ):
        ok, failed = download_bank(bank)

    mock_dl.assert_not_called()
    assert ok == 1
    assert failed == 0


def test_download_bank_force_redownloads_even_when_fresh(tmp_path: Path) -> None:
    """download_bank --force re-downloads even if the PDF is already fresh."""
    content = b"%PDF fresh"
    bank = _make_bank()
    pdf = tmp_path / "testbank" / "testbank-disclosure-2024-09-30.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(content)
    checksum = hashlib.sha256(content).hexdigest()
    meta_p = tmp_path / "testbank" / "testbank-disclosure-2024-09-30.meta.json"
    meta_p.write_text(json.dumps({"sha256": checksum}))

    def _fake_download(url: str, dest: Path) -> None:
        dest.write_bytes(b"%PDF refreshed")

    with (
        patch("scripts.download_disclosures._OUTPUT_ROOT", tmp_path),
        patch("scripts.download_disclosures.download_pdf", side_effect=_fake_download),
    ):
        ok, failed = download_bank(bank, force=True)

    assert ok == 1
    assert failed == 0


def test_download_bank_writes_metadata_on_success(tmp_path: Path) -> None:
    """download_bank writes a sidecar metadata file after a successful download."""
    bank = _make_bank()

    def _fake_download(url: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"%PDF-1.4 content")

    with (
        patch("scripts.download_disclosures._OUTPUT_ROOT", tmp_path),
        patch("scripts.download_disclosures.download_pdf", side_effect=_fake_download),
    ):
        ok, failed = download_bank(bank)

    assert ok == 1
    assert failed == 0
    meta_p = tmp_path / "testbank" / "testbank-disclosure-2024-09-30.meta.json"
    assert meta_p.exists()
    meta = json.loads(meta_p.read_text())
    assert meta["bank_id"] == "testbank"
    assert meta["source_url"] == "https://example.com/test.pdf"
    assert meta["period_end"] == "2024-09-30"
    assert meta["period_type"] == "full_year"
    assert "downloaded_at" in meta
    assert "sha256" in meta
    assert "file_size_bytes" in meta


def test_download_bank_counts_failed_on_download_error(tmp_path: Path) -> None:
    """download_bank counts failures and does not raise."""
    bank = _make_bank()
    with (
        patch("scripts.download_disclosures._OUTPUT_ROOT", tmp_path),
        patch(
            "scripts.download_disclosures.download_pdf",
            side_effect=RuntimeError("HTTP 404"),
        ),
    ):
        ok, failed = download_bank(bank)

    assert ok == 0
    assert failed == 1


def test_download_bank_no_confirmed_returns_zeros(tmp_path: Path) -> None:
    """download_bank with no confirmed reports returns (0, 0)."""
    bank = _make_bank(reports=[])
    with patch("scripts.download_disclosures._OUTPUT_ROOT", tmp_path):
        ok, failed = download_bank(bank)
    assert ok == 0
    assert failed == 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_returns_0_on_success() -> None:
    """main() returns 0 when all downloads succeed."""
    with (
        patch("scripts.download_disclosures.load_banks", return_value=[]),
    ):
        assert main([]) == 0


def test_main_returns_1_on_failure() -> None:
    """main() returns 1 when at least one download fails."""
    bank = _make_bank()
    with (
        patch("scripts.download_disclosures.load_banks", return_value=[bank]),
        patch(
            "scripts.download_disclosures.download_bank",
            return_value=(0, 1),
        ),
    ):
        assert main([]) == 1


def test_main_bank_filter_unknown_returns_1() -> None:
    """main() returns 1 when --bank specifies an unknown bank ID."""
    with patch(
        "scripts.download_disclosures.load_banks",
        return_value=[_make_bank("anz")],
    ):
        assert main(["--bank", "nonexistent"]) == 1


def test_main_bank_filter_limits_to_specified_bank() -> None:
    """main() with --bank only processes the specified bank."""
    bank_a = _make_bank("anz")
    bank_b = _make_bank("asb")
    calls: list[str] = []

    def _fake_download_bank(bank: dict, *, force: bool = False) -> tuple[int, int]:
        calls.append(bank["id"])
        return 1, 0

    with (
        patch("scripts.download_disclosures.load_banks", return_value=[bank_a, bank_b]),
        patch(
            "scripts.download_disclosures.download_bank",
            side_effect=_fake_download_bank,
        ),
    ):
        result = main(["--bank", "anz"])

    assert result == 0
    assert calls == ["anz"]


def test_main_force_flag_is_passed_to_download_bank() -> None:
    """main() passes force=True to download_bank when --force is given."""
    bank = _make_bank()
    received_force: list[bool] = []

    def _fake_download_bank(b: dict, *, force: bool = False) -> tuple[int, int]:
        received_force.append(force)
        return 1, 0

    with (
        patch("scripts.download_disclosures.load_banks", return_value=[bank]),
        patch(
            "scripts.download_disclosures.download_bank",
            side_effect=_fake_download_bank,
        ),
    ):
        main(["--force"])

    assert received_force == [True]
