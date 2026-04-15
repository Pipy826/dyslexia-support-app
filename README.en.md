# Dyslexia Screening & Intervention System

An AI-powered application for early dyslexia screening and intervention, designed for parents and children. It uses gamified assessments to identify risk levels and leverages large language models to deliver personalized report interpretations, training plans, growth trend analysis, and more.

---

## Features

### Core
- **Gamified Screening**: Three game types — visual discrimination, spelling recognition, reading comprehension — each with three difficulty levels (L1/L2/L3)
- **Intelligent Assessment**: Automatically scores 7 ability dimensions and outputs Low / Medium / High risk levels
- **Detailed Reports**: Generates reports with dimension breakdowns, summaries, and intervention suggestions
- **Training System**: Personalized training tasks with a star-reward motivation system
- **Dual Interface**: UniApp cross-platform frontend supporting H5 and WeChat Mini Program

### AI Features (powered by NVIDIA NIM / OpenAI-compatible APIs)

| Feature | Description |
|---------|-------------|
| 💬 Streaming AI Chat | Real-time parent–AI conversation with child report data injected as context; supports SSE streaming |
| 📋 Personalized Report Interpretation | AI generates a tailored interpretation after each screening, replacing static template text |
| 🗓️ AI Training Plan Generator | One-tap generation of a 4-week home training plan based on weak dimensions; directly applicable to the task list |
| 📈 Growth Trend Analysis | AI compares multiple screening sessions and generates a longitudinal progress/regression report |
| 💡 Daily Learning Tips | Homepage displays a daily AI-generated tip personalized to the child's current status |
| ❤️ Parental Emotional Support | High-risk results automatically trigger an AI comfort and guidance modal to ease parental anxiety |
| 🎮 Adaptive Difficulty | AI evaluates answer performance every 5 questions and adjusts game difficulty in real time |
| 🌟 Child Encouragement | AI generates personalized encouragement after each game session, replacing generic "Great job!" messages |

All AI features include graceful fallback to template content when the API is unavailable.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy, SQLite, JWT |
| Frontend | Vue 3, UniApp, Vite, SCSS |
| AI | NVIDIA NIM (`meta/llama-3.3-70b-instruct`), OpenAI-compatible; swappable with DeepSeek, Qwen, etc. |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── ai_qa.py        # All AI endpoints (chat, report, plan, analysis, etc.)
│   │   │   ├── auth.py         # Register, login, verification code
│   │   │   ├── children.py     # Child profile management
│   │   │   ├── screenings.py   # Screening flow
│   │   │   ├── reports.py      # Report queries
│   │   │   └── training.py     # Tasks, growth records, rewards
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── ai_service.py   # LLM call wrappers (normal / streaming / feature functions)
│   │   │   └── screening_service.py  # Scoring algorithm and report generation
│   │   ├── games/              # Question banks (visual, spelling, comprehension × 3 levels)
│   │   ├── utils/              # JWT, password hashing
│   │   ├── config.py           # Configuration (reads .env)
│   │   └── main.py             # FastAPI application entry
│   ├── .env                    # Environment variables (includes AI API key)
│   ├── requirements.txt
│   └── run.py
└── frontend/
    └── src/
        ├── pages/
        │   ├── parent/
        │   │   ├── home/       # Home (daily tip, report summary)
        │   │   ├── screening/  # Screening launch and history
        │   │   ├── report/     # Report list and detail (AI interpretation, emotional support modal)
        │   │   ├── training/   # Training plan (AI generation entry)
        │   │   ├── growth/     # Growth trend analysis (new page)
        │   │   ├── ai-chat/    # Streaming AI chat
        │   │   └── profile/    # User profile
        │   └── child/
        │       ├── home/       # Child home (game type selection)
        │       ├── game/       # Game engine (adaptive difficulty)
        │       ├── reward/     # Reward page (AI encouragement)
        │       └── training/   # Child training park
        ├── api/                # API wrappers (including streaming chatStream)
        └── styles/             # Global styles
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server (.env already includes NVIDIA NIM config — works out of the box)
python run.py
```

Once running:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Frontend

```bash
cd frontend
npm install

# H5 development mode (recommended)
npm run dev:h5

# WeChat Mini Program development mode
npm run dev
```

Frontend available at: http://localhost:8080

### 3. Create an Account

The database is empty on first run. Register via the frontend, or use the API directly:

```bash
# PowerShell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/register" `
  -ContentType "application/json" `
  -Body '{"username":"test","password":"test123"}'
```

| Username | Password |
|----------|----------|
| `test` | `test123` |

---

## Environment Variables

`backend/.env` ships with NVIDIA NIM configuration — no changes needed to use AI features. To switch providers:

```env
# NVIDIA NIM (default)
AI_API_KEY=nvapi-xxxx
AI_API_BASE_URL=https://integrate.api.nvidia.com/v1
AI_MODEL=meta/llama-3.3-70b-instruct

# DeepSeek
# AI_API_KEY=sk-xxxx
# AI_API_BASE_URL=https://api.deepseek.com/v1
# AI_MODEL=deepseek-chat

# OpenAI
# AI_API_KEY=sk-xxxx
# AI_API_BASE_URL=https://api.openai.com/v1
# AI_MODEL=gpt-4o-mini

# Qwen (Alibaba Cloud)
# AI_API_KEY=sk-xxxx
# AI_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# AI_MODEL=qwen-turbo
```

---

## API Reference

### Business Endpoints

| Module | Prefix | Description |
|--------|--------|-------------|
| Auth | `/api/auth` | Register, login, verification code, current user |
| Children | `/api/children` | CRUD for child profiles |
| Screenings | `/api/screenings` | Fetch questions, start/submit screening, history |
| Reports | `/api/reports` | Report list, detail, dimension scores |
| Training | `/api/training` | Tasks, growth records, rewards, star count |

### AI Endpoints (`/api/ai`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Standard chat |
| `/chat/stream` | POST | Streaming chat (SSE) |
| `/history` | GET | Chat history |
| `/report-interpretation` | POST | AI report interpretation |
| `/training-plan` | POST | AI training plan generation |
| `/encouragement` | POST | Child encouragement message |
| `/growth-analysis/{child_id}` | GET | Growth trend analysis |
| `/daily-tip/{child_id}` | GET | Daily learning tip |
| `/emotional-support` | POST | Parental emotional support |
| `/adaptive-difficulty` | POST | Adaptive difficulty evaluation |

---

## Game Types & Ability Dimensions

| Game | Dimensions Assessed |
|------|---------------------|
| `visual` Visual Discrimination | Visual discrimination, Attention |
| `spelling` Spelling Recognition | Spelling, Phonological mapping, Character order |
| `comprehension` Reading Comprehension | Reading comprehension, Semantic integration, Information extraction |

Difficulty levels: `L1` (Basic) / `L2` (Intermediate) / `L3` (Advanced)  
Risk levels: `low` / `medium` / `high`

---

## License

MIT
