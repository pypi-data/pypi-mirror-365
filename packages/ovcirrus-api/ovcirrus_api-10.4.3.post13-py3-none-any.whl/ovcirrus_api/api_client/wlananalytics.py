# === api_client/authentication.py ===
import json
import logging
from typing import Optional, Dict, List, Any, Type
from datetime import datetime
import httpx
import backoff
from datetime import datetime, timedelta
from ovcirrus_api.api_client.auth import Authenticator
from ovcirrus_api.models.wlananalytics import WirelessClientSummary, WirelessAnalyticsResponse

from ovcirrus_api.utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def format_query_params(
    startDate: Optional[Any] = None,
    endDate: Optional[Any] = None,
    staMac: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "startDate": startDate,
        "endDate": endDate,
        "staMac": staMac
    }

class WlanAnalyticsClient:
    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client
        
    async def getClientWlanSummary(
        self,
        orgId: str,
        startDate: Optional[str] = None,
        endDate: Optional[str] = None,
        staMac: Optional[str] = None,
    ) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/wlan-analytics/sessions/wireless/summary"
        query_params = format_query_params(startDate, endDate, staMac)
        # Send the request
        rawResponse = await self.base.get(endpoint, params=query_params)
        if rawResponse:
            return safe_model_validate(WirelessAnalyticsResponse[WirelessClientSummary], rawResponse)
        return None
    
    async def getClientStatus(
        self,
        orgId: str,
        search: str
    ) -> Optional[WirelessClientSummary]:
        """
        Fetch the WirelessClientSummary for a client matching the search term
        (username, MAC, or IP). If not currently online, fall back to historical.
        """
        try:
            staMac = None

            # 1. Search live sessions
            all_online = await self.base.authentication.getAuthRecords(
                orgId=orgId,
                limit=1000,
                offset=0,
                sort=[]
            )
            if all_online and all_online.data and all_online.data.list:
                for record in all_online.data.list:
                    if search.lower() in (record.username or "").lower() \
                    or search.lower() in (record.deviceMac or "").lower() \
                    or search in (getattr(record, 'deviceIpv4', '') or ''):
                        staMac = record.deviceMac
                        break

            # 2. If not found online, search history
            if not staMac:
                history = await self.getAuthHistoryRecords(
                    orgId=orgId,
                    limit=1,
                    offset=0,
                    search=search,
                    sort=[{"sessionStart": "DESC"}]
                )
                if history and history.data and history.data.list:
                    staMac = history.data.list[0].deviceMac

            if not staMac:
                return None  # Could not find a matching MAC

            # 3. Fetch summary using staMac
            endDate = datetime.utcnow()
            startDate = endDate - timedelta(days=7)
            summary = await self.getClientWlanSummary(
                orgId=orgId,
                startDate=startDate.isoformat(),
                endDate=endDate.isoformat(),
                staMac=staMac
            )
            return summary.data  # This should be a WirelessClientSummary object

        except Exception as e:
            logger.exception(f"Error in getClientStatus for search='{search}': {str(e)}")
            return None
            


