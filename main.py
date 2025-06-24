from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os

app = FastAPI()

# Allow all CORS (adjust for production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        # Save file to temporary path
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # TODO: Replace this with real parsing logic
        result = {
            "report_type": "CBC",
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": "14.2",
                    "unit": "g/dL",
                    "reference_range": "13.0 - 17.0"
                },
                {
                    "name": "White Blood Cells",
                    "value": "7.5",
                    "unit": "10^3/µL",
                    "reference_range": "4.5 - 11.0"
                },
                {
                    "name": "Total Cholesterol",
                    "value": "220",
                    "unit": "mg/dL",
                    "reference_range": "125 - 200"
                }
            ],
            "summary": "Mock result from PDF parser",
            "metadata": {
                "filename": file.filename,
                "pages": 2,
                "extraction_quality": "good"
            }
        }

        # Clean up temp file
        os.remove(temp_path)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")
