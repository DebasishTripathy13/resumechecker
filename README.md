# Resume Checker

A modular Flask app that analyzes PDF resumes and scores them on ATS readability, sections, content quality, contact info, and keyword match against an optional job description.

## Quick start

```bash
cd resume-checker
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements-dev.txt
python run.py                   # http://127.0.0.1:5000
pytest                          # run the test suite
```

For production, set `SECRET_KEY` and `FLASK_CONFIG=production`, then serve with a WSGI server, e.g. `waitress-serve --call app:create_app` or `gunicorn "app:create_app('production')"`.

## Project layout

```
resume-checker/
├── run.py                       # entry point
├── config.py                    # Dev / Test / Prod config (upload limits, page cap)
├── app/
│   ├── __init__.py              # create_app() factory
│   ├── routes/
│   │   ├── main.py              # HTML: upload form + results page
│   │   ├── api.py               # JSON: POST /api/analyze, GET /api/health
│   │   └── errors.py            # 404/413/500 → HTML or JSON
│   ├── services/
│   │   ├── analyzer.py          # orchestrates parse → checks → score
│   │   ├── pdf_parser.py        # in-memory PDF text extraction (pypdf)
│   │   ├── contact_extractor.py # email, phone, LinkedIn, GitHub, website
│   │   ├── section_detector.py  # Experience / Education / Skills / ...
│   │   ├── content_analyzer.py  # action verbs, metrics, weak phrases, pronouns
│   │   ├── formatting_checker.py# ATS readability, length, density
│   │   ├── keyword_matcher.py   # skill detection + job-description match
│   │   └── scorer.py            # weighted overall score + grade
│   ├── models/report.py         # Finding / CheckResult / AnalysisReport
│   ├── data/keywords.py         # action verbs, skills, stopwords
│   ├── utils/
│   │   ├── validators.py        # extension + %PDF- magic-byte check
│   │   ├── security.py          # CSRF token + security headers (CSP)
│   │   └── text_utils.py        # normalize, tokenize, phrase matching
│   ├── templates/               # base, index, result, error
│   └── static/                  # css/style.css, js/main.js
└── tests/                       # pytest suite (generates PDFs with reportlab)
```

## Scoring

| Check | Weight | What it looks at |
|---|---|---|
| Contact | 15% | email, phone, LinkedIn, portfolio/GitHub |
| Sections | 20% | required: Experience, Education, Skills; recommended: Summary, Projects, Certifications |
| Content | 25% | distinct action verbs, quantified lines, bullet count; penalties for weak phrases and "I/me/my" |
| Formatting | 15% | selectable text (scanned PDFs fail), page count, word count, dense paragraphs, symbols |
| Keywords | 25% | with a job description: % of JD keywords found; without: detected skills |

Grades: A ≥ 85, B ≥ 70, C ≥ 55, D below.

## API

```bash
curl -F "resume=@my_resume.pdf" -F "job_description=Python, AWS, Kubernetes..." \
     http://127.0.0.1:5000/api/analyze
```

Returns `overall_score`, `grade`, `checks[]` (each with `score`, `status`, `findings`, `details`) and `suggestions[]`.

## Security notes

- Uploads are parsed in memory and never written to disk.
- 5 MB request cap, 10-page cap, extension and `%PDF-` signature checks; encrypted PDFs are rejected.
- The HTML form is CSRF-protected; all pages send a strict CSP (no inline scripts or styles).
- Extracted resume text is auto-escaped by Jinja before display.
