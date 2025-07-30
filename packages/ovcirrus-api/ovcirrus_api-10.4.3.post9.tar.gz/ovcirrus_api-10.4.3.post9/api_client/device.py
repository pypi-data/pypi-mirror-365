# === api_client/device_client.py ===

import logging
from typing import Optional, List, Any

from models.device import Device, DeviceData, SaveToRunningResponse, RebootResponse, DeviceResponse
from utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)


class DeviceClient:

    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client

    async def createDevice(self, orgId: str, siteId: str, device: Device) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}/devices"
        rawResponse = await self.base.post(endpoint, device)
        if rawResponse:
            return safe_model_validate(DeviceResponse[Device], rawResponse)
        return rawResponse

    async def getAllDevices(self, orgId: str, siteId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}/devices"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(DeviceResponse[List[Device]], rawResponse)
        return rawResponse

    async def getAllDevicesFromOrganization(self, orgId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/devices"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(DeviceResponse[List[Device]], rawResponse)
        return rawResponse

    async def getDevice(self, orgId: str, deviceId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/devices/{deviceId}"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(DeviceResponse[DeviceData], rawResponse)
        return rawResponse

    async def getDeviceDetails(self, orgId: str, deviceId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/devices/{deviceId}/details"
        rawResponse = await self.base.get(endpoint)
        if rawResponse:
            return safe_model_validate(DeviceResponse[Device], rawResponse)
        return rawResponse

    async def updateDevice(self, orgId: str, siteId: str, deviceId: str, device: Device) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}/devices/{deviceId}"
        rawResponse = await self.base.put(endpoint, device.model_dump(mode="json"))
        if rawResponse:
            return safe_model_validate(DeviceResponse[Device], rawResponse)
        return rawResponse

    async def deleteDevice(self, orgId: str, siteId: str, deviceId: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}/devices/{deviceId}"
        rawResponse = await self.base.delete(endpoint)
        if rawResponse:
            try:
                return DeviceResponse[Any].model_validate(rawResponse)
            except:
                return None
        return rawResponse

    async def createRemoteAP(self, orgId: str, siteId: str, device: Device) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}/remote-aps"
        rawResponse = await self.base.post(endpoint, device)
        if rawResponse:
            return safe_model_validate(DeviceResponse[Device], rawResponse)
        return rawResponse

    async def updateRemoteAP(self, orgId: str, siteId: str, deviceId: str, device: Device) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/{siteId}/remote-aps/{deviceId}"
        rawResponse = await self.base.put(endpoint, device.model_dump(mode="json"))
        if rawResponse:
            return safe_model_validate(DeviceResponse[Device], rawResponse)
        return rawResponse

    async def saveToRunning(self, orgId: str, devicesIds: List[str], macAddresses: List[str]) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/devices/savetorunning"
        postData = {
            "devicesIds": devicesIds,
            "data": macAddresses
        }
        rawResponse = await self.base.post(endpoint, postData)
        if rawResponse:
            return safe_model_validate(DeviceResponse[SaveToRunningResponse], rawResponse)
        return rawResponse

    async def reboot(self, orgId: str, macAddresses: List[str], workMode: str) -> Optional[Any]:
        endpoint = f"api/ov/v1/organizations/{orgId}/sites/devices/reboot"
        postData = {
            "macAddresses": macAddresses,
            "workMode": workMode
        }
        rawResponse = await self.base.post(endpoint, postData)
        if rawResponse:
            return safe_model_validate(DeviceResponse[RebootResponse], rawResponse)
        return rawResponse
