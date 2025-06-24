from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import re
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("/tmp/temp.pdf", "wb") as f:
            f.write(contents)

        # Extract text using PyMuPDF
        doc = fitz.open("/tmp/temp.pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Basic test result pattern (e.g. Hemoglobin 14.2 g/dL)
        pattern = re.compile(r"([A-Za-z\s]+?)\s*[:\-]?\s*([\d.]+)\s*([a-zA-Z/%μ^0-9]+)?")

        matches = pattern.findall(full_text)
        tests = []
        for match in matches:
            name, value, unit = match
            try:
                float(value)  # Ensure value is numeric
                tests.append({
                    "name": name.strip(),
                    "value": value,
                    "unit": unit.strip() if unit else None,
                    "reference_range": None  # You can add logic to detect this too
                })
            except:
                continue

        return {
            "report_type": "Unknown",
            "tests": tests,
            "summary": "",
            "metadata": {
                "filename": file.filename,
                "pages": len(doc),
                "extraction_quality": "good" if len(tests) > 2 else "poor"
            }
        }

    except Exception as e:
        return {
            "error": str(e)
        }
