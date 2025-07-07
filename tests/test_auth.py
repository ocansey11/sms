import pytest
from fastapi.testclient import TestClient

from tests.conftest import client, sample_user_data, assert_user_response

class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_register_user(self, client: TestClient, sample_user_data: dict):
        """Test user registration."""
        response = client.post("/api/auth/register", json=sample_user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert_user_response(data, sample_user_data)
    
    def test_register_duplicate_user(self, client: TestClient, sample_user_data: dict):
        """Test registering a user with duplicate email."""
        # Register user first time
        response = client.post("/api/auth/register", json=sample_user_data)
        assert response.status_code == 201
        
        # Try to register again with same email
        response = client.post("/api/auth/register", json=sample_user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_login_user(self, client: TestClient, sample_user_data: dict):
        """Test user login."""
        # Register user first
        client.post("/api/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, sample_user_data: dict):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Test getting current user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "role" in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_refresh_token(self, client: TestClient, sample_user_data: dict):
        """Test token refresh."""
        # Register and login
        client.post("/api/auth/register", json=sample_user_data)
        
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_change_password(self, client: TestClient, auth_headers: dict):
        """Test password change."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        response = client.post("/api/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"
