from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/error_handling.feature")

@given("I am on the organization sign up page")
def org_signup_page():
    pass

@when("I submit the organization sign up form with missing admin email")
def submit_org_signup_missing_email():
    payload = {
        "organization_name": "Missing Email Org",
        "admin_first_name": "Test",
        "admin_last_name": "User",
        # "admin_email" is missing
        "admin_password": "StrongPass123!"
    }
    response = client.post("/api/auth/signup/organization", json=payload)
    return response

@then("I should see an error about missing required fields")
def missing_field_error(submit_org_signup_missing_email):
    assert submit_org_signup_missing_email.status_code in (400, 422)
    assert "email" in submit_org_signup_missing_email.json()["detail"].lower()

@given("I am on the teacher sign up page")
def teacher_signup_page():
    pass

@when(parsers.parse('I enter a weak teacher password "{password}"'))
def weak_teacher_password(password):
    return {
        "teacher_first_name": "Weak",
        "teacher_last_name": "Password",
        "teacher_email": "weak@teacher.com",
        "teacher_password": password
    }

@when("I submit the teacher sign up form")
def submit_teacher_signup(weak_teacher_password):
    response = client.post("/api/auth/signup/teacher", json=weak_teacher_password)
    return response

@then("I should see an error about password strength")
def weak_password_error(submit_teacher_signup):
    assert submit_teacher_signup.status_code == 400
    assert "password" in submit_teacher_signup.json()["detail"].lower()

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
    assert "duplicate" in duplicate_teacher_signup.json()["detail"].lower() or "exists" in duplicate_teacher_signup.json()["detail"].lower()

@given(parsers.parse('an organization named "{org_name}" already exists'))
def existing_org(org_name):
    payload = {
        "organization_name": org_name,
        "admin_first_name": "Jane",
        "admin_last_name": "Doe",
        "admin_email": f"jane_{org_name.replace(' ', '').lower()}@school.edu",
        "admin_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/organization", json=payload)

@when(parsers.parse('I try to sign up another organization with the name "{org_name}"'))
def duplicate_org_signup(org_name):
    payload = {
        "organization_name": org_name,
        "admin_first_name": "Jake",
        "admin_last_name": "Smith",
        "admin_email": f"jake_{org_name.replace(' ', '').lower()}@school.edu",
        "admin_password": "StrongPass123!"
    }
    response = client.post("/api/auth/signup/organization", json=payload)
    return response

@then("I should see an error about duplicate organization name")
def duplicate_org_error(duplicate_org_signup):
    assert duplicate_org_signup.status_code == 400
    assert "duplicate" in duplicate_org_signup.json()["detail"].lower() or "exists" in duplicate_org_signup.json()["detail"].lower()