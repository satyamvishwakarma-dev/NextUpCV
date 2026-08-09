import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import directly from your src modules
from src.vectorcv import *

app = FastAPI(
    title="VectorCV API",
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
    if not file.filename.lower().endswith(".pdf"):
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
        match_score = match_engine.compute_similarity(raw_text, job_description)
        missing_keywords = match_engine.extract_missing_keywords(
            raw_text, job_description
        )
        suggested_bullets = bullet_generator.generate_tailored_bullets(missing_keywords)

        # 3. Save Record in SQLite
        scan_id = save_scan_record(
            file_name=file.filename,
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


# Serve HTML/CSS/JS frontend files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
