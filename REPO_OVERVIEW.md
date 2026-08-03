# SipSetu Repository Overview

## Project Summary

SipSetu is an AI-assisted recruitment platform built as a Flask backend with a React + TypeScript frontend. The application supports:
- Role-based portals for applicants and recruiters
- Resume upload and parsing
- Job posting and cancellation
- Candidate matching and scoring
- Recruiter dashboards and job management

The backend is located in `app/`, while the frontend client is under `frontend/`.

---

## Top-Level Files

### `README.md`
- Project overview, setup instructions, tech stack, and API endpoint documentation.
- Contains a general description of features and limitations.

### `requirements.txt`
- Python dependencies for the backend.
- Required for Flask, SQLAlchemy, JWT, CORS, and other server-side packages.

### `tsconfig.json`
- TypeScript compiler configuration for the frontend.

### `run.py`
- Entrypoint for starting the Flask backend.
- Calls `create_app()` from `app/__init__.py` and runs the server with `debug=True`.

### `pyrefly.toml`
- Likely tool or formatting config for Python refactoring/analysis (not inspected in detail).

### `package-lock.json`
- Frontend dependency lockfile for npm.

---

## Backend Structure (`app/`)

### `app/__init__.py`
- Creates and configures the Flask application.
- Initializes `SQLAlchemy`, `JWTManager`, and CORS.
- Registers blueprints for auth, profile, resumes, jobs, applicant dashboard, recruiter dashboard, and public routes.
- Contains `ensure_applicant_table_schema()` to migrate missing columns and ensure table schemas at startup.
- Calls `db.create_all()` in app context for development.

### `app/config.py`
- Loads environment variables using `dotenv`.
- Defines `Config` with `SQLALCHEMY_DATABASE_URI`, `SQLALCHEMY_TRACK_MODIFICATIONS=False`, `JWT_SECRET_KEY`, and JWT expiration.

### `app/models.py`
- SQLAlchemy models for the core data schema.
- `User`, `Applicant`, `Recruiter`, `Resume`, `Analysis`, `Job`, and `Application`.
- Uses PostgreSQL arrays and UUID primary keys.
- `Job.status` supports `published` and `cancelled`.

### `app/payload.json`
- Example or placeholder payload data used by the app.

### `app/test_register.py`
- Manual or helper script for testing registration-related backend behavior.

---

## Backend Routes (`app/routes/`)

### `app/routes/__init__.py`
- Likely defines package initialization for routing.

### `app/routes/auth.py`
- Handles registration and login endpoints.
- Likely includes JWT issuance and user role assignment.

### `app/routes/profile.py`
- Profile retrieval and update endpoints for users.
- Possibly integrates applicant and recruiter profile info.

### `app/routes/resumes.py`
- Resume upload, parse, and management endpoints.
- Works with `app/services/pdf_parser.py`, `docx_parser.py`, and `resume_parser.py`.

### `app/routes/jobs.py`
- Job creation, listing, application, cancellation, and resume scoring.
- Key behaviors:
  - `POST /api/jobs` creates a published job.
  - `GET /api/jobs` lists only `published` jobs, optionally filtered by recruiter.
  - `POST /api/jobs/<job_id>/apply` lets applicants apply to a published job.
  - `DELETE /api/jobs/<job_id>/apply` cancels an applicant application.
  - `DELETE /api/jobs/<job_id>` lets a recruiter soft-cancel their own published job by setting `status='cancelled'`.
  - `POST /api/jobs/<job_id>/score-resume` scores a resume against job requirements.

### `app/routes/applicant.py`
- Applicant-specific route handlers, likely for applicant actions outside the dashboard.

### `app/routes/applicant_dashboard.py`
- Provides dashboard data for applicants.
- Likely returns jobs, applications, scores, and profile-related info.

### `app/routes/recruiter_dashboard.py`
- Provides recruiter dashboard data.
- Supplies active jobs, top candidates, total candidates, and match summaries.

### `app/routes/public.py`
- Public-facing endpoints, possibly health checks or open data.

---

## Backend Services (`app/services/`)

### `resume_parser.py`
- Central resume parsing logic.
- Likely delegates to PDF/DOCX parser modules and extracts structured fields.

### `pdf_parser.py`
- Parses PDF resumes and extracts text.

### `docx_parser.py`
- Parses DOCX resumes.

### `info_extractor.py`, `experience_extractor.py`, `education_extractor.py`
- Specialized extraction of resume fields such as contact info, work experience, and education.

### `skill_matcher.py`
- Handles skill matching logic between resumes and job requirements.
- Probably used for scoring or candidate ranking.

---

## Backend Utilities (`app/utils/`)

### `parser.py`
- Helper functions for parsing raw text and normalizing data.

### `scorer.py`
- Core scoring or matching algorithms.
- Likely used by route handlers and dashboard logic.

### `feedback.py`
- Possibly generates user-facing feedback messages, skill gap suggestions, or parse diagnostics.

---

## Database Migrations (`migrations/`)

### `001_tables.sql`
- Initial table creation SQL.

### `002_tables.sql`
- Additional schema modifications or new tables.

---

## Frontend Structure (`frontend/`)

