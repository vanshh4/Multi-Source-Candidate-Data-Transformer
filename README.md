# Candidate Transformer

A configurable candidate transformation pipeline that converts recruiter-provided structured data and resume files into a validated canonical candidate record and runtime-projected JSON outputs.

The project is organized into phased layers:

```text
Phase 1: Contracts and sample configs
Phase 2: Source readers
Phase 3: Field extraction
Phase 4: Normalization
Phase 5: Canonical candidate building, merge, provenance, validation
Phase 6: Runtime projection layer and full pipeline CLI
UI Layer: Minimal Streamlit upload/run/download surface
```

---

## 1. What This Project Does

This project takes candidate data from:

```text
1. Recruiter CSV
2. Resume DOCX / PDF / TXT
3. Runtime projection YAML config
```

and produces:

```text
1. Source-reading output
2. Extracted field candidates
3. Normalized field candidates
4. Canonical candidate JSON
5. Runtime-projected JSON output
```

The key architectural idea is:

```text
Stable internal canonical schema
        +
Runtime projection configuration
        =
Custom output format without changing code
```

---

## 2. Project Folder Structure

Expected project structure:

```text
candidate_transformer/
│
├── configs/
│   ├── sample_input_manifest.yaml
│   ├── default_projection.yaml
│   ├── minimal_recruiter_view.yaml
│   └── client_custom_schema.yaml
│
├── schemas/
│   ├── canonical_candidate.schema.json
│   └── projection_config.schema.json
│
├── data/
│   ├── samples/
│   │   ├── recruiter.csv
│   │   ├── vansh_resume.docx
│   │   ├── resume.pdf                  # optional
│   │   └── sample_resume_text.txt
│   │
│   ├── expected/
│   │   ├── source_reading_example.json
│   │   ├── extraction_example.json
│   │   ├── normalization_example.json
│   │   ├── canonical_candidate_example.json
│   │   ├── default_projection_output_example.json
│   │   ├── minimal_recruiter_view_output_example.json
│   │   └── client_custom_schema_output_example.json
│   │
│   ├── outputs/
│   │   └── ui/
│   │
│   ├── ui_uploads/
│   └── ui_runs/
│
├── src/
│   └── transformer/
│       ├── readers/
│       ├── extractors/
│       ├── normalizers/
│       ├── canonical/
│       ├── merge/
│       ├── provenance/
│       ├── validation/
│       ├── projection/
│       ├── ui_helpers/
│       ├── pipeline.py
│       └── cli.py
│
├── tests/
│
├── ui/
│   ├── __init__.py
│   └── streamlit_app.py
│
├── requirements.txt
└── README.md
```

---

## 3. Fresh System Setup

### 3.1 Clone or copy the project

Open a terminal in your desired workspace and place the project folder there.

Example:

```bash
cd path/to/your/workspace
```

Then open the project root:

```bash
cd candidate_transformer
```

---

### 3.2 Create a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run PowerShell as administrator and use:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 3.3 Install dependencies

Make sure `requirements.txt` contains at least:

```txt
pandas
openpyxl
python-docx
pdfplumber
PyYAML
jsonschema
pytest
streamlit
```

Then install:

```bash
pip install -r requirements.txt
```

---

## 4. Required Input Files Before Running

Before running the pipeline, confirm these files exist:

```text
configs/sample_input_manifest.yaml
configs/default_projection.yaml
configs/minimal_recruiter_view.yaml
configs/client_custom_schema.yaml

schemas/canonical_candidate.schema.json
schemas/projection_config.schema.json

data/samples/recruiter.csv
data/samples/vansh_resume.docx
```

Optional but useful files:

```text
data/samples/sample_resume_text.txt
data/samples/resume.pdf
```

---

## 5. Important Manifest Path Check

Open:

```text
configs/sample_input_manifest.yaml
```

Make sure the resume path uses the updated file name:

```yaml
inputs:
  recruiter_csv:
    path: data/samples/recruiter.csv
    required: false
    source_id: recruiter_csv
    source_type: recruiter_csv

  resume:
    path: data/samples/vansh_resume.docx
    type: docx
    required: false
    source_id: resume_docx
    source_type: resume_docx

projection:
  config_path: configs/default_projection.yaml

output:
  path: data/outputs/default_candidate_output.json
  pretty_print: true
```

