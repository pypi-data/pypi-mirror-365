from .base import BaseClient
from .user import UserClient
from .site import SiteClient
from .device import DeviceClient
from .ssid import SSIDClient
from .organization import OrganizationClient
from .auth import Authenticator
from .authentication import AuthenticationClient

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
