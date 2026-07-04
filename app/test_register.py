from app import create_app
import traceback

try:
	app = create_app()
	client = app.test_client()

	resp = client.post('/api/auth/register', json={'name':'Test Recruiter','email':'recruiter-test@example.com','password':'pass','role':'recruiter'})
	print(resp.status_code)
	print(resp.get_data(as_text=True))
except Exception:
	traceback.print_exc()
