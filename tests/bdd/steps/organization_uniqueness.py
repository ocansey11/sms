from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios("../features/organization_uniqueness.feature")

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

@when(parsers.parse('I sign up another organization with the name "{org_name}"'))
def unique_org_signup(org_name):
    payload = {
        "organization_name": org_name,
        "admin_first_name": "Sam",
        "admin_last_name": "Lee",
        "admin_email": f"sam_{org_name.replace(' ', '').lower()}@school.edu",
        "admin_password": "StrongPass123!"
    }
    response = client.post("/api/auth/signup/organization", json=payload)
    return response

@then("I should see a confirmation that the organization was registered")
def org_signup_confirmation(unique_org_signup):
    assert unique_org_signup.status_code == 200
    data = unique_org_signup.json()
    assert data["success"] is True