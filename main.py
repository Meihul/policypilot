import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from azure_services import (
    extract_text,
    analyze_text,
    translate_text
)

# ==========================================
# Paths
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ==========================================
# FastAPI App
# ==========================================

app = FastAPI(title="PolicyPilot AI")

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Serve frontend (index.html, style.css, script.js)
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# ==========================================
# Language Mapping
# ==========================================

language_codes = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh-Hans"
}

# ==========================================
# Home Route -> serves the frontend
# ==========================================

@app.get("/")
def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# ==========================================
# Upload Route
# ==========================================

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    language: str = "Hindi"
):

    try:

        # Save the PDF to a system temp file (outside the project folder)
        contents = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(contents)
            file_path = tmp.name

        try:
            # Azure Document Intelligence
            extracted_text = extract_text(file_path)

            # Azure AI Language
            analysis = analyze_text(extracted_text)

            # Convert language name to Azure language code
            target_language = language_codes.get(language, language)

            # Azure Translator
            translated_text = translate_text(
                extracted_text,
                target_language
            )
        finally:
            # Always clean up the temp file
            os.remove(file_path)

        return {

            "success": True,

            "file_name": os.path.basename(file.filename),

            "language_detected": analysis["language"],

            "key_phrases": analysis["key_phrases"],

            "entities": analysis["entities"],

            "original_text": extracted_text,

            "translated_text": translated_text

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )