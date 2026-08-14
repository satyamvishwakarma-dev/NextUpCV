# NextUpCV 🎯
> Lightweight, Deterministic ATS Matching Engine & Action-Oriented Bullet Generator.

NextUpCV is a production-ready Applicant Tracking System (ATS) matching tool built to parse, analyze, and optimize resumes against job descriptions. Designed specifically for serverless edge deployments, it operates on a zero-heavy-ML architecture, reducing cold starts to sub-second speeds and keeping deployment bundles under **30 MB**.

---

## ✨ Features

- ⚡ **Ultra-Lightweight Serverless Architecture:** Optimized for Vercel/AWS Lambda with a minimal footprint (< 30 MB) and zero heavy C-extension dependencies.
- 📄 **Pure-Python PDF Parsing:** Fast, in-memory stream extraction using `pypdf` with no disk-writing bottlenecks.
- 🎯 **Deterministic Match Engine:** Cosine similarity and keyword frequency scoring using vector-space math in the Python standard library.
- 💡 **Action-Oriented Suggestion Engine:** Extracts critical missing technical keywords and dynamically produces tailored impact bullets.
- 🗄️ **Ephemeral / Cloud-Ready Persistence:** Integrated SQLite logging configured for ephemeral `/tmp/` environments and easy migration to PostgreSQL/Supabase.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.12, Uvicorn, Pydantic
- **Parsing & Math:** `pypdf`, Standard Library (`math`, `re`, `collections`)
- **Database:** SQLite (Ephemeral `/tmp/` configuration via SQLAlchemy)
- **Deployment:** Vercel Serverless Functions

---

## 🚀 Quickstart (Local Development)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/satyamvishwakarma-dev/NextUpCV
cd nextupcv
```
```
# Using uv (recommended)
uv sync
```
```
# Or using standard pip
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
### 2. Run the Application
```bash
uvicorn main:app --reload --port 8000
```
- Open http://localhost:8000 in your browser.

---

## 🌐 Quickstart (Website)

visit [https://nextupcv.vercel.app/](https://nextupcv.vercel.app/)


---

## 📡 API Reference

- POST /api/v1/analyze
- Analyzes a resume against a target job description.

- Form Data:

    file: Resume PDF (multipart/form-data)

    job_description: Target job requirements (string)

- Response:

```json
{ 
  "status": "success",
  "scan_id": 1,
  "filename": "resume.pdf",
  "match_score": 84,
  "contact_info": {
    "email": "user@example.com",
    "phone": "+919876543210",
    "linkedin": "[linkedin.com/in/user](https://linkedin.com/in/user)",
    "github": "[github.com/user](https://github.com/user)"
  },
  "missing_keywords": ["Kubernetes", "Docker", "CI/CD"],
  "suggested_bullets": [
    "Orchestrated containerized microservices using Docker and Kubernetes to improve deployment frequency."
  ]
}
```