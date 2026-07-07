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


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175"
    ])

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        ensure_applicant_table_schema()

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from app.routes.applicant import applicant_bp
    app.register_blueprint(applicant_bp, url_prefix="/api/applicant")

    with app.app_context():
        db.create_all()

    return app