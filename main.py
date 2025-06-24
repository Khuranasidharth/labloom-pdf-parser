from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import re
from typing import List, Optional

app = FastAPI()

# Allow CORS (so Supabase Edge Function can call it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    doc = fitz.open(stream=contents, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    tests = []
    for match in re.finditer(r"([A-Za-z ()]+?)\s+(\d+\.?\d*)\s+([a-zA-Z%/^\dµ]+)\s+(\d+\.?\d*\s*-\s*\d+\.?\d*)", text):
        tests.append({
            "name": match.group(1).strip(),
            "value": match.group(2),
            "unit": match.group(3),
            "reference_range": match.group(4)
        })

    return {
        "report_type": "General",
        "tests": tests,
        "summary": text[:200] + "...",
        "metadata": {
            "filename": file.filename,
            "pages": len(doc),
            "extraction_quality": "good"
        }
    }