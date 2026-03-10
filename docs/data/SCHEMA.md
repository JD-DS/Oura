# External Health Data Schema

Schema definitions for Excel and PDF imports. Used by the import pipeline and validated on upload.

---

## Excel / CSV — Activity & Nutrition

Expected columns for calories, steps, workouts, and other manual-tracking data.

### Required

| Column      | Type   | Description              | Example  |
|-------------|--------|--------------------------|----------|
| `date`      | date   | Day the data applies to | 2024-03-15 |
| `steps`     | int    | Step count              | 8542     |
| `calories`  | float  | Total calories (kcal)   | 2100.5   |

### Optional (aliases supported)

| Canonical  | Aliases                         | Type   | Description                  |
|------------|----------------------------------|--------|------------------------------|
| `date`     | day, Day, Date                   | date   | Row date                     |
| `steps`    | Steps, step_count                | int    | Steps                        |
| `calories` | Calories, cal, kcal              | float  | Calories                     |
| `workouts` | Workouts, workout_min, exercise  | int/float | Workout minutes           |
| `weight`   | Weight, weight_kg                | float  | Body weight (kg)             |
| `sleep_hours` | sleep, Sleep, hours_slept     | float  | Self-reported sleep hours   |
| `notes`    | Notes, memo                      | str    | Free text                    |

### Date formats supported

- `YYYY-MM-DD`
- `MM/DD/YYYY`
- `DD/MM/YYYY`
- Excel date serial number

### Validation rules

- `date` must parse to a valid date
- Numeric columns: NaN/empty allowed; invalid values rejected
- Duplicate dates: last row wins (incremental update behavior)

---

## Blood Panel PDF — Lab Results

Extracted biomarkers mapped to a common schema.

### Schema per result

| Field           | Type  | Description                    |
|-----------------|-------|--------------------------------|
| `test_name`     | str   | Biomarker name (e.g. LDL-C)   |
| `value`         | float | Numeric result                |
| `unit`          | str   | e.g. mg/dL, mmol/L           |
| `reference_low` | float | Lower ref (optional)         |
| `reference_high`| float | Upper ref (optional)         |
| `panel_date`    | date  | Date of draw                  |
| `source_file`   | str   | Original PDF filename        |

### Common biomarkers (name normalization)

- Lipids: LDL-C, HDL-C, triglycerides, total cholesterol
- Metabolic: glucose, HbA1c
- CBC: RBC, WBC, hemoglobin, hematocrit, platelets
- Metabolic panel: creatinine, BUN, albumin, ALT, AST
- Vitamins: vitamin D, B12

---

## Storage

- **Excel data**: `activity` table — one row per date, merged from all imports
- **Lab results**: `lab_results` table — one row per biomarker per panel
