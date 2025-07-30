import pytest
import httpx
from httpx import Request, Response
from unittest.mock import AsyncMock, patch
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.user import UserResponse, UserProfile
from api_client.auth import Authenticator

class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"
    def force_relogin(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_update_user_profile_success():
    user_profile = UserProfile(firstname="John Doe", email="john@example.com")
    mock_response = {
        "status": 200,
        "message": "Success",
        "data": user_profile.model_dump()
    }

    async def mock_send(request: Request) -> Response:
        return Response(status_code=200, json=mock_response)

    transport = httpx.MockTransport(mock_send)
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    client.client = httpx.AsyncClient(transport=transport)

    with patch.object(BaseClient, 'put', AsyncMock(return_value=mock_response)):
        result = await client.user.updateUserProfile(user_profile)

    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.status == 200
    assert isinstance(result.data, UserProfile)
    assert result.data.firstname == "John Doe"

    await client.close()

@pytest.mark.asyncio
async def test_update_user_profile_invalid_data():
    user_profile = UserProfile(firstname="Invalid", email="bad@example.com")

    mock_response_data = {
        "status": 400,
        "message": "Bad Request",
        "errors": [ 
                {

                    "type": "any.required",
                    "field": "Lastname",
                    "errorMsg": "Lastname is required"

                }
        ]
    }

    async def mock_send(request: Request) -> Response:
        return Response(status_code=400, json=mock_response_data)

    transport = httpx.MockTransport(mock_send)
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    client.client = httpx.AsyncClient(transport=transport)

    with patch.object(BaseClient, 'put', AsyncMock(return_value=mock_response_data)):
        result = await client.user.updateUserProfile(user_profile)

    assert isinstance(result, UserResponse)
    assert result.status == 400
    assert result.message == "Bad Request"
    assert result.errors[0].errorMsg == "Lastname is required"

    await client.close()

@pytest.mark.asyncio
async def test_update_user_profile_no_response():
    user_profile = UserProfile(firstname="Nobody", email="null@example.com")

    async def mock_send(request: Request) -> Response:
        return Response(status_code=204)

    transport = httpx.MockTransport(mock_send)
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    client.client = httpx.AsyncClient(transport=transport)

    with patch.object(BaseClient, 'put', AsyncMock(return_value=None)):
        result = await client.user.updateUserProfile(user_profile)

    assert result is None

    await client.close()

@pytest.mark.asyncio
async def test_update_user_profile_retry_on_401():
    user_profile = UserProfile(firstname="Retry Guy", email="retry@example.com")

    responses = [401, 200]
    call_count = 0

    async def mock_send(request: Request) -> Response:
        nonlocal call_count
        status_code = responses[call_count]
        call_count += 1

        if status_code == 401:
            return Response(status_code=401, json={"message": "Unauthorized"})
        return Response(status_code=200, json={
            "status": 200,
            "message": "Success",
            "data": user_profile.model_dump()
        })

    transport = httpx.MockTransport(mock_send)
    mock_httpx_client = httpx.AsyncClient(transport=transport)

    # ✅ Create client and inject mock transport correctly
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # 🔥 The magic line — inject into BaseClient inside UserApi
    client.user.base.client = mock_httpx_client
    # 🔁 Run actual retry test
    result = await client.user.updateUserProfile(user_profile)

    assert result is not None
    assert result.status == 200
    assert result.data.firstname == "Retry Guy"
    assert call_count == 2  # ✅ retried once after 401

    await client.close()




@pytest.mark.asyncio
async def test_update_user_profile_invalid_header():
    user_profile = UserProfile(firstname="Retry Guy", email="retry@example.com")

    # Simulated error response
    mock_response = {
        "errorCode": 406,
        "errorMsg": "The 'Content-Type' header is missing or invalid. You should use 'Content-Type: application/json'.",
        "errorDetailsCode": "invalid_header"
    }

    client = OVCirrusApiClient(base_url="http://mock.api", auth=DummyAuthenticator())

    # Patch the actual call to base.put
    client.user.base.put = AsyncMock(return_value=mock_response)

    result = await client.user.updateUserProfile(user_profile)

    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.errorCode == 406
    assert result.errorMsg.startswith("The 'Content-Type' header is missing")
    assert result.errorDetailsCode == "invalid_header"

    await client.close()
