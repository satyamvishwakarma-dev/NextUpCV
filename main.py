import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

# 1. Resolve Paths & Inject into sys.path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 2. Application Imports
from nextupcv.database.connection import init_db
from nextupcv.database.repository import save_scan_record, get_recent_scans
from nextupcv.services.pdf_parser import ResumeParserService
from nextupcv.services.match_engine import MatchEngine
from nextupcv.services.generator import RuleBasedBulletGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from nextupcv.database.connection import init_db


# 3. Lifespan for Safe Database Initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        print("Database successfully initialized in /tmp/nextupcv.db")
    except Exception as e:
        print(f"Warning: Database initialization error: {e}")
    yield


app = FastAPI(
    title="NextUpCV API",
    lifespan=lifespan,
)

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Service Instances
resume_parser = ResumeParserService()
match_engine = MatchEngine()
bullet_generator = RuleBasedBulletGenerator()

# 6. Frontend Directory Setup
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")


# 7. Static Page Routes
@app.get("/about")
async def read_about():
    about_file = FRONTEND_DIR / "about.html"
    if about_file.exists():
        return FileResponse(about_file)
    raise HTTPException(status_code=404, detail="about.html not found")


@app.get("/pricing")
async def read_pricing():
    pricing_file = FRONTEND_DIR / "pricing.html"
    if pricing_file.exists():
        return FileResponse(pricing_file)
    raise HTTPException(status_code=404, detail="pricing.html not found")


@app.get("/contact")
async def read_contact():
    return RedirectResponse(url="https://msystech.onrender.com/pages/contact.html")


# 8. API Endpoints
@app.post("/api/v1/analyze")
async def analyze_resume(
    file: UploadFile = File(...), job_description: str = Form(...)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    try:
        file_bytes = await file.read()

        # Parse PDF
        parsed_resume = resume_parser.parse_resume(file_bytes)
        if "error" in parsed_resume:
            raise HTTPException(status_code=422, detail=parsed_resume["error"])

        raw_text = parsed_resume["raw_text"]

        # Match Engine & Bullet Generation
        match_score = match_engine.compute_similarity(raw_text, job_description)
        missing_keywords = match_engine.extract_missing_keywords(
            raw_text, job_description
        )
        suggested_bullets = bullet_generator.generate_tailored_bullets(missing_keywords)

        # Save Record in SQLite
        scan_id = None
        try:
            scan_id = save_scan_record(
                file_name=file.filename,
                raw_resume_text=raw_text,
                job_description=job_description,
                match_score=match_score,
                missing_keyword_count=len(missing_keywords),
            )
        except Exception as db_err:
            print(f"Warning: Failed to save scan history: {db_err}")

        return {
            "status": "success",
            "scan_id": scan_id,
            "filename": file.filename,
            "match_score": match_score,
            "contact_info": parsed_resume.get("contact_info", {}),
            "missing_keywords": missing_keywords,
            "suggested_bullets": suggested_bullets,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/history")
async def fetch_history():
    """Returns past scans logged in SQLite."""
    try:
        scans = get_recent_scans(limit=5)
        return {"status": "success", "history": scans}
    except Exception:
        return {"status": "success", "history": []}