If your resume file has a different name or location, update only:

```yaml
inputs:
  resume:
    path: data/samples/vansh_resume.docx
```

---

## 6. Set PYTHONPATH

From the project root, most commands should be run with:

### macOS / Linux

```bash
export PYTHONPATH=src
```

### Windows PowerShell

```powershell
$env:PYTHONPATH="src"
```

You can also prefix commands directly:

```bash
PYTHONPATH=src pytest tests
```

---

## 7. Run All Tests

Run the full test suite:

```bash
set PYTHONPATH=src && pytest tests
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
pytest tests
```

Expected result:

```text
All tests passed
```

The test suite covers:

```text
Phase 2: readers and router
Phase 3: extractors
Phase 4: normalizers
Phase 5: canonical builder, merge, provenance, validation
Phase 6: runtime projection
UI manifest builder
```

---

## 8. Run Source-Reading Mode

This command only reads the configured input sources and produces source status output.

```bash
PYTHONPATH=src python -m transformer.cli \
  --manifest configs/sample_input_manifest.yaml
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m transformer.cli `
  --manifest configs/sample_input_manifest.yaml
```

Expected output file:

```text
data/outputs/source_reading_output.json
```

Expected terminal output should look similar to:

```text
Source reading completed.
Overall status: completed

Sources:
- recruiter_csv (recruiter_csv): ok
- resume_docx (resume_docx): ok

Output written to: data/outputs/source_reading_output.json
```

Expected JSON structure:

```json
{
  "run_id": "sample_candidate_run_001",
  "description": "Phase 2 source-reading output. Extraction, normalization, merge, and projection are not performed here.",
  "sources": [
    {
      "source_id": "recruiter_csv",
      "source_type": "recruiter_csv",
      "source_name": "recruiter.csv",
      "path": "data/samples/recruiter.csv",
      "status": "ok",
      "content_type": "tabular",
      "metadata": {
        "row_count": 1,
        "column_count": 10
      },
      "warnings": [],
      "errors": []
    },
    {
      "source_id": "resume_docx",
      "source_type": "resume_docx",
      "source_name": "vansh_resume.docx",
      "path": "data/samples/vansh_resume.docx",
      "status": "ok",
      "content_type": "text",
      "metadata": {
        "has_extractable_text": true
      },
      "warnings": [],
      "errors": []
    }
  ],
  "overall_status": "completed",
  "warnings": [],
  "errors": []
}
```

---

## 9. Run Full Pipeline With Default Projection

This runs the complete pipeline:

```text
read → extract → normalize → canonical build → projection
```

Command:

```bash
PYTHONPATH=src python -m transformer.cli \
  --manifest configs/sample_input_manifest.yaml \
  --project \
  --output data/outputs/projected_candidate_output.json
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m transformer.cli `
  --manifest configs/sample_input_manifest.yaml `
  --project `
  --output data/outputs/projected_candidate_output.json
```

Expected output file:

```text
data/outputs/projected_candidate_output.json
```

Expected terminal output:

```text
Candidate transformer pipeline completed.
Status: completed
Projected fields: <number_of_projected_fields>

Output written to: data/outputs/projected_candidate_output.json
```

Expected JSON structure:

```json
{
  "run_id": "sample_candidate_run_001",
  "status": "completed",
  "projected_output": {
    "candidate_id": "cand_xxxxxxxxxx",
    "full_name": "Sample Candidate",
    "emails": [
      "sample@example.com"
    ],
    "phones": [
      "+919999999999"
    ],
    "location": {
      "city": "Delhi",
      "region": "Delhi",
      "country": "IN",
      "raw": "Delhi, India"
    },
    "links": {
      "linkedin": "https://linkedin.com/in/samplecandidate",
      "github": null,
      "portfolio": null,
      "other": []
    },
    "headline": "Data Analyst Intern",
    "years_experience": 1.0,
    "skills": [
      {
        "name": "Python",
        "confidence": 0.9,
        "sources": [
          "resume_docx"
        ]
      }
    ],
    "overall_confidence": 0.87,
    "_provenance": {},
    "_confidence": {}
  },
  "warnings": [],
  "errors": []
}
```

Actual values will depend on your recruiter CSV and resume contents.

