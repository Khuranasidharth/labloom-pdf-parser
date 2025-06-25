from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import tempfile

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
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        extracted_tests = []

        # Parse table rows from the PDF
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 2:
                            continue

                        # Clean up each cell
                        row = [cell.strip() if cell else "" for cell in row]

                        # Basic logic for 4-column rows: test name, value, unit, reference
                        if len(row) >= 4:
                            name, value, unit, ref = row[:4]
                        elif len(row) == 3:
                            name, value, unit = row
                            ref = None
                        elif len(row) == 2:
                            name, value = row
                            unit = ref = None
                        else:
                            continue

                        try:
                            float(value)  # Ensure it's a numeric value
                            extracted_tests.append({
                                "name": name,
                                "value": value,
                                "unit": unit or None,
                                "reference_range": ref or None
                            })
                        except ValueError:
                            continue

        return {
            "report_type": "Parsed via tables",
            "tests": extracted_tests,
            "summary": "",
            "metadata": {
                "filename": file.filename,
                "pages": len(pdf.pages),
                "extraction_quality": "good" if len(extracted_tests) > 2 else "poor"
            }
        }

    except Exception as e:
        return { "error": str(e) }
