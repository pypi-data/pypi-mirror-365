# === api_client/organization_client.py ===

import logging
from typing import Optional, List, Any

from models.organization import Organization, OrganizationResponse
from utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)

class OrganizationClient:

    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client

    async def createOrganization(self, organization: Organization) -> Optional[Any]:
        endpoint = "api/ov/v1/organizations"
        rawResponse = await self.base.post(endpoint, organization)
        if rawResponse:
            return safe_model_validate(OrganizationResponse[Organization], rawResponse)
        return rawResponse

    async def getAllUserOrganizations(self) -> Optional[Any]:
        endpoint = "api/ov/v1/organizations"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(OrganizationResponse[List[Organization]], rawResponse)
        return rawResponse

    async def getOrganization(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(OrganizationResponse[Organization], rawResponse)
        return rawResponse

    async def updateOrganization(self, orgId: str, organization: Organization) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}"
        rawResponse = await self.base.put(endpoint, organization.model_dump(mode="json"))
        if rawResponse:
            return safe_model_validate(OrganizationResponse[Organization], rawResponse)
        return rawResponse

    async def deleteOrganization(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}"
        rawResponse = await self.base.delete(endpoint)
        if rawResponse:
            try:
                return OrganizationResponse[Any].model_validate(rawResponse)
            except:
                return None
        return rawResponse

    async def getOrganizationBasicSettings(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/settings/basic"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(OrganizationResponse[Organization], rawResponse)
        return rawResponse
