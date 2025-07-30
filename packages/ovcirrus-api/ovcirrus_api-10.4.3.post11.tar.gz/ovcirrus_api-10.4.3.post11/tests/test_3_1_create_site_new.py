import pytest
from unittest.mock import AsyncMock, patch

from typing import Optional, Any

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.site import SiteResponse, Site


# Dummy Authenticator that always returns a token
class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"

    def force_relogin(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_create_site_success():

    # Mock successful response
    mock_success_response = {
        "status": 200, 
        "message": "Site created successfully", 
        "data": {
            "name": "site ALE"
            }
    }

    siteData = Site(
            name="site ALE",
            countryCode="BE",
            timezone="Europe/Brussels",
            address="12, Treft, Strombeek-Bever, Belgium"
        )

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=mock_success_response)):
        response = await client.site.createSite("123",siteData)      


    # Assertions for a successful response
    assert response is not None
    assert response.status == 200
    assert response.message == "Site created successfully"
    assert response.data.name == "site ALE"

    await client.close()

@pytest.mark.asyncio
async def test_create_site_no_response():

    siteData = Site(
            name="site ALE",
            countryCode="BE",
            timezone="Europe/Brussels",
            address="12, Treft, Strombeek-Bever, Belgium"
        )

        

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=None)):
        response = await client.site.createSite("123",siteData)      


    # Assertions for a successful response
    assert response is None

    await client.close()    

@pytest.mark.asyncio
async def test_create_site_invalid_data(caplog):

    siteData = Site(
            name="123",
        )

    # Mock successful response
    mock_invalid_response = {
        "status": 200, 
        "message": "Site created successfully", 
        "data": {
            "name": 123
            }
    }        

    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=mock_invalid_response)):
        response = await client.site.createSite("123",siteData)      


    # Assertions for a successful response
    assert response is None
    assert "Validation failed for" in caplog.text
    await client.close()        

# @pytest.mark.asyncio
# class TestCreateSite:

#     @pytest.fixture
#     def valid_site(self):
#         return Site(
#             name="site ALE",
#             countryCode="BE",
#             timezone="Europe/Brussels",
#             address="12, Treft, Strombeek-Bever, Belgium"
#         )

#     @pytest.fixture
#     def valid_response(self, valid_site):
#         return {
#             "status": 200,
#             "message": "Site created successfully",
#             "data": valid_site.model_dump()
#         }

#     @pytest.fixture
#     def client(self):
#         client = OVCirrusApiClient(base_url="https://api.example.com", auth=AsyncMock())
#         client.post = AsyncMock()
#         return client

#     async def test_create_site_success(self, client, valid_site, valid_response):
#         client.post.return_value = valid_response
#         response = await client.createSite("123", valid_site)
#         assert isinstance(response, ApiResponse)
#         assert response.status == 200
#         assert response.data.name == "site ALE"

#     async def test_create_site_no_response(self, client, valid_site):
#         client.post.return_value = None
#         response = await client.createSite("123", valid_site)
#         assert response is None

#     async def test_create_site_invalid_data(self, client, valid_site):
#         client.post.return_value = {
#             "status": 200,
#             "message": "OK",
#             "data": {
#                 "name": 123  # Invalid type
#             }
#         }
#         response = await client.createSite("123", valid_site)
#         assert response is None

#     async def test_create_site_http_error(self, client, valid_site):
#         mock_response = Response(400, request=Request("POST", "https://api.example.com"))
#         client.post.side_effect = Exception("Bad request")
#         with pytest.raises(Exception):
#             await client.createSite("123", valid_site)

#     async def test_create_site_malformed_json(self, client, valid_site):
#         malformed_data = "{'status': 200, 'message': 'OK', 'data': {'name': 'Jane Doe'}}"  # Not a dict
#         with patch("utilities.model_validator.logger") as mock_logger:
#             result = safe_model_validate(ApiResponse[Site], malformed_data)

#             # safe_model_validate should return None on failure
#             assert result is None

#             # Ensure a warning was logged
#             assert mock_logger.warning.called
#             args, _ = mock_logger.warning.call_args
#             assert "Validation failed for ApiResponse[Site]" in args[0]
