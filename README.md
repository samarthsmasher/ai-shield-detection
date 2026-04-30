# 🛡️ AI Shield — Multi-Modal AI Content & Spam Detection System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js)](https://nextjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb)](https://cloud.mongodb.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-F7931E?logo=scikit-learn)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> Real-time detection of **spam text**, **fake images**, and **deepfake videos** using machine learning — powered by FastAPI, Next.js, and MongoDB Atlas.

---

## 🔴 Live Demo

| Service  | URL |
|----------|-----|
| **Frontend** | https://ai-shield.vercel.app *(update after deployment)* |
| **Backend API** | https://ai-shield-backend.onrender.com *(update after deployment)* |
| **API Docs** | https://ai-shield-backend.onrender.com/docs |

---

## ✨ Features

- 💬 **Text Spam Detection** — TF-IDF + Multinomial Naïve Bayes (98.5% accuracy on 5,572 SMS samples)
- 🖼️ **Image Authenticity Check** — Detects AI-generated / manipulated images using colour histogram + edge-density heuristics (ResNet-50 ready)
- 🎬 **Video Deepfake Detection** — Frame-by-frame analysis with majority-vote aggregation via OpenCV
- 🔐 **JWT Authentication** — Register / login with bcrypt-hashed passwords and signed tokens
- 📊 **MongoDB Audit Trail** — Every request logged with endpoint, status code, and processing time
- 🌙 **Premium Dark UI** — Glassmorphism, neon gradients, framer-motion animations

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15 (App Router), TypeScript, Tailwind CSS, framer-motion |
| **Backend** | FastAPI 0.115, Python 3.11, Uvicorn |
| **ML — Text** | scikit-learn (TfidfVectorizer + MultinomialNB), joblib |
| **ML — Image** | Pillow, NumPy (ResNet-50 via torchvision fallback) |
| **ML — Video** | OpenCV (cv2), PIL fallback |
| **Database** | MongoDB Atlas (async via Motor) |
| **Auth** | python-jose (JWT), bcrypt |
| **Deployment** | Render (backend) · Vercel (frontend) |

---

## 📁 Project Structure

```
ai-detection-system/
├── backend/                 # FastAPI application
│   ├── main.py              # App factory, middleware, router registration
│   ├── database.py          # Motor async client + ping_db()
│   ├── dependencies.py      # JWT get_current_user dependency
│   ├── Procfile             # Render start command
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Secrets (not committed)
│   ├── routers/
│   │   ├── auth.py          # POST /api/auth/register  /login
│   │   └── detect.py        # POST /api/detect/text  /image  /video
│   └── models/
│       ├── user_model.py    # UserCreate, UserInDB, UserResponse
│       ├── result_model.py  # DetectionResult, DetectionResponse
│       └── log_model.py     # SystemLog
├── frontend/                # Next.js application
│   ├── app/
│   │   ├── layout.tsx       # Root layout (Navbar, Google Fonts, SEO)
│   │   ├── page.tsx         # Landing page (Hero + DetectionModeCards)
│   │   └── detect/
│   │       ├── text/page.tsx
│   │       ├── image/page.tsx
│   │       └── video/page.tsx
│   └── components/
│       ├── Navbar.tsx
│       ├── UploadBox.tsx
│       ├── ResultCard.tsx
│       ├── Loader.tsx
│       └── DetectionModeCard.tsx
├── models/                  # ML artefacts
│   ├── data/spam.csv        # SMS Spam Collection (5,572 samples)
│   ├── train_text_model.py  # Training script
│   ├── text_spam_model.joblib
│   ├── image_inference.py   # predict_image(bytes) → dict
│   └── video_utils.py       # extract_frames() + predict_video()
├── render.yaml              # Render IaC config
└── .gitignore
```

---

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-detection-system.git
cd ai-detection-system
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=cluster
MONGO_DB_NAME=ai_detection_db
JWT_SECRET=your_super_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

Train the text model:
```bash
cd ../models
python train_text_model.py
```

Start the backend:
```bash
cd ../backend
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend at: http://localhost:3000

---

## 🔌 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET`  | `/api/health` | None | Server health check |
| `POST` | `/api/auth/register` | None | Register new user |
| `POST` | `/api/auth/login` | None | Login, receive JWT |
| `POST` | `/api/detect/text` | Optional | Detect spam in text |
| `POST` | `/api/detect/image` | Optional | Check image authenticity |
| `POST` | `/api/detect/video` | Optional | Detect deepfake video |

### Text detection example

```bash
curl -X POST http://localhost:8000/api/detect/text \
  -H "Content-Type: application/json" \
  -d '{"text": "WINNER!! Claim your free prize now!"}'
```

Response:
```json
{
  "result": "spam",
  "confidence": 0.9977,
  "input_type": "text",
  "timestamp": "2026-04-30T15:30:00Z"
}
```

---

## 📊 Model Performance

| Model | Dataset | Accuracy | Precision | Recall |
|-------|---------|----------|-----------|--------|
| TF-IDF + MultinomialNB | SMS Spam Collection (5,572 samples) | **98.48%** | 99.25% | 89.26% |

---

## 🌐 Deployment

### Backend → Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect GitHub repo
3. Set root directory to `backend`
4. Set environment variables: `MONGO_URI`, `JWT_SECRET`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import GitHub repo
2. Set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
4. Deploy

---

## 📄 License

MIT © 2026 AI Shield

---

*Built as part of ASEP 2 — Advanced Software Engineering Project*
