from flask import Flask

from app.routes import auth as auth_module


class FakeSession:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass


class FakeQuery:
    def __init__(self, existing=False):
        self.existing = existing

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return None if not self.existing else object()


class FakeUser:
    query = FakeQuery()

    def __init__(self, email, password_hash, role):
        self.user_id = "user-123"
        self.email = email
        self.password_hash = password_hash
        self.role = role


class FakeRecruiter:
    def __init__(self, user_id, email, name=None):
        self.user_id = user_id
        self.email = email
        self.name = name


def test_recruiter_registration_saves_name(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(auth_module, "db", type("DB", (), {"session": fake_session}))
    monkeypatch.setattr(auth_module, "User", FakeUser)
    monkeypatch.setattr(auth_module, "Recruiter", FakeRecruiter)
    monkeypatch.setattr(auth_module, "bcrypt", type("bcrypt", (), {"hashpw": lambda password, salt: b"hash", "gensalt": lambda: b"salt", "checkpw": lambda password, hashed: True}))

    app = Flask(__name__)
    app.register_blueprint(auth_module.auth_bp, url_prefix="/api/auth")

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={"name": "Jane Recruiter", "email": "jane@example.com", "password": "Strong123", "role": "recruiter"},
    ):
        response = auth_module.register()

    assert response[1] == 201
    recruiter = next(obj for obj in fake_session.added if isinstance(obj, FakeRecruiter))
    assert recruiter.name == "Jane Recruiter"


def test_recruiter_registration_rejects_short_password(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(auth_module, "db", type("DB", (), {"session": fake_session}))
    monkeypatch.setattr(auth_module, "User", FakeUser)
    monkeypatch.setattr(auth_module, "Recruiter", FakeRecruiter)
    monkeypatch.setattr(auth_module, "bcrypt", type("bcrypt", (), {"hashpw": lambda password, salt: b"hash", "gensalt": lambda: b"salt", "checkpw": lambda password, hashed: True}))

    app = Flask(__name__)
    app.register_blueprint(auth_module.auth_bp, url_prefix="/api/auth")

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={"name": "Jane Recruiter", "email": "jane2@example.com", "password": "short", "role": "recruiter"},
    ):
        response = auth_module.register()

    assert response[1] == 400
    assert b"at least 8 characters" in response[0].get_data()
