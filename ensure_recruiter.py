import json
from app import create_app, db
from app.models import User, Recruiter

app = create_app()

# The recruiter user ID from previous registration
recruiter_user_id = "1a19ed98-8452-49a6-a0e1-913144f5fef5"

with app.app_context():
    user = User.query.filter_by(user_id=recruiter_user_id).first()
    if not user:
        print(f"User {recruiter_user_id} not found.")
    else:
        recruiter = Recruiter.query.filter_by(user_id=user.user_id).first()
        if recruiter:
            print(f"Recruiter entry already exists for user {user.user_id}")
        else:
            new_rec = Recruiter(user_id=user.user_id, email=user.email)
            db.session.add(new_rec)
            db.session.commit()
            print(f"Recruiter entry created for user {user.user_id}")
