# === api_client/site_client.py ===

import logging
from typing import Optional, Any, List

from models.site import Site, SiteResponse
from utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)

class SiteClient:

    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client

    async def createSite(self, orgId: str, site: Site) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites"
        rawResponse = await self.base.post(endpoint, site)
        if rawResponse:
            return safe_model_validate(SiteResponse[Site], rawResponse)
        return rawResponse

    async def getOrganizationSites(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(SiteResponse[List[Site]], rawResponse)
        return rawResponse

    async def getOrganizationSitesBuildingsFloors(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/buildings/floors"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(SiteResponse[List[Site]], rawResponse)
        return rawResponse

    async def getSite(self, orgId: str, siteId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(SiteResponse[Site], rawResponse)
        return rawResponse

    async def updateSite(self, orgId: str, siteId: str, site: Site) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}"
        rawResponse = await self.base.put(endpoint, site.model_dump(mode="json"))
        if rawResponse:
            return safe_model_validate(SiteResponse[Site], rawResponse)
        return rawResponse

    async def deleteSite(self, orgId: str, siteId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}"
        rawResponse = await self.base.delete(endpoint)
        if rawResponse:
            try:
                return SiteResponse[Any].model_validate(rawResponse)
            except:
                return None
        return rawResponse


