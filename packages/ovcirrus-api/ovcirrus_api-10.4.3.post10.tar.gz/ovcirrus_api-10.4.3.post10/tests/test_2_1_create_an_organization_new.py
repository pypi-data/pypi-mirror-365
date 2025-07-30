import pytest
from unittest.mock import AsyncMock, patch

# Import your actual classes and functions
from api_client.auth import Authenticator
from api_client.base import BaseClient
from api_client.ovcapi_client import OVCirrusApiClient
from models.organization import OrganizationResponse, Organization
from datetime import datetime, timezone

class DummyAuthenticator(Authenticator):
    def get_token(self) -> str:
        return "dummy-token"
    def force_relogin(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_create_an_organization_success():
    # Create an example organization instance
    org = Organization(
        id="62d65f2506af3feef8fec051",
        name="ALE",
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is2FARequired=False,
        imageUrl="",
        countryCode="FR",
        timezone="Europe/Tirane",
        auditHour=130,
        idleTimeout=3600,
        msp="60c8bce3eb5b4155f8b82214",
        upamAuthRecords=30,
        events=30,
        alerts=30,
        wifiRtls=30,
        networkAnalytics=30,
        clientSessions=30,
        clientAnalytics=30,
        auditLogs=7,
        loginAttemps=7,
        iotData=7,
        backupPerDevice=30,
        collectInfo=7,
        configurationBackup=5,
        qoe=30,
        enforceStrongPassword=True,
        enforceStrongPasswordNotifyType="SHOW_MESSAGE_AFTER_LOGIN"
    )

    # Mocked API response (as a dict)
    fake_response = {
        "status": 200,
        "message": "The organization has been successfully fetched.",
        "data": org.model_dump()
    }

    # Create the client and mock `post`
    client = OVCirrusApiClient(base_url="http://mock.api", auth=AsyncMock())

    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=fake_response)):
        response = await client.organization.createOrganization(org)    

    # Assertions
    assert response is not None
    assert isinstance(response, OrganizationResponse)
    assert response.status == 200
    assert response.data.name == "ALE"
    assert response.data.enforceStrongPassword is True

@pytest.mark.asyncio
async def test_create_an_organization_unauthorized():
    # Create an example organization instance
    org = Organization(
        id="62d65f2506af3feef8fec051",
        name="ALE",
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is2FARequired=False,
        imageUrl="",
        countryCode="FR",
        timezone="Europe/Tirane",
        auditHour=130,
        idleTimeout=3600,
        msp="60c8bce3eb5b4155f8b82214",
        upamAuthRecords=30,
        events=30,
        alerts=30,
        wifiRtls=30,
        networkAnalytics=30,
        clientSessions=30,
        clientAnalytics=30,
        auditLogs=7,
        loginAttemps=7,
        iotData=7,
        backupPerDevice=30,
        collectInfo=7,
        configurationBackup=5,
        qoe=30,
        enforceStrongPassword=True,
        enforceStrongPasswordNotifyType="SHOW_MESSAGE_AFTER_LOGIN"
    )    
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "errorCode": 401,
        "errorMsg": "Unauthorized",
        "errorDetailsCode": "invalid_token",
        "errorDetails": "The access token provided is expired, revoked, malformed, or invalid for other reasons."
    }

    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=mock_response)):
        result = await client.organization.createOrganization(org)    

    assert isinstance(result, OrganizationResponse)
    assert result.errorCode == 401
    assert result.errorMsg == "Unauthorized"
    assert result.errorDetailsCode == "invalid_token"
    assert result.errorDetails == "The access token provided is expired, revoked, malformed, or invalid for other reasons."        

@pytest.mark.asyncio
async def test_create_an_organization_invalid_header():
    # Create an example organization instance
    org = Organization(
        id="62d65f2506af3feef8fec051",
        name="ALE",
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is2FARequired=False,
        imageUrl="",
        countryCode="FR",
        timezone="Europe/Tirane",
        auditHour=130,
        idleTimeout=3600,
        msp="60c8bce3eb5b4155f8b82214",
        upamAuthRecords=30,
        events=30,
        alerts=30,
        wifiRtls=30,
        networkAnalytics=30,
        clientSessions=30,
        clientAnalytics=30,
        auditLogs=7,
        loginAttemps=7,
        iotData=7,
        backupPerDevice=30,
        collectInfo=7,
        configurationBackup=5,
        qoe=30,
        enforceStrongPassword=True,
        enforceStrongPasswordNotifyType="SHOW_MESSAGE_AFTER_LOGIN"
    )

    mock_response = {
        "errorCode": 406,
        "errorMsg": "The 'Content-Type' header is missing or invalid. You should use 'Content-Type: application/json'.",
        "errorDetailsCode": "invalid_header"
    }
    
    client = OVCirrusApiClient(base_url="http://mock.api", auth=AsyncMock())


    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=mock_response)):
        result = await client.organization.createOrganization(org)    

    assert result is not None
    assert isinstance(result, OrganizationResponse)
    assert result.errorCode == 406
    assert result.errorMsg == "The 'Content-Type' header is missing or invalid. You should use 'Content-Type: application/json'."
    assert result.errorDetailsCode == "invalid_header"


@pytest.mark.asyncio
async def test_create_an_organization_server_error():
    # Create an example organization instance
    org = Organization(
        id="62d65f2506af3feef8fec051",
        name="ALE",
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is2FARequired=False,
        imageUrl="",
        countryCode="FR",
        timezone="Europe/Tirane",
        auditHour=130,
        idleTimeout=3600,
        msp="60c8bce3eb5b4155f8b82214",
        upamAuthRecords=30,
        events=30,
        alerts=30,
        wifiRtls=30,
        networkAnalytics=30,
        clientSessions=30,
        clientAnalytics=30,
        auditLogs=7,
        loginAttemps=7,
        iotData=7,
        backupPerDevice=30,
        collectInfo=7,
        configurationBackup=5,
        qoe=30,
        enforceStrongPassword=True,
        enforceStrongPasswordNotifyType="SHOW_MESSAGE_AFTER_LOGIN"
    )
    client = OVCirrusApiClient(base_url="https://api.example.com", auth=DummyAuthenticator())
    mock_response = {
        "errorCode": 500,
        "errorMsg": "Server Error",
        "errorDetails": {}
    }
    # Call the method
    with patch.object(BaseClient, 'post', AsyncMock(return_value=mock_response)):
        result = await client.organization.createOrganization(org)    

    assert isinstance(result, OrganizationResponse)
    assert result.errorCode == 500
    assert result.errorMsg == "Server Error"
    assert result.errorDetails == {}  



