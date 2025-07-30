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


class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"
    def force_relogin(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_get_all_user_organizations_success():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "status": 200,
        "message": "Fetched organizations",
        "data": [
            {
                "id": "123",
                "name": "Org One",
                "timezone": "Europe/Paris"
            },
            {
                "id": "456",
                "name": "Org Two",
                "timezone": "Asia/Tokyo"
            }
        ]
    }
    client.get = AsyncMock(return_value=mock_response)

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.organization.getAllUserOrganizations()

    assert result is not None
    assert result.status == 200
    assert len(result.data) == 2
    assert result.data[0].name == "Org One"

@pytest.mark.asyncio
async def test_get_all_user_organizations_no_response():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    with patch.object(BaseClient, 'get', AsyncMock(return_value=None)):
        result = await client.organization.getAllUserOrganizations()
    assert result is None

@pytest.mark.asyncio
async def test_get_all_user_organizations_invalid_structure():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "status": 200,
        "message": "Invalid",
        "data": [
            {
                "id": "123",
                "name": 123,  # Invalid type
                "timezone": True  # Invalid type
            }
        ]
    }

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.organization.getAllUserOrganizations()

    assert result is None
