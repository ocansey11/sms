import requests

url = "http://localhost:8000/api/auth/login"
data = {"email": "teacher@schoolsms.com", "password": "teacher123"}
response = requests.post(url, json=data)
print(response.json())