### `frontend/package.json`
- Frontend dependencies and npm scripts.
- Likely includes React, Vite, shadcn/ui, Lucide icons, axios, and router packages.

### `frontend/vite.config.ts`
- Vite configuration for development and build.

### `frontend/components.json`
- shadcn component registry config.

### `frontend/src/main.tsx`
- React entry point that renders `App` and likely includes global styles.

### `frontend/src/lib/utils.ts`
- Utility functions used in the frontend, such as `cn()` for class merging.

### `frontend/src/hooks/use-mobile.tsx`
- Custom hook to detect mobile viewport or device properties.

### `frontend/src/hooks/use-toast.ts`
- Toast state and API used by frontend components.
- Centralized toast actions for success, error, and dismissal.

### `frontend/src/components/ApplicantLayout.tsx`
- Layout wrapper for applicant pages.
- Likely includes navigation, sidebar, or consistent page chrome.

### `frontend/src/components/RecruiterLayout.tsx`
- Layout wrapper for recruiter pages.

### `frontend/src/components/ApplyJobModal.tsx`
- Modal UI for applicants to apply to a job.

### `frontend/src/components/VisualBackground.tsx`
- Visual styling background component used on landing or dashboard screens.

---

## Frontend UI Components (`frontend/src/components/ui/`)

This directory contains shadcn-based UI primitives used throughout the app. Notable files:
- `alert.tsx`, `alert-dialog.tsx`, `button.tsx`, `badge.tsx`
- `card.tsx`, `dialog.tsx`, `input.tsx`, `label.tsx`
- `toast.tsx`, `toaster.tsx`
- `table.tsx`, `tabs.tsx`, `select.tsx`
- Various layout, form, and navigation components.

These files are mostly reusable design system primitives.

---

## Frontend Pages (`frontend/src/pages/`)

### Main Pages
- `LandingPage.tsx` — Public homepage.
- `LoginPage.tsx` — Login form for applicants/recruiters.
- `RegisterPage.tsx` — Registration page.
- `PreviewPage.tsx` — Demo/preview content page.
- `not-found.tsx` — 404 fallback.
- `ChangePasswordPage.tsx` — Password update flow.

### Applicant Pages (`frontend/src/pages/applicant/`)
- `Dashboard.tsx` — Applicant dashboard overview and status.
- `Resume.tsx` — Resume upload/parsing page.
- `JobMatches.tsx` — Job matching and recommended listing.
- `SkillGap.tsx` — Skill gap visualization and recommendations.
- `Profile.tsx` — Applicant profile settings.

### Recruiter Pages (`frontend/src/pages/recruiter/`)
- `Dashboard.tsx` — Recruiter overview, active postings, top candidates, and cancel flow.
- `PostJob.tsx` — Job posting form with toast-based success/error feedback.
- `Candidates.tsx` — Candidate list view.
- `BulkScreening.tsx` — Bulk screening page.
- `Profile.tsx` — Recruiter profile edit page.

---

## Routing and Layout

### `frontend/src/app/routes.tsx`
- Defines all client-side routes.
- Uses `createBrowserRouter` from React Router.
- Maps applicant and recruiter pages into their respective layout components.

### `frontend/src/app/App.tsx`
- Renders the router provider for the application.

---

## Current Important Behavior

### Applicant Cancellation
- Backend: `DELETE /api/jobs/<job_id>/apply` removes the `Application` record.
- Frontend: Applicant pages likely call this endpoint to cancel applications.

### Recruiter Job Cancellation
- Backend: `DELETE /api/jobs/<job_id>` soft-cancels jobs by setting `Job.status = 'cancelled'`.
- Frontend: `frontend/src/pages/recruiter/Dashboard.tsx` uses `AlertDialog` and `useToast` for confirmation and feedback.
- Jobs with `status === 'cancelled'` are filtered out of active listings.

### UI Notification Handling
- The repository uses React-based toast notifications instead of browser `alert()`.
- `frontend/src/hooks/use-toast.ts` is the centralized toast API.
- `frontend/src/components/ui/alert-dialog.tsx` provides an app-native confirmation dialog.

---

## Tests

### `tests/test_auth_register.py`
- Authentication and registration test coverage.

### `tests/test_scorer.py`
- Tests scoring logic, likely for `app/utils/scorer.py`.

---

## Training / Resume Model

### `training/`
- Contains annotated data, Spacy conversion scripts, training scripts, and output models.
- `training/output_model/` stores a trained spaCy NER/resume parsing model.
- `app/models/resume_ner/` mirrors the trained model artifact structure.

---

## Uploads

### `uploads/avatars/`
- Storage for avatar uploads.
- May be used by applicant/recruiter profile photo uploading flows.

---

## Notes & Suggested Focus Areas

- The backend relies on schema migration logic inside `app/__init__.py`, so schema drift is possible if the DB configuration changes.
- The job cancellation flow is currently a soft cancel; canceled jobs remain in the database but are excluded from active listings.
- Review auth and JWT enforcement because current frontend role storage appears local-only.
- The frontend contains many reusable shadcn UI components; page behavior is centralized via layout wrappers and routes.
- If you need a more targeted file list or deeper per-file details, this overview can be expanded into a dedicated docs folder.