---

## 10. Run Full Pipeline With Debug Intermediates

Use this once to inspect the complete pipeline output.

```bash
PYTHONPATH=src python -m transformer.cli \
  --manifest configs/sample_input_manifest.yaml \
  --project \
  --include-intermediate \
  --output data/outputs/full_debug_output.json
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m transformer.cli `
  --manifest configs/sample_input_manifest.yaml `
  --project `
  --include-intermediate `
  --output data/outputs/full_debug_output.json
```

Expected output file:

```text
data/outputs/full_debug_output.json
```

This file includes:

```text
source_results
field_candidates
normalized_candidates
canonical_candidate
projected_output
warnings
errors
```

Use this file to debug each phase.

---

## 11. Run Full Pipeline With Each Projection Config

### 11.1 Default Projection

```bash
PYTHONPATH=src python -m transformer.cli \
  --manifest configs/sample_input_manifest.yaml \
  --project \
  --config configs/default_projection.yaml \
  --output data/outputs/default_projection_output.json
```

Expected output:

```text
data/outputs/default_projection_output.json
```

---

### 11.2 Minimal Recruiter View

```bash
PYTHONPATH=src python -m transformer.cli \
  --manifest configs/sample_input_manifest.yaml \
  --project \
  --config configs/minimal_recruiter_view.yaml \
  --output data/outputs/minimal_recruiter_output.json
```

Expected output:

```text
data/outputs/minimal_recruiter_output.json
```

Expected projected fields:

```json
{
  "id": "cand_xxxxxxxxxx",
  "name": "Sample Candidate",
  "email": ["sample@example.com"],
  "phone": ["+919999999999"],
  "city": "Delhi",
  "headline": "Data Analyst Intern",
  "years_experience": 1.0,
  "skills": [],
  "linkedin": "https://linkedin.com/in/samplecandidate",
  "_confidence": {}
}
```

`_provenance` should not appear if provenance is disabled in the minimal recruiter config.

---

### 11.3 Client Custom Schema

```bash
PYTHONPATH=src python -m transformer.cli \
  --manifest configs/sample_input_manifest.yaml \
  --project \
  --config configs/client_custom_schema.yaml \
  --output data/outputs/client_custom_output.json
```

Expected output:

```text
data/outputs/client_custom_output.json
```

Expected projected fields:

```json
{
  "external_candidate_key": "cand_xxxxxxxxxx",
  "candidate_name": "Sample Candidate",
  "primary_emails": ["sample@example.com"],
  "mobile_numbers": ["+919999999999"],
  "current_city": "Delhi",
  "current_region": "Delhi",
  "country_code": "IN",
  "linkedin_url": "https://linkedin.com/in/samplecandidate",
  "github_url": null,
  "profile_summary": "Data Analyst Intern",
  "total_experience_years": 1.0,
  "skill_set": [],
  "work_history": [],
  "academic_history": [],
  "record_confidence": 0.87,
  "_provenance": {},
  "_confidence": {}
}
```

---

## 12. Run the Streamlit UI

### 12.1 Install Streamlit

If Streamlit is not installed:

```bash
pip install streamlit
```

Or install everything:

```bash
pip install -r requirements.txt
```

---

### 12.2 Start the UI

```bash
set PYTHONPATH=src && python -m streamlit run ui\streamlit_app.py
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
streamlit run ui/streamlit_app.py
```

A browser window should open at:

```text
http://localhost:8501
```

---

### 12.3 Use the UI

In the UI:

1. Upload recruiter CSV:

```text
data/samples/recruiter.csv
```

2. Upload resume:

```text
data/samples/vansh_resume.docx
```

3. Select projection config:

```text
Default Projection
Minimal Recruiter View
Client Custom Schema
```

4. Click:

```text
Run Transformer
```

5. Inspect projected JSON output.

6. Click:

```text
Download output JSON
```

---

## 13. UI Output Locations

The UI writes uploaded and generated files here:

```text
data/ui_uploads/<run_id>/
data/ui_runs/<run_id>/manifest.yaml
data/outputs/ui/<run_id>_projected_output.json
```

These should not be committed to Git because uploaded resumes and recruiter files may contain sensitive data.

Recommended `.gitignore` entries:

