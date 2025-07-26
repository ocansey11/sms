from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/signup.feature")

@given("I am on the organization sign up page")
def org_signup_page():
    pass  # UI navigation simulated for API test

@when("I enter valid organization details")
def enter_org_details():
    return {
        "organization_name": "Acme School",
        "admin_first_name": "Jane",
        "admin_last_name": "Doe",
        "admin_email": "jane@acmeschool.edu",
        "admin_password": "StrongPass123!"
    }

@when("I submit the organization sign up form")
def submit_org_signup(enter_org_details):
    response = client.post("/api/auth/signup/organization", json=enter_org_details)
    return response

@then("I should see a confirmation that the organization was registered")
def org_signup_confirmation(submit_org_signup):
    assert submit_org_signup.status_code == 200
    data = submit_org_signup.json()
    assert data["success"] is True

@given("I am on the teacher sign up page")
def teacher_signup_page():
    pass

@when("I enter valid teacher details")
def enter_teacher_details():
    return {
        "teacher_first_name": "John",
        "teacher_last_name": "Smith",
        "teacher_email": "john@teachers.com",
        "teacher_password": "StrongPass123!"
    }

@when("I submit the teacher sign up form")
def submit_teacher_signup(enter_teacher_details):
    response = client.post("/api/auth/signup/teacher", json=enter_teacher_details)
    return response

@then("I should see a confirmation that the teacher was registered")
def teacher_signup_confirmation(submit_teacher_signup):
    assert submit_teacher_signup.status_code == 200
    data = submit_teacher_signup.json()
    assert data["success"] is True

@given(parsers.parse('an organization named "{org_name}" already exists'))
def existing_org(org_name):
    payload = {
        "organization_name": org_name,
        "admin_first_name": "Jane",
        "admin_last_name": "Doe",
        "admin_email": "jane2@acmeschool.edu",
        "admin_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/organization", json=payload)

@when(parsers.parse('I try to sign up another organization with the name "{org_name}"'))
def duplicate_org_signup(org_name):
    payload = {
        "organization_name": org_name,
        "admin_first_name": "Jake",
        "admin_last_name": "Smith",
        "admin_email": "jake@acmeschool.edu",
        "admin_password": "StrongPass123!"
    }
    response = client.post("/api/auth/signup/organization", json=payload)
    return response

@then("I should see an error about duplicate organization name")
def duplicate_org_error(duplicate_org_signup):
    assert duplicate_org_signup.status_code == 400
    assert "already exists" in duplicate_org_signup.json()["detail"].lower()

@given(parsers.parse('a teacher with email "{email}" already exists'))
def existing_teacher(email):
    payload = {
        "teacher_first_name": "John",
        "teacher_last_name": "Smith",
        "teacher_email": email,
        "teacher_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/teacher", json=payload)

@when(parsers.parse('I try to sign up another teacher with the email "{email}"'))
def duplicate_teacher_signup(email):
    payload = {
        "teacher_first_name": "Jake",
        "teacher_last_name": "Smith",
        "teacher_email": email,
        "teacher_password": "StrongPass123!"
    }
    response = client.post("/api/auth/signup/teacher", json=payload)
    return response

@then("I should see an error about duplicate email")
def duplicate_teacher_error(duplicate_teacher_signup):
    assert duplicate_teacher_signup.status_code == 400
    assert "failed" in duplicate_teacher_signup.json()["detail"].lower()