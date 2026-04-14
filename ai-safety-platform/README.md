# AI Safety & Smart FIR Platform

AI Safety & Smart FIR Platform is a production-ready full-stack solution that:

- Detects harmful content from text and image evidence.
- Extracts text from image uploads via OCR.
- Scores toxicity with a HuggingFace transformer model.
- Generates structured FIR PDFs for cyber abuse incidents.
- Stores evidence in Cloudinary and metadata in MongoDB.

## Tech Stack

### Frontend
- Next.js
- Tailwind CSS
- Axios

### Backend
- FastAPI
- Uvicorn
- Motor (MongoDB async driver)

### AI/ML
- HuggingFace Transformers (`unitary/toxic-bert`)
- pytesseract OCR

### Report Generation
- reportlab

### Cloud Storage
- Cloudinary Python SDK

## Project Structure

```text
ai-safety-platform/
|- backend/
|  |- config/
|  |- models/
|  |- routes/
|  |- services/
|  |- utils/
|  |- Dockerfile
|  |- main.py
|- frontend/
|  |- components/
|  |- pages/
|  |- services/
|  |- styles/
|  |- package.json
|- ai-services/
|  |- toxicity.py
|  |- ocr.py
|- .env.example
|- requirements.txt
|- README.md
```

## Features Implemented

1. Text Analysis API (`POST /analyze-text`)
- Input text.
- Returns toxicity score and risk label (LOW/MEDIUM/HIGH).

2. Image Analysis API (`POST /analyze-image`)
- Accepts image via `UploadFile`.
- Uploads image to Cloudinary.
- Performs OCR from Cloudinary URL.
- Runs toxicity analysis on extracted text.

3. Risk Scoring Engine
- `score > 0.8`: HIGH
- `score > 0.5`: MEDIUM
- Else: LOW

4. FIR Generation (`POST /generate-fir`)
- Accepts complainant details and evidence.
- Uploads evidence file to Cloudinary when provided.
- Generates FIR PDF using reportlab.
- Stores FIR binary in MongoDB for download.

5. FIR Download (`GET /download-fir?fir_id=...`)
- Streams PDF as downloadable file.

6. Evidence Storage
- No local files are persisted.
- MongoDB stores only Cloudinary URL + `public_id` and metadata.

## API Endpoints

- `POST /analyze-text`
- `POST /analyze-image`
- `POST /generate-fir`
- `GET /download-fir`
- `GET /health`

## Setup Instructions

## 1) Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB running locally or remotely
- Cloudinary account credentials
- Tesseract OCR installed on host machine
- On Windows, prefer a short virtual environment path (example: `C:\v\asp`) to avoid path-length issues when installing Transformers.

### Install Tesseract
- Windows: Install from official UB Mannheim build and optionally set `TESSERACT_CMD`.
- Ubuntu: `sudo apt install tesseract-ocr`
- macOS: `brew install tesseract`

## 2) Configure Environment

From project root:

1. Copy `.env.example` to `.env`.
2. Fill in MongoDB and Cloudinary credentials.

For frontend:

1. Copy `frontend/.env.local.example` to `frontend/.env.local`.
2. Set backend URL (default `http://localhost:8000`).

## 3) Run Backend

```bash
cd ai-safety-platform
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Windows Long Path Workaround

Recommended on Windows (avoids long path issues with Transformers and Store Python paths):

```powershell
cd ai-safety-platform
python -m venv C:\v\asp
C:\v\asp\Scripts\python.exe -m pip install --upgrade pip
C:\v\asp\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
C:\v\asp\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Optional (requires Administrator PowerShell):

```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -Type DWord -Value 1
```

Reboot after enabling LongPaths.

## 4) Run Frontend

```bash
cd ai-safety-platform/frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Docker (Backend)

Build from project root:

```bash
docker build -f backend/Dockerfile -t ai-safety-backend .
```

Run:

```bash
docker run --env-file .env -p 8000:8000 ai-safety-backend
```

## Cloudinary Migration Notes

This implementation is fully migrated to Cloudinary:

- Upload pipeline is centralized in `backend/services/cloudinary_service.py`.
- Cloudinary is initialized from env vars in `backend/config/cloudinary_config.py`.
- Routes no longer write files locally.
- MongoDB records store Cloudinary metadata (`cloudinary_url`, `cloudinary_public_id`) only.
- OCR reads image bytes using Cloudinary secure URL.
- FIR generation includes cloud evidence URL in the PDF.

## Production Hardening Suggestions

- Add JWT authentication for protected operations.
- Add API rate limiting and request throttling.
- Add audit logs and tamper-evident storage.
- Add background queue (Celery/RQ) for heavy OCR/model workloads.
- Add object lifecycle policy and signed URLs in Cloudinary.
- Add unit/integration tests and CI pipeline.