```gitignore
data/ui_uploads/*
!data/ui_uploads/.gitkeep

data/ui_runs/*
!data/ui_runs/.gitkeep

data/outputs/ui/*
!data/outputs/ui/.gitkeep

__pycache__/
*.pyc
.pytest_cache/
.streamlit/
```

---

## 14. Expected Output Files Generated by Commands

Running the commands above can produce:

```text
data/outputs/source_reading_output.json
data/outputs/projected_candidate_output.json
data/outputs/full_debug_output.json
data/outputs/default_projection_output.json
data/outputs/minimal_recruiter_output.json
data/outputs/client_custom_output.json
data/outputs/ui/<run_id>_projected_output.json
```

Expected reference examples are stored in:

```text
data/expected/source_reading_example.json
data/expected/extraction_example.json
data/expected/normalization_example.json
data/expected/canonical_candidate_example.json
data/expected/default_projection_output_example.json
data/expected/minimal_recruiter_view_output_example.json
data/expected/client_custom_schema_output_example.json
```

---

## 15. Troubleshooting

### 15.1 `ModuleNotFoundError: No module named 'transformer'`

Set `PYTHONPATH`:

```bash
export PYTHONPATH=src
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
```

Then rerun the command.

---

### 15.2 `resume_docx status: missing`

Check the resume path in:

```text
configs/sample_input_manifest.yaml
```

It should be:

```yaml
path: data/samples/vansh_resume.docx
```

Also confirm the file actually exists:

```text
data/samples/vansh_resume.docx
```

---

### 15.3 Schema file missing

Confirm these files exist:

```text
schemas/canonical_candidate.schema.json
schemas/projection_config.schema.json
```

If they are in the root by mistake, move them to:

```text
schemas/
```

---

### 15.4 Streamlit command not found

Install Streamlit:

```bash
pip install streamlit
```

Then rerun:

```bash
PYTHONPATH=src streamlit run ui/streamlit_app.py
```

---

### 15.5 PDF produces no text

If a PDF is scanned or image-based, text extraction may return no text. Use a DOCX file for the first successful test. OCR support is not included in the minimal pipeline.

---

## 16. Validation Checklist

Before calling the project complete, verify:

```text
[ ] pip install -r requirements.txt works
[ ] PYTHONPATH=src pytest tests passes
[ ] Source-reading CLI works
[ ] Full pipeline CLI works
[ ] Default projection works
[ ] Minimal recruiter projection works
[ ] Client custom projection works
[ ] Streamlit UI opens
[ ] UI upload-run-download workflow works
[ ] Manifest references vansh_resume.docx correctly
[ ] schemas/ contains both JSON schema files
```

---

## 17. Current Pipeline Summary

```text
Recruiter CSV + Resume DOCX/PDF/TXT
        ↓
Source readers
        ↓
Field extractors
        ↓
Normalizers
        ↓
Canonical candidate builder
        ↓
Runtime projection layer
        ↓
Projected JSON output
        ↓
CLI / Streamlit UI
```

---

## 18. Notes on Sensitive Data

Recruiter CSVs and resumes may contain personal information. Avoid committing the following folders:

```text
data/ui_uploads/
data/ui_runs/
data/outputs/ui/
```

For demos, use anonymized data wherever possible.

---

## 19. Quick Command Reference

Run all tests:

```bash
set PYTHONPATH=src && pytest tests
```

Run source reading:

```bash
set PYTHONPATH=src && python -m transformer.cli --manifest configs/sample_input_manifest.yaml
```

Run full pipeline:

```bash
set PYTHONPATH=src && python -m transformer.cli --manifest configs\sample_input_manifest.yaml --project --output data\outputs\projected_candidate_output.json
```

Run full debug output:

```bash
set PYTHONPATH=src && python -m transformer.cli --manifest configs/sample_input_manifest.yaml --project --include-intermediate --output data/outputs/full_debug_output.json   
```

Run minimal recruiter output:

```bash
set PYTHONPATH=src && python -m transformer.cli --manifest configs/sample_input_manifest.yaml --project --config configs/minimal_recruiter_view.yaml --output data/outputs/minimal_recruiter_output.json
```

Run UI:

```bash
set PYTHONPATH=src && python -m streamlit run ui\streamlit_app.py
```
