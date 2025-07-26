from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/password_validation.feature")

@given("I am on the organization sign up page")
def org_signup_page():
    pass

@when(parsers.parse('I enter a weak admin password "{password}"'))
def weak_admin_password(password):
    return {
        "organization_name": "Weak Password Org",
        "admin_first_name": "Test",
        "admin_last_name": "User",
        "admin_email": "weakadmin@org.com",
        "admin_password": password
    }

@when("I submit the organization sign up form")
def submit_org_signup(weak_admin_password):
    response = client.post("/api/auth/signup/organization", json=weak_admin_password)
    return response

@then("I should see an error about password strength")
def weak_password_error(submit_org_signup):
    assert submit_org_signup.status_code == 400
    assert "password" in submit_org_signup.json()["detail"].lower()

@given("I am on the teacher sign up page")
def teacher_signup_page():
    pass

@when(parsers.parse('I enter a weak teacher password "{password}"'))
def weak_teacher_password(password):
    return {
        "teacher_first_name": "Weak",
        "teacher_last_name": "User",
        "teacher_email": "weakteacher@school.com",
        "teacher_password": password
    }

@when("I submit the teacher sign up form")
def submit_teacher_signup(weak_teacher_password):
    response = client.post("/api/auth/signup/teacher", json=weak_teacher_password)
    return response

@then("I should see an error about password strength")
def weak_teacher_password_error(submit_teacher_signup):
    assert submit_teacher_signup.status_code == 400
    assert "password" in submit_teacher_signup.json()["detail"].lower()

@when(parsers.parse('I enter a strong admin password "{password}"'))
def strong_admin_password(password):
    return {
        "organization_name": "Strong Password Org",
        "admin_first_name": "Test",
        "admin_last_name": "User",
        "admin_email": "strongadmin@org.com",
        "admin_password": password
    }


@when(parsers.parse('I enter a strong teacher password "{password}"'))
def strong_teacher_password(password):
    return {
        "teacher_first_name": "Strong",
        "teacher_last_name": "User",
        "teacher_email": "strongteacher@school.com",
        "teacher_password": password
    }
