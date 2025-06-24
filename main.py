from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Labloom PDF parser running!"}

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # MOCK response (replace with real parser logic)
        result = {
            "report_type": "CBC",
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": "14.2",
                    "unit": "g/dL",
                    "reference_range": "13.0 - 17.0"
                }
            ],
            "summary": "Mock parsed PDF",
            "metadata": {
                "filename": file.filename,
                "pages": 2,
                "extraction_quality": "good"
            }
        }

        os.remove(temp_path)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")
