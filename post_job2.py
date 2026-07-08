import requests, json

# Use the token obtained from login
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4MzQwOTU2NiwianRpIjoiZWUyZTFmZDAtNTI2YS00Yjg4LThjZGItNjgwMmIyZDBmMTE3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjFhMTllZDk4LTg0NTItNDlhNi1hMGUxLTkxMzE0NGY1ZmVmNSIsIm5iZiI6MTc4MzQwOTU2NiwiY3NyZiI6ImViZDkxOTI2LWI0MzItNDY2NC1iZWM0LWFlZTBlYTA4YzcyYiIsImV4cCI6MTc4MzQxMDQ2Niwicm9sZSI6InJlY3J1aXRlciJ9.JPb3UNZu8p52l2oBE89ScFcKVDU7pxg1vn5avncwiv4"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
payload = {
    "recruiter_id": "1a19ed98-8452-49a6-a0e1-913144f5fef5",
    "title": "Software Engineer",
    "description": "Develop cool software.",
    "skills": ["python", "flask"],
    "experience_level": "1-3",
    "job_type": "full",
    "location": "Remote",
    "salary_min": 5000,
    "salary_max": 8000
}
response = requests.post("http://127.0.0.1:5000/api/jobs", json=payload, headers=headers)
print("Status:", response.status_code)
print("Body:", response.text)
