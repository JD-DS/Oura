# Sample Data Files

This directory holds **redacted sample files** for schema documentation and development. Real user data (Excel, PDF lab results, workout logs) stays in `data/` at the project root and is never committed.

## Samples

| File | Purpose |
|------|---------|
| `sample_activity.csv` | Example CSV with date, steps, calories, workouts — use to test the import pipeline |
| `sample_activity.xlsx` | (Optional) Same in Excel format |
| `sample_lab_results.pdf` | (Planned) Redacted blood panel PDF — layout reference for biomarker extraction |

## Schema

See [SCHEMA.md](SCHEMA.md) for expected column names, date formats, and validation rules.

## Usage

- **Development:** Use these samples to test the import pipeline without real data.
- **Framework users:** Replace with their own file formats; see Phase 4 in [TODO.md](../TODO.md) for the AI-powered file wrapper that can handle arbitrary formats on the fly.
