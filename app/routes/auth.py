from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Recruiter
import bcrypt

# blueprint is a way to organize a group of related routes and views in a Flask application.
# It allows you to modularize your application and keep related functionality together.
# In this case, auth_bp is a Blueprint instance that will contain all the routes related to authentication (like register, login, and me).
auth_bp = Blueprint("auth", __name__)

# Password policy helper

def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(c.islower() for c in password)
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
    )


def password_policy_message() -> str:
    return "Password must be at least 8 characters long and include uppercase, lowercase, and a number."


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "").strip().lower()

    # Basic validation
    if not email or not password or not role:
        return jsonify({"error": "email, password, and role are required"}), 400

    if not is_strong_password(password):
        return jsonify({"error": password_policy_message()}), 400

    if role not in ("applicant", "recruiter"):
        return jsonify({"error": "role must be 'applicant' or 'recruiter'"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = User(email=email, password_hash=password_hash, role=role)
    db.session.add(new_user)
    db.session.commit()

    if role == 'applicant':
        from app.models import Applicant
        applicant = Applicant(user_id=new_user.user_id, name=data.get('name'), email=new_user.email)
        db.session.add(applicant)
        db.session.commit()

    if role == 'recruiter':
        recruiter = Recruiter(user_id=new_user.user_id, name=data.get('name'), email=new_user.email)
        db.session.add(recruiter)
        db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": str(new_user.user_id),
        "email": new_user.email,
        "role": new_user.role
    }), 201


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    data = request.get_json()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not old_password or not new_password or not confirm_password:
        return jsonify({"error": "old_password, new_password, and confirm_password are required"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400

    if not is_strong_password(new_password):
        return jsonify({"error": password_policy_message()}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(old_password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Current password is incorrect"}), 401

    user.password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):#encode converts the password string into bytes, which is required by bcrypt. bcrypt.checkpw() compares the provided password (after encoding) with the stored password hash (also after encoding). If the user does not exist or the password does not match, it returns an error response indicating that the email or password is invalid.
        return jsonify({"error": "Invalid email or password"}), 401

    # Create JWT — store user_id and role in token
    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "user_id": str(user.user_id)
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": str(user.user_id),
        "email": user.email,
        "role": user.role
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200