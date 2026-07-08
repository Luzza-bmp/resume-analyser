import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app import db
from app.models import User, Applicant, Recruiter

profile_bp = Blueprint("profile", __name__)

AVATAR_FOLDER = os.path.join("uploads", "avatars")
if not os.path.exists(AVATAR_FOLDER):
    os.makedirs(AVATAR_FOLDER)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route("/avatars/<filename>")
def serve_avatar(filename):
    """Serve avatar images stored on disk."""
    return send_from_directory(os.path.abspath(AVATAR_FOLDER), filename)


@profile_bp.route("/<user_id>", methods=["GET"])
def get_profile(user_id):
    """Return profile data for the given user_id (works for both roles)."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == "applicant":
        applicant = Applicant.query.get(user_id)
        if not applicant:
            # Return empty profile with the user's email
            return jsonify({
                "user_id": user_id,
                "role": user.role,
                "name": "",
                "email": user.email,
                "phone": "",
                "location": "",
                "avatar_url": "",
            }), 200

        avatar_url = ""
        if applicant.avatar_url:
            avatar_url = request.host_url.rstrip("/") + "/api/profile/avatars/" + os.path.basename(applicant.avatar_url)

        return jsonify({
            "user_id": user_id,
            "role": user.role,
            "name": applicant.name or "",
            "email": applicant.email or user.email,
            "phone": applicant.phone or "",
            "location": applicant.location or "",
            "avatar_url": avatar_url,
        }), 200

    elif user.role == "recruiter":
        recruiter = Recruiter.query.get(user_id)
        if not recruiter:
            return jsonify({
                "user_id": user_id,
                "role": user.role,
                "name": "",
                "email": user.email,
                "phone": "",
                "location": "",
                "company": "",
                "job_title": "",
                "avatar_url": "",
            }), 200

        avatar_url = ""
        if recruiter.avatar_url:
            avatar_url = request.host_url.rstrip("/") + "/api/profile/avatars/" + os.path.basename(recruiter.avatar_url)

        return jsonify({
            "user_id": user_id,
            "role": user.role,
            "name": recruiter.name or "",
            "email": recruiter.email or user.email,
            "phone": recruiter.phone or "",
            "location": recruiter.location or "",
            "company": recruiter.company or "",
            "job_title": recruiter.job_title or "",
            "avatar_url": avatar_url,
        }), 200

    return jsonify({"error": "Unknown role"}), 400


@profile_bp.route("/<user_id>", methods=["PUT"])
def update_profile(user_id):
    """Update profile data + optional avatar upload for the given user_id."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    name = request.form.get("name", "")
    email = request.form.get("email", "")
    phone = request.form.get("phone", "")
    location = request.form.get("location", "")
    remove_avatar = request.form.get("remove_avatar", "").lower() == "true"

    # Handle avatar upload
    avatar_filename = None
    if remove_avatar:
        avatar_filename = ""  # will clear the stored path
    elif "avatar" in request.files:
        file = request.files["avatar"]
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            unique_name = f"{user_id}_{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(AVATAR_FOLDER, unique_name)
            file.save(save_path)
            avatar_filename = save_path  # stored relative path

    if user.role == "applicant":
        applicant = Applicant.query.get(user_id)
        if not applicant:
            applicant = Applicant(user_id=user_id)
            db.session.add(applicant)

        applicant.name = name
        applicant.email = email or applicant.email
        applicant.phone = phone
        applicant.location = location
        if avatar_filename is not None:
            applicant.avatar_url = avatar_filename

        db.session.commit()

        avatar_url = ""
        if applicant.avatar_url:
            avatar_url = request.host_url.rstrip("/") + "/api/profile/avatars/" + os.path.basename(applicant.avatar_url)

        return jsonify({
            "message": "Profile updated",
            "avatar_url": avatar_url,
        }), 200

    elif user.role == "recruiter":
        company = request.form.get("company", "")
        job_title = request.form.get("job_title", "")

        recruiter = Recruiter.query.get(user_id)
        if not recruiter:
            recruiter = Recruiter(user_id=user_id)
            db.session.add(recruiter)

        recruiter.name = name
        recruiter.email = email or recruiter.email
        recruiter.phone = phone
        recruiter.location = location
        recruiter.company = company
        recruiter.job_title = job_title
        if avatar_filename is not None:
            recruiter.avatar_url = avatar_filename

        db.session.commit()

        avatar_url = ""
        if recruiter.avatar_url:
            avatar_url = request.host_url.rstrip("/") + "/api/profile/avatars/" + os.path.basename(recruiter.avatar_url)

        return jsonify({
            "message": "Profile updated",
            "avatar_url": avatar_url,
        }), 200

    return jsonify({"error": "Unknown role"}), 400
