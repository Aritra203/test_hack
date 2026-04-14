# AI Safety & Smart FIR Platform (Elite)

Production-grade platform for harmful content detection, child-safety risk intelligence, legal mapping, and FIR PDF generation.

## Full Folder Structure

```text
ai-safety-platform/
├── backend/
│   ├── __init__.py
│   ├── Dockerfile
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── cloudinary_config.py
│   │   ├── database.py
│   │   └── settings.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analysis.py
│   │   ├── analytics.py
│   │   └── fir.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cloudinary_service.py
│   │   ├── fir_service.py
│   │   ├── ocr_service.py
│   │   └── toxicity_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── legal_mapping.py
│   │   ├── module_loader.py
│   │   └── risk.py
│   └── workers/
│       ├── celery_app.py
│       └── tasks.py
├── frontend/
│   ├── .env.local.example
│   ├── .eslintrc.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── app/
│   │   ├── layout.js
│   │   └── page.js
│   ├── animations/
│   │   └── motion.js
│   ├── components/
│   │   ├── HomePageClient.jsx
│   │   ├── LoadingSkeleton.jsx
│   │   └── RiskBadge.jsx
│   ├── services/
│   │   ├── api.js
│   │   └── store.js
│   └── styles/
│       └── globals.css
├── ai-services/
│   ├── context_analysis.py
│   ├── grooming_detection.py
│   ├── multilingual_processing.py
│   ├── ocr.py
│   └── toxicity.py
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Implemented Capabilities

1. **Multimodal abuse detection**
   - `POST /analyze-text`: text + previous conversation context
   - `POST /analyze-image`: image upload to Cloudinary + OCR + analysis

2. **Hybrid AI engine**
   - HuggingFace transformer + rule-based category scoring
   - Multi-label output: `cyberbullying`, `threat`, `hate_speech`, `sexual_harassment`

3. **Context-aware analysis**
   - Escalation detection over prior messages
   - Context summary and risk score boost

4. **Explainable AI**
   - Toxic spans with reasons
   - Transparent legal mapping explanation

5. **Multilingual normalization**
   - Hinglish/Hindi/Bengali-mix normalization pipeline

6. **Grooming detection**
   - Pattern detection for child-targeting behavior
   - Risk uplift for minor-targeted incidents

7. **Risk engine**
   - Risk output: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`

8. **Legal intelligence**
   - Maps abuse patterns to Indian laws (IPC, IT Act, POCSO)

9. **FIR system**
   - `POST /generate-fir` (queued via Celery or sync fallback)
   - `GET /download-fir?fir_id=...`
   - Court-style FIR PDF via reportlab

10. **Async architecture**
    - Redis + Celery worker for FIR job processing
    - `GET /fir-job/{job_id}` job status endpoint

11. **Analytics**
    - `GET /analytics` with risk/category aggregates + recent incidents

12. **Premium UI/UX**
    - Next.js App Router + Tailwind + Framer Motion
    - Landing sections: Hero, Features, How It Works, Demo Preview, Testimonials, CTA, Footer
    - Dashboard: text/image analysis, context input, risk badge, legal mapping, explainability, FIR actions
    - Glassmorphism/gradients, hover interactions, skeleton loading, toasts, dark-mode toggle, responsive layout

## API Endpoints

- `POST /analyze-text`
- `POST /analyze-image`
- `POST /generate-fir`
- `GET /fir-job/{job_id}`
- `GET /download-fir`
- `GET /analytics`
- `GET /health`

## Environment Setup

Copy `.env.example` to `.env`:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=ai_safety_platform
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_FOLDER=ai-safety-platform/evidence
ALLOWED_ORIGINS=http://localhost:3000
HF_MODEL_NAME=unitary/toxic-bert
TESSERACT_CMD=
MAX_UPLOAD_MB=10
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

Copy frontend env:

```bash
cp frontend/.env.local.example frontend/.env.local
```

## Run Locally

### Backend

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Celery Worker

```bash
celery -A backend.workers.tasks worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Run with Docker Compose

```bash
docker compose up --build
```
