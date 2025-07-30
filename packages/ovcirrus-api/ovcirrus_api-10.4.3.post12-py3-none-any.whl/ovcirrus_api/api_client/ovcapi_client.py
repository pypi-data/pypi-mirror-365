from ovcirrus_api.api_client.base import BaseClient
from ovcirrus_api.api_client.user import UserClient
from ovcirrus_api.api_client.site import SiteClient
from ovcirrus_api.api_client.device import DeviceClient
from ovcirrus_api.api_client.ssid import SSIDClient
from ovcirrus_api.api_client.organization import OrganizationClient
from ovcirrus_api.api_client.auth import Authenticator
from ovcirrus_api.api_client.authentication import AuthenticationClient

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


    async def close(self):
        await self.base_client.close()
