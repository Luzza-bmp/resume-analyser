# SipSetu

**No skill left behind.** AI-powered recruitment platform bridging job seekers and recruiters. Uses skill-based matching, resume analysis, and candidate ranking to connect talent with opportunity.

## Features

- **Role-based portals** — Dedicated dashboards for applicants and recruiters
- **Resume upload** — Upload your resume for AI-powered skill extraction
- **Intelligent job matching** — Jobs ranked by actual skill overlap with match scores
- **Skill gap analysis** — Identify missing skills for your target roles with learning resources
- **Candidate ranking** — Recruiters see applicants auto-scored against job requirements
- **Profile management** — Manage personal info, company details, and preferences

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask, SQLAlchemy, PostgreSQL |
| Frontend | React 18, TypeScript, Vite 6, Tailwind CSS v4 |
| UI | shadcn/ui, Radix UI, Lucide Icons, Framer Motion |
| Tooling | Axios, React Router v7, Recharts, Lottie |

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- npm or pnpm

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd SipSetu
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

> **Important:** Edit `.env` and replace the placeholder values with your own PostgreSQL credentials (password, host, port). The example file uses `YOUR_PASSWORD_HERE` — do not commit real credentials.

```bash
# Create the database in PostgreSQL
# psql -U postgres -c "CREATE DATABASE sipsetu;"

# Initialize database tables
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"

# Apply additional schema migrations
python update_db.py

# Start the backend server
python app.py
```

The backend starts at **http://127.0.0.1:5000**. Verify with a health check:

```bash
curl http://127.0.0.1:5000/api/health
# {"status": "healthy"}
```

### 3. Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend starts at **http://localhost:5173**.

### 4. Open the app

Navigate to **http://localhost:5173** in your browser. Register as a Job Seeker or Recruiter to explore the platform.

## Project Structure

```
SipSetu/
├── app/                      # Flask application package
│   ├── routes/               # API endpoints for auth, jobs, resumes, dashboards
│   ├── services/             # Resume parsing, matching, and extraction logic
│   ├── utils/                # Scoring and helper utilities
│   └── models/               # Trained NLP model assets
├── frontend/                 # React + TypeScript client app
│   ├── src/                  # UI pages, components, routes, and styles
│   └── package.json          # Frontend dependencies and scripts
├── migrations/               # SQL migration files
├── docs/                     # Product docs, guides, and reference notes
├── scripts/                  # Helper scripts and one-off utilities
├── examples/                 # Sample resumes and example assets
├── tests/                    # Automated tests
├── uploads/                  # Runtime uploads (ignored in Git except placeholders)
├── requirements.txt          # Backend Python dependencies
├── tsconfig.json             # Shared TypeScript config
└── README.md                 # Project overview
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Log in and retrieve user info |
| GET | `/api/jobs` | List all job postings |
| POST | `/api/jobs` | Create a new job posting |
| POST | `/api/resumes` | Upload resume text for an applicant |
| GET | `/api/profile/<user_id>` | Get user profile details |
| PUT | `/api/profile/<user_id>` | Update user profile |

## Known Limitations

This is an early-stage build (approx. 30-35% toward production readiness). Key limitations:

- **AI matching is placeholder** — The core TF-IDF / cosine similarity matching engine is marked as TODO. Match scores, skill gap analysis, and candidate rankings currently use hardcoded demo data.
- **No JWT authentication** — Auth state is stored in `localStorage` (user_id, user_role) with no server-side token validation. This is not secure for production.
- **Hardcoded demo data** — Many pages (candidates, stats, skill gaps) use static mock arrays instead of live API data.
- **Resume file upload** — Resumes accept raw text only; multipart file upload is not implemented.
- **No pagination** — List endpoints return all records without pagination.
- **No test suite** — Only one manual test script exists (`test_login.py`).

## License

© 2026 SipSetu Inc.
