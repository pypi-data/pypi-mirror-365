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
            "message": "Success",
            "data": [
                {
                    "id": "site-123",
                    "name": "Test Site",
                    "countryCode": "US",
                    "timezone": "America/New_York",
                    "address": "123 Main Street",
                    "location": {
                        "type": "Point",
                        "coordinates": ["-73.935242", "40.730610"]
                    },
                    "isDefault": False,
                    "zoom": 12,
                    "organization": "org-abc123"
                }
            ]
        }



    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_success_response)):
        response = await client.site.getOrganizationSites("123")      


    # Assertions for a successful response
    assert response is not None
    assert isinstance(response, SiteResponse)
    assert isinstance(response.data, list)
    assert isinstance(response.data[0], Site)
    assert response.data[0].name == "Test Site"

    await client.close()

@pytest.mark.asyncio
async def test_create_site_invalid_data(caplog):

    # Mock successful response
    mock_invalid_data = {
            "status": 200,
            "message": "Success",
            "data": [
                {
                    "id": "site-123",
                    "name": 123,
                    "countryCode": "US",
                    "timezone": "America/New_York",
                    "address": "123 Main Street",
                    "location": {
                        "type": "Point",
                        "coordinates": ["-73.935242", "40.730610"]
                    },
                    "isDefault": False,
                    "zoom": 12,
                    "organization": "org-abc123"
                }
            ]
        }



    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())

    # Call the method
    with patch.object(BaseClient, 'get', AsyncMock(return_value=mock_invalid_data)):
        response = await client.site.getOrganizationSites("123")      


    # Assertions for a successful response
    assert response is None
    assert "Validation failed for" in caplog.text
    await client.close()

