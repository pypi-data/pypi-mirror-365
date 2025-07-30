from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Type
from ovcirrus_api.models.wlananalytics import WirelessClientSummary, WirelessAnalyticsResponse

from ovcirrus_api.api_client.base import BaseClient
from ovcirrus_api.api_client.user import UserClient
from ovcirrus_api.api_client.site import SiteClient
from ovcirrus_api.api_client.device import DeviceClient
from ovcirrus_api.api_client.ssid import SSIDClient
from ovcirrus_api.api_client.organization import OrganizationClient
from ovcirrus_api.api_client.auth import Authenticator
from ovcirrus_api.api_client.authentication import AuthenticationClient
from ovcirrus_api.api_client.wlananalytics import WlanAnalyticsClient

class OVCirrusApiClient:
    def __init__(self, base_url: str, auth: Authenticator):
        self.base_client = BaseClient(base_url, auth)

        # Attach modular clients, reusing the base methods
        self.user = UserClient(self.base_client)
        self.organization = OrganizationClient(self.base_client)
        self.site = SiteClient(self.base_client)
        self.device = DeviceClient(self.base_client)
        self.ssid = SSIDClient(self.base_client)
        self.authentication = AuthenticationClient(self.base_client)
        self.wlananalytics = WlanAnalyticsClient(self.base_client)

    async def getClientStatus(self, orgId: str, search: str) -> Optional[WirelessClientSummary]:
            """Find a client's MAC address and return their wireless session summary."""
            staMac = None

            # 1. Try live sessions
            online = await self.authentication.getAuthRecords(orgId, limit=1000, offset=0, sort=[])
            if online and online.data and online.data.list:
                for r in online.data.list:
                    if search.lower() in (r.username or "").lower() or \
                    search.lower() in (r.deviceMac or "").lower() or \
                    search in (getattr(r, 'deviceIpv4', '') or ''):
                        staMac = r.deviceMac
                        break

            # 2. Try history
            if not staMac:
                history = await self.authentication.getAuthHistoryRecords(
                    orgId, limit=1, offset=0, search=search, sort=[{"sessionStart": "DESC"}]
                )
                if history and history.data and history.data.list:
                    staMac = history.data.list[0].deviceMac

            if not staMac:
                return None

            # 3. Get summary from wlananalytics
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            summary = await self.wlananalytics.getClientWlanSummary(
                orgId, startDate=week_ago.isoformat(), endDate=now.isoformat(), staMac=staMac
            )
            return summary.data if summary else None        

    async def close(self):
        await self.base_client.close()
