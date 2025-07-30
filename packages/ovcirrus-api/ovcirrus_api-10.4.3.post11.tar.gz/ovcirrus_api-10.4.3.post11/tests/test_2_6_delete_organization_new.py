import pytest
from unittest.mock import AsyncMock, patch

from typing import Optional, Any

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.organization import OrganizationResponse, Organization

# Dummy Authenticator that always returns a token
class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"

    def force_relogin(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_delete_organization_success():

    # Mock successful response
    mock_success_response = {
        "status": 200, 
        "message": "Organization deleted successfully", 
        "data": {"orgId": "123"}
    }

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'delete', AsyncMock(return_value=mock_success_response)):
        response = await client.organization.deleteOrganization("123")      


    # Assertions for a successful response
    assert response is not None
    assert response.status == 200
    assert response.message == "Organization deleted successfully"
    assert response.data["orgId"] == "123"

    await client.close()


@pytest.mark.asyncio
async def test_delete_organization_invalid_id():
    # Mock response for invalid ID
    mock_invalid_id ={
        "status": 400, 
        "message": "Invalid organization ID", 
        "data": {}
    }

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'delete', AsyncMock(return_value=mock_invalid_id)):
        response = await client.organization.deleteOrganization("123")   

    # Assertions for a bad request response
    assert response is not None
    assert response.status == 400
    assert response.message == "Invalid organization ID"

    await client.close()


@pytest.mark.asyncio
async def test_delete_organization_not_found():
    # Mock response for not found
    mock_organization_not_found ={
        "status": 404, 
        "message": "Organization not found", 
        "data": {}
    }

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'delete', AsyncMock(return_value=mock_organization_not_found)):
        response = await client.organization.deleteOrganization("123")  

    # Assertions for not found response
    assert response is not None
    assert response.status == 404
    assert response.message == "Organization not found"

    await client.close()


