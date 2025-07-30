import pytest
import httpx
from typing import Optional
from datetime import datetime
from httpx import HTTPStatusError, Request, Response
from unittest.mock import AsyncMock, patch

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.organization import OrganizationResponse, Organization
from datetime import datetime, timezone
from utilities.model_validator import safe_model_validate  # adjust as needed

# Dummy Authenticator that always returns a token
class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"

    def force_relogin(self) -> bool:
        return True

# Mock response data for organization settings
mock_org_settings_data = {
    "status": 200,
    "message": "Success",
    "data": {
        "id": "123",
        "name": "ALE",
        "createdAt": "2022-08-04T12:10:38.058Z",
        "updatedAt": "2022-09-08T15:56:53.407Z",
        "enforceStrongPassword": True,
        "enforceStrongPasswordNotifyType": "SHOW_MESSAGE_AFTER_LOGIN",
        "timezone": "Europe/Tirane",
        "auditHour": 130,
        "idleTimeout": 3600
    }
}

# Mock invalid response (e.g., 400 Bad Request)
mock_invalid_response = {
    "status": 400,
    "message": "Bad Request",
    "data": None
}

# Mock no response (None)
mock_no_response = None

@pytest.mark.asyncio
async def test_get_organization_basic_settings():
    # Define the organization ID
    org_id = "123"

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Run the method
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_org_settings_data)):
        response = await client.organization.getOrganizationBasicSettings(org_id)

    # Assertions for valid response
    assert response is not None
    assert response.status == 200
    assert response.data.id == org_id
    assert response.data.name == "ALE"
    assert response.data.enforceStrongPassword is True
    assert response.data.timezone == "Europe/Tirane"
    assert response.data.auditHour == 130
    assert response.data.idleTimeout == 3600

    # Close the client after the test
    await client.close()


@pytest.mark.asyncio
async def test_get_organization_invalid_status():
    # Define the organization ID
    org_id = "123"

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Run the method
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_invalid_response)):
        response = await client.organization.getOrganizationBasicSettings(org_id)

    # Assertions for invalid response
    assert response is not None
    assert response.status == 400
    assert response.message == "Bad Request"
    assert response.data is None

    # Close the client after the test
    await client.close()


@pytest.mark.asyncio
async def test_get_organization_no_response():
    # Define the organization ID
    org_id = "123"

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Run the method
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_no_response)):
        response = await client.organization.getOrganizationBasicSettings(org_id)

    # Assertions for no response
    assert response is None

    # Close the client after the test
    await client.close()
