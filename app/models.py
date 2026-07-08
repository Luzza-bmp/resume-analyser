import uuid
from app import db
from sqlalchemy.dialects.postgresql import ARRAY


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    # attribute name should be user_id, not id, because in the database, the column is named user_id. If we use id, it will not match the column name in the database and will cause an error when trying to access or manipulate user records.
    user_id = db.Column(db.UUID(as_uuid=True),
                        primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Applicant(db.Model):
    __tablename__ = "applicants"
    __table_args__ = {"schema": "public"}

    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey(
        "public.users.user_id", ondelete="CASCADE"), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Numeric, nullable=True)
    skills = db.Column(ARRAY(db.String), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Recruiter(db.Model):
    __tablename__ = "recruiters"
    __table_args__ = {"schema": "public"}

    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey(
        "public.users.user_id", ondelete="CASCADE"), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    job_title = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

class Resume(db.Model):
    __tablename__ = "resumes"
    __table_args__ = {"schema": "public"}

    resume_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey(
        "public.applicants.user_id", ondelete="CASCADE"), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    experience_years = db.Column(db.Numeric, nullable=True)
    skills = db.Column(ARRAY(db.String), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Analysis(db.Model):
    __tablename__ = "analyses"
    __table_args__ = {"schema": "public"}

    analysis_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey(
        "public.resumes.resume_id", ondelete="CASCADE"), nullable=False)
    jd_text = db.Column(db.Text, nullable=True)
    match_score = db.Column(db.Numeric, nullable=True)
    format_score = db.Column(db.Numeric, nullable=True)
    overall_score = db.Column(db.Numeric, nullable=True)
    matched_skills = db.Column(ARRAY(db.String), nullable=True)
    missing_skills = db.Column(ARRAY(db.String), nullable=True)
    suggestions = db.Column(ARRAY(db.String), nullable=True)
    analyzed_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Job(db.Model):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "public"}

    job_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.recruiters.user_id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    skills = db.Column(ARRAY(db.String), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    salary_min = db.Column(db.Numeric, nullable=True)
    salary_max = db.Column(db.Numeric, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="published")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = {"schema": "public"}

    application_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.jobs.job_id", ondelete="CASCADE"), nullable=False)
    applicant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.applicants.user_id", ondelete="CASCADE"), nullable=False)
    resume_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.resumes.resume_id", ondelete="SET NULL"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="applied")  # applied | reviewed | shortlisted | rejected
    applied_at = db.Column(db.DateTime, default=db.func.current_timestamp())