import pytest
from unittest.mock import AsyncMock, patch

from typing import Optional, Any

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.organization import OrganizationResponse, Organization
from utilities.model_validator import safe_model_validate  # adjust as needed

# Dummy Authenticator that always returns a token
class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"

    def force_relogin(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_get_organization_valid_response():
    org_id = "123"

    # Mocking a valid response from the API
    mock_response = {
        "status": 200,
        "message": "Success",
        "data": {
            "id": "org123",
            "name": "Test Organization",
            "is2FARequired": True,
            "imageUrl": "http://example.com/image.jpg",
            "countryCode": "US",
            "timezone": "GMT",
            "auditHour": 12,
            "idleTimeout": 60
        }
    }

    # Create an instance of OVCirrusApiClient (replace with actual class)
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.organization.getOrganization(org_id)

    # Verify the result is an ApiResponse and contains the expected data
    assert result is not None
    assert isinstance(result, OrganizationResponse)
    assert isinstance(result.data, Organization)
    assert result.data.id == "org123"
    assert result.data.name == "Test Organization"
    assert result.data.is2FARequired is True
    assert result.data.imageUrl == "http://example.com/image.jpg"

@pytest.mark.asyncio
async def test_get_organization_no_response():
    org_id = "123"
    # Create an instance of OVCirrusApiClient (replace with actual class)
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Mocking the `get` method to return None
    with patch.object(BaseClient, 'get', AsyncMock(return_value=None)):
        result = await client.organization.getOrganization(org_id)
    
    # Assert that the result is None because there's no response
    assert result is None

@pytest.mark.asyncio
async def test_get_organization_invalid_status():
    org_id = "123"
    # Create an instance of OVCirrusApiClient (replace with actual class)
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Mocking an invalid API response (non-200 status code)
    mock_response = {
        "status": 400,
        "message": "Bad Request",
        "data": {}
    }

    # Mocking the `get` method to return None
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.organization.getOrganization(org_id)


    # Assert that the result is None because the status is not 200
    assert result is not None
    assert result.status == 400
    assert isinstance(result, OrganizationResponse)
    assert result.message == "Bad Request"

