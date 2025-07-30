import pytest
from unittest.mock import AsyncMock, patch

from typing import Optional, Any

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.user import UserResponse, UserProfile  # adjust module path
from utilities.model_validator import safe_model_validate  # adjust as needed

class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"
    def force_relogin(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_get_user_profile_success():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "status": 200,
        "message": "success",
        "data": {
            "email": "user@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "id": "12345"
        }
    }

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.user.getUserProfile()

    assert isinstance(result, UserResponse)
    assert result.status == 200
    assert isinstance(result.data, UserProfile)
    assert result.data.email == "user@example.com"
    assert result.data.firstname == "John"
    assert result.data.lastname == "Doe"
    assert result.data.id == "12345"


@pytest.mark.asyncio
async def test_get_user_profile_unauthorized():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "errorCode": 401,
        "errorMsg": "Unauthorized",
        "errorDetailsCode": "invalid_token",
        "errorDetails": "The access token provided is expired, revoked, malformed, or invalid for other reasons."
    }

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.user.getUserProfile()

    assert isinstance(result, UserResponse)
    assert result.errorCode == 401
    assert result.errorMsg == "Unauthorized"
    assert result.errorDetailsCode == "invalid_token"
    assert result.errorDetails == "The access token provided is expired, revoked, malformed, or invalid for other reasons."


@pytest.mark.asyncio
async def test_get_user_profile_server_error():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "errorCode": 500,
        "errorMsg": "Server Error",
        "errorDetails": {}
    }

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.user.getUserProfile()

    assert isinstance(result, UserResponse)
    assert result.errorCode == 500
    assert result.errorMsg == "Server Error"
    assert result.errorDetails == {}


@pytest.mark.asyncio
async def test_get_user_profile_invalid_format():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = "not a valid dict"
    client.get = AsyncMock(return_value=mock_response)

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.user.getUserProfile()

    assert result is None


@pytest.mark.asyncio
async def test_get_user_profile_missing_fields():
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "status": 200,
        "message": "success",
        "data": {}  # Missing required fields in UserProfile
    }

    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_response)):
        result = await client.user.getUserProfile()

    assert isinstance(result, UserResponse)
    assert result.status == 200
    assert isinstance(result.data, UserProfile)
    assert result.data.firstname == None
