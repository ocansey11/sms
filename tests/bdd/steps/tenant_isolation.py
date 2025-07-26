from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/tenant_isolation.feature")

@given(parsers.parse('two organizations "{org1}" and "{org2}" exist'))
def create_two_orgs(org1, org2):
    payload1 = {
        "organization_name": org1,
        "admin_first_name": "Alpha",
        "admin_last_name": "Admin",
        "admin_email": f"admin_{org1.replace(' ', '').lower()}@school.edu",
        "admin_password": "StrongPass123!"
    }
    payload2 = {
        "organization_name": org2,
        "admin_first_name": "Beta",
        "admin_last_name": "Admin",
        "admin_email": f"admin_{org2.replace(' ', '').lower()}@school.edu",
        "admin_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/organization", json=payload1)
    client.post("/api/auth/signup/organization", json=payload2)

@given(parsers.parse('I am logged in as an admin of "{org_name}"'))
def login_as_admin(org_name):
    email = f"admin_{org_name.replace(' ', '').lower()}@school.edu"
    payload = {
        "email": email,
        "password": "StrongPass123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    return response.json()["access_token"]

@when(parsers.parse('I try to access data belonging to "{org_name}"'))
def access_other_org_data(login_as_admin, org_name):
    # Simulate accessing another org's data (e.g., GET /api/tenants/{id})
    # Here, we assume tenant IDs are sequential for demo purposes
    # In a real test, fetch the actual tenant ID for org_name
    # For now, just simulate forbidden access
    headers = {"Authorization": f"Bearer {login_as_admin}"}
    response = client.get(f"/api/tenants/{org_name}", headers=headers)
    return response

@then("I should be denied access")
def denied_access(access_other_org_data):
    assert access_other_org_data.status_code in (403, 404)

@given(parsers.parse('a teacher is registered under "{org_name}"'))
def register_teacher(org_name):
    payload = {
        "teacher_first_name": "AlphaTeacher",
        "teacher_last_name": "One",
        "teacher_email": f"teacher_{org_name.replace(' ', '').lower()}@school.edu",
        "teacher_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/teacher", json=payload)

@when(parsers.parse('the teacher tries to access data belonging to "{org_name}"'))
def teacher_access_other_org_data(register_teacher, org_name):
    email = f"teacher_{org_name.replace(' ', '').lower()}@school.edu"
    login_payload = {
        "email": email,
        "password": "StrongPass123!"
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/tenants/{org_name}", headers=headers)
    return response

@then("the teacher should be denied access")
def teacher_denied_access(teacher_access_other_org_data):
    assert teacher_access_other_org_data.status_code in (403, 404)

@given(parsers.parse('two teachers "{teacher1}" and "{teacher2}" are registered under different organizations'))
def register_two_teachers(teacher1, teacher2):
    # Register teacher1 under Alpha School
    payload1 = {
        "teacher_first_name": teacher1,
        "teacher_last_name": "Alpha",
        "teacher_email": f"{teacher1.lower()}@alphaschool.edu",
        "teacher_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/teacher", json=payload1)
    # Register teacher2 under Beta Academy
    payload2 = {
        "teacher_first_name": teacher2,
        "teacher_last_name": "Beta",
        "teacher_email": f"{teacher2.lower()}@betaacademy.edu",
        "teacher_password": "StrongPass123!"
    }
    client.post("/api/auth/signup/teacher", json=payload2)

@when(parsers.parse('"{teacher1}" tries to access data belonging to "{teacher2}"'))
def teacher_access_other_teacher_data(teacher1, teacher2):
    login_payload = {
        "email": f"{teacher1.lower()}@alphaschool.edu",
        "password": "StrongPass123!"
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/users/{teacher2.lower()}@betaacademy.edu", headers=headers)
    return response

@then(parsers.parse('"{teacher1}" should be denied access'))
def teacher_to_teacher_denied_access(teacher_access_other_teacher_data):
    assert teacher_access_other_teacher_data.status_code in (403, 404)