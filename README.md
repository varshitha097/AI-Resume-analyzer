# Improved AI Resume Analyzer

This is a VS Code-ready AI Resume Analyzer project built without any generative LLM. It uses PDF parsing, NLP-style extraction, skill taxonomy normalization, optional sentence embeddings, section-wise scoring, gap analysis and candidate ranking.

## Improvements in this version

- Better PDF extraction using PyMuPDF with pdfplumber fallback.
- Optional OCR fallback for scanned PDF resumes.
- Expanded `skills_taxonomy.json` with aliases such as `ML = Machine Learning`, `React.js = React`, `Postgres = PostgreSQL`.
- Section-wise resume parsing for skills, experience, education, projects and certifications.
- JD processing to extract required skills and minimum experience.
- Better similarity engine: sentence-transformers when available, TF-IDF fallback when not available.
- Weighted scoring formula:
  - Skills: 45%
  - Experience: 20%
  - Projects: 15%
  - Overall semantic match: 10%
  - Education: 5%
  - Certifications: 5%
- Missing skills and matched skills detection.
- Candidate ranking for multiple resumes.
- Domain detection: Python Developer, Full Stack, Data Analyst, ML Engineer, DevOps, QA and more.
- CSV export for ranking results.

## Folder structure

```text
ai_resume_analyzer_improved/
  app.py
  requirements.txt
  run_windows_cmd.bat
  run_linux_mac.sh
  config/
    skills_taxonomy.json
    domain_profiles.json
  src/
    parser.py
    sectionizer.py
    taxonomy.py
    extractor.py
    similarity.py
    scorer.py
    domain.py
    pipeline.py
    report.py
  static/
    index.html
    styles.css
    script.js
  samples/
    sample_jd.txt
    sample_resume_text.txt
  tests/
    test_core.py
```

## How to run in Windows CMD

Open CMD in the project folder and run:

```cmd
run_windows_cmd.bat
```

Then open:

```text
http://127.0.0.1:5000
```

## Manual setup

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

For higher semantic accuracy, install the advanced packages:

```cmd
pip install -r requirements-advanced.txt
```

## If sentence-transformers is slow or internet is unavailable

The project automatically falls back to TF-IDF similarity if sentence-transformers cannot load. So the project still works.

## Optional OCR setup for scanned PDFs

Python OCR packages are listed in `requirements-advanced.txt`, but OCR also requires system tools:

- Tesseract OCR
- Poppler

If they are not installed, OCR is skipped and normal PDF parsing still works.

## Accuracy tuning

To improve accuracy further for your college/project demo:

1. Add more skills and synonyms in `config/skills_taxonomy.json`.
2. Add more domains in `config/domain_profiles.json`.
3. Adjust weights in `src/scorer.py`.
4. Add test resumes and expected results in `tests/`.
5. Keep JD text clear with required skills and experience.

## API endpoints

- `GET /` - web UI
- `GET /api/health` - engine status
- `POST /api/analyze` - analyze uploaded resumes with JD
- `GET /api/export.csv` - download ranking report
