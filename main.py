import sys
import os
from pathlib import Path

# 1. Resolve project root and src directory
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

# 2. Add 'src' to sys.path so 'nextupcv' can be imported directly
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Now import your application packages
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import FileResponse, RedirectResponse

# Import directly from your src modules
from nextupcv.database.connection import init_db
from nextupcv.database.repository import save_scan_record, get_recent_scans
from nextupcv.services.pdf_parser import ResumeParserService
from nextupcv.services.match_engine import MatchEngine
from nextupcv.services.generator import RuleBasedBulletGenerator

app = FastAPI(
    title="NextUpCV API",
    description="Deterministic ATS Engine REST API",
    version="2.0.0",
)

# Enable CORS for external API clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database & Core Engines
init_db()
resume_parser = ResumeParserService()
match_engine = MatchEngine()
bullet_generator = RuleBasedBulletGenerator()


@app.post("/api/v1/analyze")
async def analyze_resume(
    file: UploadFile = File(...), job_description: str = Form(...)
):
    if not file.filename.lower().endswith(".pdf"):  # type: ignore
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    try:
        file_bytes = await file.read()

        # 1. Parse PDF
        parsed_resume = resume_parser.parse_resume(file_bytes)
        if "error" in parsed_resume:
            raise HTTPException(status_code=422, detail=parsed_resume["error"])

        raw_text = parsed_resume["raw_text"]

        # 2. Match Engine & spaCy Bullet Generation
        match_score = match_engine.compute_similarity(raw_text, job_description)  # type: ignore
        missing_keywords = match_engine.extract_missing_keywords(  # type: ignore
            raw_text, job_description
        )
        suggested_bullets = bullet_generator.generate_tailored_bullets(missing_keywords)

        # 3. Save Record in SQLite
        scan_id = save_scan_record(
            file_name=file.filename,  # type: ignore
            raw_resume_text=raw_text,
            job_description=job_description,
            match_score=match_score,
            missing_keyword_count=len(missing_keywords),
        )

        return {
            "status": "success",
            "scan_id": scan_id,
            "filename": file.filename,
            "match_score": match_score,
            "contact_info": parsed_resume.get("contact_info", {}),
            "missing_keywords": missing_keywords,
            "suggested_bullets": suggested_bullets,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/history")
async def fetch_history():
    """Returns past scans logged in SQLite."""
    scans = get_recent_scans(limit=5)
    return {"status": "success", "history": scans}


@app.get("/about")
async def read_about():
    return FileResponse(os.path.join(frontend_dir, "about.html"))


@app.get("/pricing")
async def read_pricing():
    return FileResponse(os.path.join(frontend_dir, "pricing.html"))


@app.get("/contact")
async def read_contact():
    return RedirectResponse(url="https://msystech.onrender.com/pages/contact.html")


# Serve HTML/CSS/JS frontend files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


# Detect Vercel environment and use ephemeral /tmp directory
IS_VERCEL = os.environ.get("VERCEL", False)

if IS_VERCEL:
    DB_DIR = Path("/tmp")
else:
    DB_DIR = Path(__file__).resolve().parent / "data"
    DB_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_DIR / 'NextUpCV.db'}"
