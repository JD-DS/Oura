"""Parse blood panel PDFs and extract lab results."""

from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import TypedDict


class ColumnMapping(TypedDict, total=False):
    """Column mapping configuration for PDF extraction."""
    test_name: list[str]  # Header patterns for test name column
    value: list[str]       # Header patterns for result/value column
    unit: list[str]        # Header patterns for unit column
    reference: list[str]   # Header patterns for reference range column


# Default column header patterns (case-insensitive)
DEFAULT_COLUMN_PATTERNS: ColumnMapping = {
    "test_name": ["test", "component", "name", "lab", "analyte", "biomarker", "item"],
    "value": ["result", "value", "level", "your value", "observed", "finding"],
    "unit": ["unit", "units", "uom"],
    "reference": ["reference", "range", "ref", "normal", "standard"],
}


# Common biomarker name normalizations (various lab naming conventions)
BIOMARKER_ALIASES = {
    "ldl": "LDL-C",
    "ldl-c": "LDL-C",
    "ldl cholesterol": "LDL-C",
    "ldl calculated": "LDL-C",
    "ldl chol calc": "LDL-C",
    "hdl": "HDL-C",
    "hdl-c": "HDL-C",
    "hdl cholesterol": "HDL-C",
    "triglycerides": "Triglycerides",
    "trigs": "Triglycerides",
    "triglyceride": "Triglycerides",
    "total cholesterol": "Total Cholesterol",
    "cholesterol": "Total Cholesterol",
    "cholesterol total": "Total Cholesterol",
    "glucose": "Glucose",
    "blood glucose": "Glucose",
    "glucose serum": "Glucose",
    "fasting glucose": "Glucose",
    "hba1c": "HbA1c",
    "a1c": "HbA1c",
    "hemoglobin a1c": "HbA1c",
    "glycated hemoglobin": "HbA1c",
    "rbc": "RBC",
    "red blood cell": "RBC",
    "red blood cell count": "RBC",
    "wbc": "WBC",
    "white blood cell": "WBC",
    "white blood cell count": "WBC",
    "hemoglobin": "Hemoglobin",
    "hgb": "Hemoglobin",
    "hb": "Hemoglobin",
    "hematocrit": "Hematocrit",
    "hct": "Hematocrit",
    "platelets": "Platelets",
    "platelet count": "Platelets",
    "plt": "Platelets",
    "creatinine": "Creatinine",
    "creat": "Creatinine",
    "bun": "BUN",
    "blood urea nitrogen": "BUN",
    "albumin": "Albumin",
    "alb": "Albumin",
    "alt": "ALT",
    "alanine aminotransferase": "ALT",
    "sgpt": "ALT",
    "ast": "AST",
    "aspartate aminotransferase": "AST",
    "sgot": "AST",
    "vitamin d": "Vitamin D",
    "vit d": "Vitamin D",
    "25-hydroxyvitamin d": "Vitamin D",
    "vitamin d 25-oh": "Vitamin D",
    "b12": "Vitamin B12",
    "vitamin b12": "Vitamin B12",
    "cobalamin": "Vitamin B12",
    "tsh": "TSH",
    "thyroid stimulating hormone": "TSH",
    "t3": "T3",
    "t4": "T4",
    "free t4": "Free T4",
    "ft4": "Free T4",
    "iron": "Iron",
    "serum iron": "Iron",
    "ferritin": "Ferritin",
    "tibc": "TIBC",
    "total iron binding capacity": "TIBC",
    "transferrin saturation": "Transferrin Saturation",
    "magnesium": "Magnesium",
    "mag": "Magnesium",
    "calcium": "Calcium",
    "ca": "Calcium",
    "potassium": "Potassium",
    "k": "Potassium",
    "sodium": "Sodium",
    "na": "Sodium",
    "chloride": "Chloride",
    "cl": "Chloride",
    "uric acid": "Uric Acid",
    "egfr": "eGFR",
    "estimated gfr": "eGFR",
    "glomerular filtration rate": "eGFR",
    "hs-crp": "hs-CRP",
    "c-reactive protein": "hs-CRP",
    "crp": "hs-CRP",
    "homocysteine": "Homocysteine",
    "insulin": "Insulin",
    "fasting insulin": "Insulin",
    "apolipoprotein b": "ApoB",
    "apob": "ApoB",
    "apo b": "ApoB",
    "lipoprotein a": "Lp(a)",
    "lp(a)": "Lp(a)",
    "lpa": "Lp(a)",
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


def _infer_columns(
    headers: list,
    rows: list,
    column_patterns: ColumnMapping | None = None,
) -> dict[str, int]:
    """Map canonical keys to column indices based on header names."""
    patterns = column_patterns or DEFAULT_COLUMN_PATTERNS
    mapping = {}
    for i, h in enumerate(headers):
        if not h:
            continue
        h_lower = str(h).lower().strip()
        for key, pattern_list in patterns.items():
            if key in mapping:
                continue
            for pattern in pattern_list:
                if pattern.lower() in h_lower:
                    mapping[key] = i
                    break
    return mapping


def load_extraction_config(config_path: str | Path | None = None) -> ColumnMapping | None:
    """Load custom column mapping from JSON config file."""
    if config_path is None:
        return None
    path = Path(config_path)
    if not path.exists():
        return None
    try:
        with open(path) as f:
            config = json.load(f)
        return config.get("column_patterns")
    except (json.JSONDecodeError, KeyError):
        return None


def _extract_from_text_lines(pdf_bytes: bytes) -> list[dict]:
    """
    Fallback extraction: parse text lines for pattern: TEST_NAME ... VALUE UNIT RANGE.
    Used when table extraction fails (e.g., non-tabular PDF layouts).
    """
    import pdfplumber

    results = []
    line_pattern = re.compile(
        r"^([A-Za-z][A-Za-z0-9\s\-\(\)]+?)\s+"
        r"([<>]?\s*\d+\.?\d*)\s*"
        r"([A-Za-z/%µμ]+)?\s*"
        r"([\d.]+\s*[-–—]\s*[\d.]+)?",
        re.MULTILINE,
    )
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for m in line_pattern.finditer(text):
                test_raw = m.group(1).strip()
                value = _parse_value(m.group(2))
                if value is None:
                    continue
                unit = (m.group(3) or "").strip()
                ref_low, ref_high = _parse_ref_range(m.group(4) or "")
                results.append({
                    "test_name": _normalize_name(test_raw),
                    "value": value,
                    "unit": unit,
                    "reference_low": ref_low,
                    "reference_high": ref_high,
                })
    return results


def _extract_from_tables(
    pdf_bytes: bytes,
    column_patterns: ColumnMapping | None = None,
) -> list[dict]:
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
                mapping = _infer_columns(headers, table[1:], column_patterns)
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
    config_path: str | Path | None = None,
) -> tuple[list[dict], list[str]]:
    """
    Parse a blood panel PDF and extract lab results.

    Args:
        file_or_bytes: PDF file path or raw bytes
        filename: Optional filename for source tracking
        panel_date: Override panel date (YYYY-MM-DD); auto-detected if None
        config_path: Optional path to JSON config with custom column_patterns

    Returns:
        (list of result dicts, list of errors/warnings).
        Each result: test_name, value, unit, reference_low, reference_high, panel_date, source_file.

    Config file format (optional):
        {
            "column_patterns": {
                "test_name": ["test", "analyte", "biomarker"],
                "value": ["result", "value", "observed"],
                "unit": ["unit", "units"],
                "reference": ["reference", "range", "normal"]
            }
        }
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

    column_patterns = load_extraction_config(config_path)

    try:
        results = _extract_from_tables(pdf_bytes, column_patterns)
    except Exception as e:
        return [], [f"PDF parsing error: {e}"]

    if not results:
        try:
            results = _extract_from_text_lines(pdf_bytes)
            if results:
                errors.append("Used text-line fallback; results may be less accurate.")
        except Exception:
            pass

    if not results:
        errors.append(
            "No lab results extracted. PDF format may not be supported. "
            "Try providing a custom config file with column_patterns."
        )

    date_str = panel_date or _extract_date_from_text(pdf_bytes)
    if not date_str:
        errors.append("Could not determine panel date. You may need to enter it manually.")

    for r in results:
        r["panel_date"] = date_str or ""
        r["source_file"] = filename or ""

    return results, errors
