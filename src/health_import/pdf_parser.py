"""Parse blood panel PDFs and extract lab results."""

from __future__ import annotations

import io
import re
from pathlib import Path


# Common biomarker name normalizations (various lab naming conventions)
BIOMARKER_ALIASES = {
    "ldl": "LDL-C",
    "ldl-c": "LDL-C",
    "ldl cholesterol": "LDL-C",
    "hdl": "HDL-C",
    "hdl-c": "HDL-C",
    "hdl cholesterol": "HDL-C",
    "triglycerides": "Triglycerides",
    "trigs": "Triglycerides",
    "total cholesterol": "Total Cholesterol",
    "cholesterol": "Total Cholesterol",
    "glucose": "Glucose",
    "blood glucose": "Glucose",
    "hba1c": "HbA1c",
    "a1c": "HbA1c",
    "hemoglobin a1c": "HbA1c",
    "rbc": "RBC",
    "wbc": "WBC",
    "hemoglobin": "Hemoglobin",
    "hgb": "Hemoglobin",
    "hematocrit": "Hematocrit",
    "hct": "Hematocrit",
    "platelets": "Platelets",
    "creatinine": "Creatinine",
    "bun": "BUN",
    "albumin": "Albumin",
    "alt": "ALT",
    "ast": "AST",
    "vitamin d": "Vitamin D",
    "vit d": "Vitamin D",
    "b12": "Vitamin B12",
    "vitamin b12": "Vitamin B12",
}


def _normalize_name(raw: str) -> str:
    """Map raw test name to canonical biomarker name."""
    key = raw.lower().strip().replace("-", " ").replace("_", " ")
    return BIOMARKER_ALIASES.get(key, raw.strip())


def _parse_value(text: str) -> float | None:
    """Extract numeric value from text like '125', '125.5', '<5', '>200'."""
    if not text or not isinstance(text, str):
        return None
    text = str(text).strip()
    # Remove common prefixes
    text = re.sub(r"^[<>=]\s*", "", text)
    # Extract first number
    m = re.search(r"([-]?\d+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _parse_ref_range(text: str) -> tuple[float | None, float | None]:
    """Parse reference range like '70-99', '70 - 99', '< 5.7', '12.0-15.5'."""
    if not text or not isinstance(text, str):
        return (None, None)
    text = str(text).strip()
    # Match patterns: 70-99, 70 - 99, 12.0-15.5
    m = re.search(r"([\d.]+)\s*[-–—]\s*([\d.]+)", text)
    if m:
        try:
            return (float(m.group(1)), float(m.group(2)))
        except ValueError:
            pass
    # Single value: "< 5.7" or "> 200"
    v = _parse_value(text)
    if v is not None:
        if "<" in text:
            return (None, v)
        if ">" in text:
            return (v, None)
    return (None, None)


def _infer_columns(headers: list, rows: list) -> dict[str, int]:
    """Map canonical keys to column indices based on header names."""
    mapping = {}
    for i, h in enumerate(headers):
        if not h:
            continue
        h_lower = str(h).lower()
        if "test" in h_lower or "component" in h_lower or "name" in h_lower or "lab" in h_lower:
            mapping["test_name"] = i
        elif "result" in h_lower or "value" in h_lower or "level" in h_lower:
            mapping["value"] = i
        elif "unit" in h_lower or "units" in h_lower:
            mapping["unit"] = i
        elif "reference" in h_lower or "range" in h_lower or "ref" in h_lower:
            mapping["reference"] = i
    return mapping


def _extract_from_tables(pdf_bytes: bytes) -> list[dict]:
    """Extract lab results from PDF tables."""
    import pdfplumber

    results = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables or []:
                if not table or len(table) < 2:
                    continue
                headers = [str(h).strip() if h else "" for h in table[0]]
                mapping = _infer_columns(headers, table[1:])
                if "test_name" not in mapping or "value" not in mapping:
                    continue
                for row in table[1:]:
                    if not row:
                        continue
                    test_raw = row[mapping["test_name"]] if mapping["test_name"] < len(row) else ""
                    if not test_raw or not str(test_raw).strip():
                        continue
                    value = _parse_value(
                        row[mapping["value"]] if mapping["value"] < len(row) else ""
                    )
                    if value is None:
                        continue
                    unit = ""
                    if "unit" in mapping and mapping["unit"] < len(row):
                        unit = str(row[mapping["unit"]] or "").strip()
                    ref_low, ref_high = None, None
                    if "reference" in mapping and mapping["reference"] < len(row):
                        ref_low, ref_high = _parse_ref_range(row[mapping["reference"]] or "")
                    results.append({
                        "test_name": _normalize_name(str(test_raw)),
                        "value": value,
                        "unit": unit or "",
                        "reference_low": ref_low,
                        "reference_high": ref_high,
                    })
    return results


def _extract_date_from_text(pdf_bytes: bytes) -> str | None:
    """Try to find a date in the PDF (e.g. report date, collection date)."""
    import pdfplumber

    date_pattern = re.compile(
        r"(?:date|collected|report|drawn)[:\s]*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",
        re.I
    )
    alt_pattern = re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})")
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for m in date_pattern.finditer(text):
                try:
                    mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    year = y if y > 100 else 2000 + y
                    return f"{year}-{mo:02d}-{d:02d}"
                except (ValueError, IndexError):
                    pass
            for m in alt_pattern.finditer(text):
                try:
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    return f"{y}-{mo:02d}-{d:02d}"
                except (ValueError, IndexError):
                    pass
    return None


def parse_lab_pdf(
    file_or_bytes: bytes | str | Path,
    filename: str | None = None,
    panel_date: str | None = None,
) -> tuple[list[dict], list[str]]:
    """
    Parse a blood panel PDF and extract lab results.
    Returns (list of result dicts, list of errors).
    Each result: test_name, value, unit, reference_low, reference_high, panel_date, source_file.
    """
    errors = []
    pdf_bytes: bytes

    if isinstance(file_or_bytes, (str, Path)):
        path = Path(file_or_bytes)
        if not path.exists():
            return [], [f"File not found: {path}"]
        pdf_bytes = path.read_bytes()
        filename = filename or path.name
    elif isinstance(file_or_bytes, bytes):
        pdf_bytes = file_or_bytes
    else:
        return [], ["Unsupported input type"]

    try:
        results = _extract_from_tables(pdf_bytes)
    except Exception as e:
        return [], [f"PDF parsing error: {e}"]

    if not results:
        errors.append("No lab results extracted. PDF format may not be supported.")

    date_str: str | None = None
    if panel_date:
        # Validate/normalize user-supplied date to ISO YYYY-MM-DD
        from datetime import datetime
        normalized = None
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y"):
            try:
                normalized = datetime.strptime(panel_date.strip(), fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        if normalized is None:
            errors.append(
                f"Invalid panel_date '{panel_date}'. Expected YYYY-MM-DD. Using auto-detected date instead."
            )
        else:
            date_str = normalized

    if date_str is None:
        date_str = _extract_date_from_text(pdf_bytes)
    if not date_str:
        errors.append("Could not determine panel date. You may need to enter it manually.")

    for r in results:
        r["panel_date"] = date_str or ""
        r["source_file"] = filename or ""

    return results, errors
