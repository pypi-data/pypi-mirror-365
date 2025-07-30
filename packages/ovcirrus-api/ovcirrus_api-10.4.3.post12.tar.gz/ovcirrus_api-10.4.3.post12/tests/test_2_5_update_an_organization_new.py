import pytest
from unittest.mock import AsyncMock, patch

from typing import Optional, Any

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.organization import OrganizationResponse, Organization
from utilities.model_validator import safe_model_validate  # adjust as needed

# Dummy authenticator for tests
class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"
    def force_relogin(self) -> bool:
        return False

# Sample payload for a valid organization
valid_org = Organization(
    id="123",
    name="ALE",
    enforceStrongPassword=True,
    enforceStrongPasswordNotifyType="SHOW_MESSAGE_AFTER_LOGIN",
    timezone="Europe/Tirane",
    auditHour=130,
    idleTimeout=3600
)

# Mock successful response
mock_success_response = {
    "status": 200,
    "message": "Updated successfully",
    "data": {
        "id": "123",
        "name": "ALE",
        "enforceStrongPassword": True,
        "enforceStrongPasswordNotifyType": "SHOW_MESSAGE_AFTER_LOGIN",
        "timezone": "Europe/Tirane",
        "auditHour": 130,
        "idleTimeout": 3600
    }
}

# Mock error response
mock_error_response = {
    "status": 400,
    "message": "Invalid data",
    "data": {}
}

# Mock malformed response
mock_error_response_404 = {
    "errorCode": 404,
    "errorMsg": "Resource Not Found",
    "errorResourceName": "Firstname",
    "errorPropertyName": "<Firstname>",
    "errorDetails": "No resource found with <Firstname>: <Firstname>"
}

@pytest.mark.asyncio
async def test_update_organization_success():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'put', AsyncMock(return_value=mock_success_response)):
        response = await client.organization.updateOrganization("123",valid_org)  

    assert response is not None
    assert response.status == 200
    assert response.data.id == "123"
    assert response.data.name == "ALE"

    await client.close()

@pytest.mark.asyncio
async def test_update_organization_invalid_data():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'put', AsyncMock(return_value=mock_error_response)):
        response = await client.organization.updateOrganization("123",valid_org)  


    assert response is not None
    assert response.status == 400
    assert response.message == "Invalid data"
    assert isinstance(response.data, Organization)

    await client.close()

@pytest.mark.asyncio
async def test_update_organization_no_response():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'put', AsyncMock(return_value=None)):
        response = await client.organization.updateOrganization("123",valid_org)  

    assert response is None
    await client.close()

@pytest.mark.asyncio
async def test_update_organization_404():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'put', AsyncMock(return_value=mock_error_response_404)):
        response = await client.organization.updateOrganization("123",valid_org)  

    assert response is not None
    assert response.errorCode == 404
    assert isinstance(response, OrganizationResponse)
    assert response.errorMsg == "Resource Not Found"
    assert response.errorDetails == "No resource found with <Firstname>: <Firstname>"

    await client.close()


