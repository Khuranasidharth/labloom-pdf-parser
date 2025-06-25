from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import tempfile
import re

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
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        extracted_tests = []

        # Extract data using pdfplumber
        with pdfplumber.open(tmp_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

            # Pattern like "Hemoglobin 14.2 g/dL" or "TSH : 2.5 mIU/L"
            pattern = re.compile(r"([A-Za-z\s]+?)\s*[:\-]?\s*([\d.]+)\s*([a-zA-Z/%μ^0-9]+)?")
            matches = pattern.findall(text)

            for match in matches:
                name, value, unit = match
                try:
                    float(value)
                    extracted_tests.append({
                        "name": name.strip(),
                        "value": value,
                        "unit": unit.strip() if unit else None,
                        "reference_range": None
                    })
                except:
                    continue

        return {
            "report_type": "General",
            "tests": extracted_tests,
            "summary": "",
            "metadata": {
                "filename": file.filename,
                "pages": len(pdf.pages),
                "extraction_quality": "good" if len(extracted_tests) > 1 else "poor"
            }
        }

    except Exception as e:
        return { "error": str(e) }