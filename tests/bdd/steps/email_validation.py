from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/email_validation.feature")

@given("I am on the organization sign up page")
def org_signup_page():
    pass

@when(parsers.parse('I enter an invalid admin email "{email}"'))
def invalid_admin_email(email):
    return {
        "organization_name": "Invalid Email Org",
        "admin_first_name": "Test",
        "admin_last_name": "User",
        "admin_email": email,
        "admin_password": "StrongPass123!"
    }

@when("I submit the organization sign up form")
def submit_org_signup(invalid_admin_email):
    response = client.post("/api/auth/signup/organization", json=invalid_admin_email)
    return response

@then("I should see an error about invalid email format")
def org_invalid_email_error(submit_org_signup):
    assert submit_org_signup.status_code in (400, 422)
    assert "email" in submit_org_signup.json()["detail"].lower()

@given("I am on the teacher sign up page")
def teacher_signup_page():
    pass

@when(parsers.parse('I enter an invalid teacher email "{email}"'))
def invalid_teacher_email(email):
    return {
        "teacher_first_name": "Test",
        "teacher_last_name": "User",
        "teacher_email": email,
        "teacher_password": "StrongPass123!"
    }

@when("I submit the teacher sign up form")
def submit_teacher_signup(invalid_teacher_email):
    response = client.post("/api/auth/signup/teacher", json=invalid_teacher_email)
    return response

@then("I should see an error about invalid email format")
def teacher_invalid_email_error(submit_teacher_signup):
    assert submit_teacher_signup.status_code in (400, 422)
    assert "email" in submit_teacher_signup.json()["detail"].lower()

@when(parsers.parse('I enter a valid admin email "{email}"'))
def valid_admin_email(email):
    return {
        "organization_name": "Valid Email Org",
        "admin_first_name": "Test",
        "admin_last_name": "User",
        "admin_email": email,
        "admin_password": "StrongPass123!"
    }

@then("I should see a confirmation that the organization was registered")
def org_signup_confirmation(submit_org_signup):
    assert submit_org_signup.status_code == 200
    data = submit_org_signup.json()
    assert data["success"] is True

@when(parsers.parse('I enter a valid teacher email "{email}"'))
def valid_teacher_email(email):
    return {
        "teacher_first_name": "Test",
        "teacher_last_name": "User",
        "teacher_email": email,
        "teacher_password": "StrongPass123!"
    }

@then("I should see a confirmation that the teacher was registered")
def teacher_signup_confirmation(submit_teacher_signup):
    assert submit_teacher_signup.status_code == 200
    data = submit_teacher_signup.json()
    assert data["success"] is True