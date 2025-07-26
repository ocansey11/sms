from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/login.feature")

@given(parsers.parse('an organization admin account exists with email "{email}" and password "{password}"'))
def create_org_admin(email, password):
    payload = {
        "organization_name": "Login School",
        "admin_first_name": "Admin",
        "admin_last_name": "User",
        "admin_email": email,
        "admin_password": password
    }
    client.post("/api/auth/signup/organization", json=payload)

@given(parsers.parse('a teacher account exists with email "{email}" and password "{password}"'))
def create_teacher(email, password):
    payload = {
        "teacher_first_name": "Teacher",
        "teacher_last_name": "User",
        "teacher_email": email,
        "teacher_password": password
    }
    client.post("/api/auth/signup/teacher", json=payload)

@when(parsers.parse('I log in with email "{email}" and password "{password}"'))
def login(email, password):
    payload = {
        "email": email,
        "password": password
    }
    response = client.post("/api/auth/login", json=payload)
    return response

@then("I should be redirected to the admin dashboard")
def admin_dashboard(login):
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert data.get("role") == "admin" or "admin" in data.get("access_token", "")

@then("I should be redirected to the teacher dashboard")
def teacher_dashboard(login):
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert data.get("role") == "teacher" or "teacher" in data.get("access_token", "")

@then("I should see an error about invalid credentials")
def invalid_credentials(login):
    assert login.status_code == 401