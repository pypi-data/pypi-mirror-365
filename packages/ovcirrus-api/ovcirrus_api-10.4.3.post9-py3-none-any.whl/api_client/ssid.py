    # === api_client/ssid_client.py ===

import logging
from typing import Optional, List, Any

from models.ssid import SSIDData, SSIDResponse
from utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)

class SSIDClient:

    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client

    async def getAllSsids(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/wlan/ssids"
        rawResponse = await self.base.get(endpoint)
        if rawResponse: 
            return safe_model_validate(SSIDResponse[List[SSIDData]], rawResponse)
        return rawResponse

    async def createSSID(self, orgId: str, ssidData: SSIDData) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/wlan/ssids"
        rawResponse = await self.base.post(endpoint, ssidData)
        if rawResponse:
            return safe_model_validate(SSIDResponse, rawResponse)
        return rawResponse

    async def updateSSID(self, orgId: str, ssidData: SSIDData) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/wlan/ssids"
        rawResponse = await self.base.put(endpoint, ssidData)
        if rawResponse:
            return safe_model_validate(SSIDResponse, rawResponse)
        return rawResponse        
