import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_organization_success(async_client: AsyncClient, sample_organization_data: dict):
    """Test successful organization signup."""
    response = await async_client.post("/api/tenant/signup/organization", json=sample_organization_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user_id" in data
    assert "tenant_id" in data
    
    # Verify the response contains expected data
    assert isinstance(data["user_id"], str)
    assert isinstance(data["tenant_id"], str)
