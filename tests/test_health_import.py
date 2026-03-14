"""Tests for health_import: excel_parser, pdf_parser, and storage."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from health_import.excel_parser import _parse_date, parse_excel
from health_import.pdf_parser import parse_lab_pdf
from health_import.storage import (
    get_activity_store,
    get_lab_store,
    query_activity,
    query_lab_results,
    save_activity_rows,
    save_lab_results,
)


# ---------------------------------------------------------------------------
# excel_parser tests
# ---------------------------------------------------------------------------


class TestParseDate:
    def test_iso_string(self):
        assert _parse_date("2024-03-14") == "2024-03-14"

    def test_us_slash_format(self):
        assert _parse_date("03/14/2024") == "2024-03-14"

    def test_eu_slash_format(self):
        assert _parse_date("14/03/2024") == "2024-03-14"

    def test_datetime_object(self):
        assert _parse_date(datetime(2024, 6, 1)) == "2024-06-01"

    def test_excel_serial_number(self):
        # Excel serial 45365 = 2024-03-14 (days since 1899-12-30)
        result = _parse_date(45365)
        assert result == "2024-03-14"

    def test_excel_serial_not_nanoseconds(self):
        # Old behavior: pd.Timestamp(45365) would interpret as ns since epoch (~1970-01-01)
        # New behavior: should produce a date far in the future from Unix epoch,
        # specifically 45365 days after 1899-12-30 = 2024-03-14
        result = _parse_date(45365)
        assert result is not None
        year = int(result.split("-")[0])
        assert year >= 2000, "Excel serial date should resolve to a modern date"

    def test_nan_returns_none(self):
        assert _parse_date(float("nan")) is None
        assert _parse_date(pd.NaT) is None

    def test_none_returns_none(self):
        assert _parse_date(None) is None

    def test_invalid_string_returns_none(self):
        assert _parse_date("not-a-date") is None


class TestParseExcel:
    def _make_csv_bytes(self, content: str) -> bytes:
        return content.encode()

    def test_basic_csv_parse(self):
        csv_content = "date,steps,calories\n2024-01-01,8000,2000\n2024-01-02,9000,2200\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        assert errors == []
        assert len(df) == 2
        assert list(df["date"]) == ["2024-01-01", "2024-01-02"]
        assert df["steps"].iloc[0] == 8000.0

    def test_column_aliasing(self):
        csv_content = "Day,step_count,kcal\n2024-02-01,7000,1800\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        assert "date" in df.columns
        assert "steps" in df.columns
        assert "calories" in df.columns

    def test_invalid_dates_dropped(self):
        csv_content = "date,steps\n2024-01-01,5000\nnot-a-date,6000\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        assert len(df) == 1
        assert any("invalid dates" in e.lower() for e in errors)

    def test_deduplication_last_wins(self):
        csv_content = "date,steps\n2024-01-01,5000\n2024-01-01,9999\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        assert len(df) == 1
        assert df["steps"].iloc[0] == 9999.0

    def test_missing_date_column_returns_error(self):
        csv_content = "steps,calories\n8000,2000\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        assert df.empty
        assert any("date" in e.lower() for e in errors)

    def test_empty_file_returns_error(self):
        df, errors = parse_excel(b"", filename="test.csv")
        assert df.empty
        assert errors

    def test_numeric_columns_coerced(self):
        csv_content = "date,steps,calories\n2024-01-01,abc,2000\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        # 'abc' in steps should be coerced to NaN
        assert pd.isna(df["steps"].iloc[0])

    def test_excel_serial_date_in_csv(self):
        # 45365 = 2024-03-14 in Excel serial format
        csv_content = "date,steps\n45365,10000\n"
        df, errors = parse_excel(self._make_csv_bytes(csv_content), filename="test.csv")
        assert not df.empty
        assert df["date"].iloc[0] == "2024-03-14"


# ---------------------------------------------------------------------------
# pdf_parser tests
# ---------------------------------------------------------------------------


class TestParsePanelDate:
    """Tests for panel_date validation and normalization in parse_lab_pdf."""

    def _run_with_panel_date(self, panel_date):
        """Run parse_lab_pdf with mocked pdfplumber returning no tables/text."""
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = []
        mock_page.extract_text.return_value = ""
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = lambda s: s
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            results, errors = parse_lab_pdf(b"%PDF-1.4", panel_date=panel_date)
        return results, errors

    def test_iso_date_accepted(self):
        _results, errors = self._run_with_panel_date("2024-03-14")
        # Should not get an invalid date error
        assert not any("Invalid panel_date" in e for e in errors)

    def test_us_slash_date_normalized(self):
        _results, errors = self._run_with_panel_date("03/14/2024")
        assert not any("Invalid panel_date" in e for e in errors)

    def test_invalid_date_produces_warning(self):
        _results, errors = self._run_with_panel_date("not-a-date")
        assert any("Invalid panel_date" in e for e in errors)

    def test_none_panel_date_auto_detects(self):
        """When panel_date is None and PDF has no date, error about missing date."""
        _results, errors = self._run_with_panel_date(None)
        assert any("panel date" in e.lower() for e in errors)

    def test_results_get_normalized_date(self):
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [[
            ["Test", "Value", "Unit", "Reference"],
            ["Glucose", "90", "mg/dL", "70-100"],
        ]]
        mock_page.extract_text.return_value = "Glucose 90 mg/dL"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = lambda s: s
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            results, _errors = parse_lab_pdf(b"%PDF-1.4", panel_date="03/14/2024")

        # All results should have ISO date
        for r in results:
            if r.get("panel_date"):
                assert r["panel_date"] == "2024-03-14"


# ---------------------------------------------------------------------------
# storage tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_data_dir(tmp_path):
    return str(tmp_path)


class TestSaveActivityRows:
    def test_basic_insert(self, tmp_data_dir):
        df = pd.DataFrame([{"date": "2024-01-01", "steps": 8000.0, "calories": 2000.0}])
        conn = get_activity_store(tmp_data_dir)
        n = save_activity_rows(conn, df, source="test")
        conn.close()
        assert n == 1

    def test_upsert_updates_existing(self, tmp_data_dir):
        df1 = pd.DataFrame([{"date": "2024-01-01", "steps": 5000.0}])
        df2 = pd.DataFrame([{"date": "2024-01-01", "steps": 9999.0}])
        conn = get_activity_store(tmp_data_dir)
        save_activity_rows(conn, df1, source="test")
        save_activity_rows(conn, df2, source="test")
        result = query_activity(tmp_data_dir, "2024-01-01", "2024-01-01")
        conn.close()
        assert result.iloc[0]["steps"] == 9999.0

    def test_empty_df_returns_zero(self, tmp_data_dir):
        conn = get_activity_store(tmp_data_dir)
        n = save_activity_rows(conn, pd.DataFrame(), source="test")
        conn.close()
        assert n == 0

    def test_batch_insert_multiple_rows(self, tmp_data_dir):
        rows = [{"date": f"2024-01-{i:02d}", "steps": float(i * 1000)} for i in range(1, 6)]
        df = pd.DataFrame(rows)
        conn = get_activity_store(tmp_data_dir)
        n = save_activity_rows(conn, df, source="batch_test")
        conn.close()
        assert n == 5
        result = query_activity(tmp_data_dir, "2024-01-01", "2024-01-05")
        assert len(result) == 5


class TestSaveLabResults:
    def test_basic_insert(self, tmp_data_dir):
        results = [
            {
                "test_name": "Glucose",
                "value": 90.0,
                "unit": "mg/dL",
                "reference_low": 70.0,
                "reference_high": 100.0,
                "panel_date": "2024-03-14",
                "source_file": "test.pdf",
            }
        ]
        conn = get_lab_store(tmp_data_dir)
        n = save_lab_results(conn, results)
        conn.close()
        assert n == 1

    def test_empty_list_returns_zero(self, tmp_data_dir):
        conn = get_lab_store(tmp_data_dir)
        n = save_lab_results(conn, [])
        conn.close()
        assert n == 0

    def test_query_by_date_range(self, tmp_data_dir):
        results = [
            {"test_name": "HDL-C", "value": 50.0, "unit": "mg/dL",
             "reference_low": 40.0, "reference_high": None,
             "panel_date": "2024-01-15", "source_file": "a.pdf"},
            {"test_name": "LDL-C", "value": 120.0, "unit": "mg/dL",
             "reference_low": None, "reference_high": 130.0,
             "panel_date": "2024-06-15", "source_file": "b.pdf"},
        ]
        conn = get_lab_store(tmp_data_dir)
        save_lab_results(conn, results)
        conn.close()
        df = query_lab_results(tmp_data_dir, "2024-01-01", "2024-03-31")
        assert len(df) == 1
        assert df.iloc[0]["test_name"] == "HDL-C"
