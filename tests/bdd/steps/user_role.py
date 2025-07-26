from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/user_role.feature")

@given("an organization admin account exists")
def create_admin():
    payload = {
        "organization_name": "RoleTestOrg",
        "admin_first_name": "Admin",
        "admin_last_name": "User",
        "admin_email": "admin@roletestorg.edu",
        "admin_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/organization", json=payload)

@when("the admin logs in")
def admin_login():
    payload = {
        "email": "admin@roletestorg.edu",
        "password": "StrongPass123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    return response.json()["access_token"]

@then("the admin should have access to the admin dashboard")
def admin_dashboard_access(admin_login):
    # Simulate access to admin dashboard endpoint
    headers = {"Authorization": f"Bearer {admin_login}"}
    response = client.get("/api/admin/dashboard", headers=headers)
    assert response.status_code == 200

@given("a teacher account exists")
def create_teacher():
    payload = {
        "teacher_first_name": "Teacher",
        "teacher_last_name": "User",
        "teacher_email": "teacher@roletestorg.edu",
        "teacher_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/teacher", json=payload)

@when("the teacher logs in")
def teacher_login():
    payload = {
        "email": "teacher@roletestorg.edu",
        "password": "StrongPass123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    return response.json()["access_token"]

@then("the teacher should have access to the teacher dashboard")
def teacher_dashboard_access(teacher_login):
    headers = {"Authorization": f"Bearer {teacher_login}"}
    response = client.get("/api/teacher/dashboard", headers=headers)
    assert response.status_code == 200

@when("the teacher tries to access an admin-only endpoint")
def teacher_access_admin_endpoint(teacher_login):
    headers = {"Authorization": f"Bearer {teacher_login}"}
    response = client.get("/api/admin/dashboard", headers=headers)
    return response

@then("the teacher should be denied access")
def teacher_denied_admin_access(teacher_access_admin_endpoint):
    assert teacher_access_admin_endpoint.status_code == 403

@when("the admin tries to access a teacher-only endpoint")
def admin_access_teacher_endpoint(admin_login):
    headers = {"Authorization": f"Bearer {admin_login}"}
    response = client.get("/api/teacher/dashboard", headers=headers)
    return response

@then("the admin should be denied access")
def admin_denied_teacher_access(admin_access_teacher_endpoint):
    assert admin_access_teacher_endpoint.status_code == 403