from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy import inspect, text

db = SQLAlchemy()
jwt = JWTManager()


def ensure_applicant_table_schema():
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names(schema="public"))

    if "applicants" not in tables:
        db.create_all()
        return

    columns = {column["name"] for column in inspector.get_columns("applicants", schema="public")}

    with db.engine.begin() as connection:
        if "name" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN name VARCHAR(255)"))
        if "email" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN email VARCHAR(255)"))
        if "phone" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN phone VARCHAR(50)"))
        if "education" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN education TEXT"))
        if "experience" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN experience NUMERIC"))
        if "skills" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN skills TEXT[]"))
        if "created_at" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
        if "location" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN location VARCHAR(255)"))
        if "avatar_url" not in columns:
            connection.execute(text("ALTER TABLE public.applicants ADD COLUMN avatar_url VARCHAR(500)"))

    # Ensure jobs table has required columns
    if "jobs" in tables:
        job_columns = {col["name"] for col in inspector.get_columns("jobs", schema="public")}
        with db.engine.begin() as connection:
            if "skills" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN skills VARCHAR[]"))
            if "experience_level" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN experience_level VARCHAR(50)"))
            if "job_type" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN job_type VARCHAR(50)"))
            if "location" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN location VARCHAR(255)"))
            if "salary_min" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN salary_min NUMERIC"))
            if "salary_max" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN salary_max NUMERIC"))
            # Ensure status column exists with default 'published'
            if "status" not in job_columns:
                connection.execute(text("ALTER TABLE public.jobs ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'"))

    # Migrate recruiters table
    if "recruiters" in tables:
        rec_columns = {col["name"] for col in inspector.get_columns("recruiters", schema="public")}
        with db.engine.begin() as connection:
            if "name" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN name VARCHAR(255)"))
            if "email" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN email VARCHAR(255)"))
            if "phone" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN phone VARCHAR(50)"))
            if "location" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN location VARCHAR(255)"))
            if "company" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN company VARCHAR(255)"))
            if "job_title" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN job_title VARCHAR(255)"))
            if "avatar_url" not in rec_columns:
                connection.execute(text("ALTER TABLE public.recruiters ADD COLUMN avatar_url VARCHAR(500)"))

    # Migrate resumes table — add columns that exist in the model but not in the original DB dump
    if "resumes" in tables:
        res_columns = {col["name"] for col in inspector.get_columns("resumes", schema="public")}
        with db.engine.begin() as connection:
            if "name" not in res_columns:
                connection.execute(text("ALTER TABLE public.resumes ADD COLUMN name VARCHAR(255)"))
            if "email" not in res_columns:
                connection.execute(text("ALTER TABLE public.resumes ADD COLUMN email VARCHAR(255)"))
            if "phone" not in res_columns:
                connection.execute(text("ALTER TABLE public.resumes ADD COLUMN phone VARCHAR(50)"))
            if "experience_years" not in res_columns:
                connection.execute(text("ALTER TABLE public.resumes ADD COLUMN experience_years NUMERIC"))
            if "skills" not in res_columns:
                connection.execute(text("ALTER TABLE public.resumes ADD COLUMN skills TEXT[]"))

    # Migrate analyses table
    if "analyses" in tables:
        an_columns = {col["name"] for col in inspector.get_columns("analyses", schema="public")}
        with db.engine.begin() as connection:
            if "jd_text" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN jd_text TEXT"))
            if "match_score" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN match_score NUMERIC"))
            if "format_score" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN format_score NUMERIC"))
            if "overall_score" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN overall_score NUMERIC"))
            if "matched_skills" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN matched_skills TEXT[]"))
            if "missing_skills" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN missing_skills TEXT[]"))
            if "suggestions" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN suggestions TEXT[]"))
            if "analyzed_at" not in an_columns:
                connection.execute(text("ALTER TABLE public.analyses ADD COLUMN analyzed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP"))

    # Ensure applications table exists
    if "applications" not in tables:
        with db.engine.begin() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.applications (
                    application_id UUID PRIMARY KEY,
                    job_id UUID NOT NULL REFERENCES public.jobs(job_id) ON DELETE CASCADE,
                    applicant_id UUID NOT NULL REFERENCES public.applicants(user_id) ON DELETE CASCADE,
                    resume_id UUID REFERENCES public.resumes(resume_id) ON DELETE SET NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'applied',
                    applied_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
    else:
        app_columns = {col["name"] for col in inspector.get_columns("applications", schema="public")}
        with db.engine.begin() as connection:
            if "resume_id" not in app_columns:
                connection.execute(text("ALTER TABLE public.applications ADD COLUMN resume_id UUID REFERENCES public.resumes(resume_id) ON DELETE SET NULL"))
            if "status" not in app_columns:
                connection.execute(text("ALTER TABLE public.applications ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'applied'"))
            if "applied_at" not in app_columns:
                connection.execute(text("ALTER TABLE public.applications ADD COLUMN applied_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP"))





def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ])

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        ensure_applicant_table_schema()

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from app.routes.profile import profile_bp
    app.register_blueprint(profile_bp, url_prefix="/api/profile")

    from app.routes.resumes import resumes_bp
    app.register_blueprint(resumes_bp, url_prefix="/api/resumes")

    from app.routes.jobs import jobs_bp
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    from app.routes.applicant_dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix="/api/applicants")
    from app.routes.recruiter_dashboard import recruiter_dashboard_bp
    app.register_blueprint(recruiter_dashboard_bp, url_prefix="/api/recruiters")
    from app.routes.public import public_bp
    app.register_blueprint(public_bp, url_prefix="/api/public")

    with app.app_context():
        # WARNING: This drops all tables and recreates them from models.
        # Suitable for development environment only.
        # db.drop_all()  # Disabled to avoid dropping dependent tables during development
        db.create_all()

    return app