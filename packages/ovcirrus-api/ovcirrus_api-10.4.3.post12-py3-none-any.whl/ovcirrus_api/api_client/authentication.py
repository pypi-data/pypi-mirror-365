# === api_client/authentication.py ===
import json
import logging
from typing import Optional, Dict, List, Any, Type
from datetime import datetime
import httpx
import backoff
from ovcirrus_api.api_client.auth import Authenticator
from ovcirrus_api.models.authentication import AuthDetailData, AuthData, AuthResponse, AuthHistoryDetail

from ovcirrus_api.utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def format_query_params(
    limit: int,
    offset: int,
    startDate: Optional[Any] = None,
    endDate: Optional[Any] = None,
    sort: Optional[List[Dict[str, str]]] = None,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "limit": limit,
        "offset": offset,
        "startDate": startDate,
        "endDate": endDate,
        "sort": json.dumps(sort or []),
        "filters": json.dumps(filters or {}),
        "search": search or ""
    }

class AuthenticationClient:
    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client
        
    async def getAuthRecords(
        self,
        orgId: str,
        limit: int = 1,
        offset: int = 0,
        startDate: Optional[datetime] = None,
        endDate: Optional[datetime] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None
    ) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/am/access-records/authentication-online-records"
        query_params = format_query_params(limit, offset, startDate, endDate, sort, filters, search)

        # Send the request
        rawResponse = await self.base.get(endpoint, params=query_params)
        if rawResponse:
            return safe_model_validate(AuthResponse[AuthData], rawResponse)
        return None
    
    async def getAuthHistoryRecords(
        self,
        orgId: str,
        limit: int = 1,
        offset: int = 0,
        startDate: Optional[datetime] = None,
        endDate: Optional[datetime] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None
    ) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/am/access-records/authentication-history-records"
        query_params = format_query_params(limit, offset, startDate, endDate, sort, filters, search)

        # Send the request
        rawResponse = await self.base.get(endpoint, params=query_params)
        if rawResponse:
            return safe_model_validate(AuthResponse[AuthData], rawResponse)
        return None    
    
    async def getAuthHistoryRecordDetail(
        self,
        orgId: str,
        recordId: str,
    ) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/am/access-records/authentication-history-records/{recordId}"

        # Send the request
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(AuthResponse[AuthHistoryDetail], rawResponse)
        return None   

    async def getOnlineAuthRecord(
        self,
        orgId: str,
        mac: str,
    ) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/am/access-records/authentication-online-records/{mac}"

        # Send the request
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(AuthResponse[AuthDetailData], rawResponse)
        return None       

    async def getStatus(
        self,
        orgId: str,
        search: str  # user, IP, or MAC
    ) -> Optional[str]:
        """
        Determines if a device or user is currently connected.
        If not, returns last seen from history.
        """
        # === 1. Fetch all online records (no search filter supported) ===
        all_online = await self.getAuthRecords(
            orgId=orgId,
            limit=1000,
            offset=0,
            sort=[],
        )

        # === 2. Search manually ===
        if all_online and all_online.data and all_online.data.list:
            for record in all_online.data.list:
                if search.lower() in (record.username or "").lower() \
                   or search.lower() in (record.deviceMac or "").lower() \
                   or search in (getattr(record, 'deviceIpv4', '') or ''):
                    start_time = datetime.fromtimestamp(record.sessionStart / 1000).isoformat() if record.sessionStart else "N/A"
                    return (
                        f"✅ Device/user is currently connected:\n"
                        f"- Username: {record.username}\n"
                        f"- Device MAC: {record.deviceMac}\n"
                        f"- IP: {getattr(record, 'deviceIpv4', 'N/A')}\n"
                        f"- Connected to: {record.nasIpAddress}\n"
                        f"- Associated to SSID: {record.ssid}\n"
                        f"- Session start: {start_time}"
                    )

        # === 3. Search history if not found online ===
        history = await self.getAuthHistoryRecords(
            orgId=orgId,
            limit=1,
            offset=0,
            search=search,
            sort=[{"sessionStart": "DESC"}]
        )

        if history and history.data and history.data.list:
            record = history.data.list[0]
            last_seen_ts = record.sessionStop or record.sessionStart
            last_seen = datetime.fromtimestamp(last_seen_ts / 1000).isoformat() if last_seen_ts else "N/A"
            return (
                f"⚠️ Device/user is not currently connected.\n"
                f"- Username: {record.username}\n"
                f"- Last seen: {last_seen}\n"
                f"- MAC: {record.deviceMac}\n"
                f"- Connected to: {record.nasIpAddress}\n"
                f"- Associated to SSID: {record.ssid}"
            )

        return "❌ No authentication records found for this device or user."

    


