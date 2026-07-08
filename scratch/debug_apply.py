import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import User, Job, Application, Resume

app = create_app()
with app.app_context():
    # Find any applicant
    applicant = User.query.filter_by(role='applicant').first()
    if not applicant:
        print("No applicant found in DB")
        sys.exit(1)

    # Find any job
    job = Job.query.first()
    if not job:
        print("No job found in DB")
        sys.exit(1)

    print(f"Testing application for applicant: {applicant.user_id} (email: {applicant.email}) and job: {job.job_id} (title: {job.title})")
    
    # Try to insert directly or simulate what Flask does
    try:
        # Check if already exists
        existing = Application.query.filter_by(job_id=job.job_id, applicant_id=applicant.user_id).first()
        if existing:
            print("Application already exists, deleting it to test fresh...")
            db.session.delete(existing)
            db.session.commit()

        resume = Resume.query.filter_by(applicant_id=applicant.user_id).first()
        resume_id = resume.resume_id if resume else None
        print(f"Linking resume: {resume_id}")

        new_app = Application(
            job_id=job.job_id,
            applicant_id=applicant.user_id,
            resume_id=resume_id,
            status='applied'
        )
        db.session.add(new_app)
        db.session.commit()
        print("Successfully created application record in database!")
    except Exception as e:
        import traceback
        print("Failed with exception:")
        traceback.print_exc()
