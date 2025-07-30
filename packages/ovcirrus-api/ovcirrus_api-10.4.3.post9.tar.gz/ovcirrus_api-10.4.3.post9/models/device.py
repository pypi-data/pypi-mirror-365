from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Generic, Union, List  # Make sure to import the correct types
from datetime import datetime

T = TypeVar("T")

class DeviceLabel(BaseModel):
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    color: Optional[str] = None
    organization: Optional[str] = None


class Location(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[Union[str, float]]] = None


class Site(BaseModel):
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    countryCode: Optional[str] = None
    timezone: Optional[str] = None
    address: Optional[str] = None
    location: Optional[Location] = None
    imageUrl: Optional[str] = None
    isDefault: Optional[bool] = None
    zoom: Optional[int] = None
    organization: Optional[str] = None


class Group(BaseModel):
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    provisioningTemplateName: Optional[str] = None
    isExtendScale: Optional[bool] = None
    site: Optional[str] = None


class FloorPlanImageCoordinates(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[List[float]]] = None


class AreaGeometry(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[List[List[float]]]] = None


class Floor(BaseModel):
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    floorNumber: Optional[int] = None
    floorPlanUrl: Optional[str] = None
    floorPlanImageCoordinates: Optional[FloorPlanImageCoordinates] = None
    relativeAltitude: Optional[float] = None
    areaGeometry: Optional[AreaGeometry] = None
    area: Optional[int] = None
    areaUnit: Optional[str] = None
    building: Optional[str] = None
    site: Optional[str] = None
    organization: Optional[str] = None


class Building(BaseModel):
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    site: Optional[str] = None
    organization: Optional[str] = None


class License(BaseModel):
    maxCount: Optional[int] = None
    currentCount: Optional[int] = None
    productId: Optional[str] = None
    expiredDate: Optional[str] = None
    gracePeriod: Optional[int] = None
    available: Optional[int] = None
    percentUsed: Optional[str] = None


class UpgradeSchedule(BaseModel):
    id: Optional[int] = None
    scheduleName: Optional[str] = None
    cronExpression: Optional[str] = None
    startDate: Optional[int] = None
    endDate: Optional[int] = None
    timeZone: Optional[str] = None
    duration: Optional[int] = None
    state: Optional[str] = None
    nextTriggerTime: Optional[int] = None
    prevTriggerTime: Optional[int] = None
    maxScope: Optional[str] = None
    orgId: Optional[str] = None


class Device(BaseModel):
    deviceLabels: Optional[List[DeviceLabel]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    ipAddress: Optional[str] = None
    ipAddressV6: Optional[str] = None
    friendlyName: Optional[str] = None
    macAddress: Optional[str] = None
    serialNumber: Optional[str] = None
    deviceFamily: Optional[str] = None
    type: Optional[str] = ""
    physicalLocation: Optional[str] = ""
    description: Optional[str] = ""
    systemContact: Optional[str] = None
    location: Optional[Location] = None
    floorElevation: Optional[Union[int,T]] = 0
    deviceStatus: Optional[str] = None
    currentSwVer: Optional[str] = None
    workingMode: Optional[str] = None
    lastSeenTime: Optional[int] = None
    imageLocation: Optional[str] = ""
    licenseStatus: Optional[str] = None
    autoChoosingLicenseMode: Optional[str] = None
    markPremium: Optional[bool] = None
    managementMode: Optional[str] = None
    isRap: Optional[bool] = None
    vpnSettingName: Optional[str] = None
    isAutoRegistered: Optional[bool] = None
    vcSerialNumber: Optional[str] = ""
    calculatedMacAddress: Optional[str] = None
    organization: Optional[str] = None
    site: Optional[Site] = None
    group: Optional[Group] = None
    building: Optional[Building] = None
    floor: Optional[Floor] = None
    license: Optional[License] = None
    lastEventReceivedAt: Optional[int] = None
    wiredPortLinkStatus: Optional[str] = ""
    vpnServers: Optional[List] = []
    iotStatus: Optional[str] = None
    ipMode: Optional[str] = None
    meshEnable: Optional[bool] = None
    meshRole: Optional[str] = ""
    meshIsRoot: Optional[bool] = None
    meshBand: Optional[str] = ""
    meshEssid: Optional[str] = ""
    meshPassphrase: Optional[str] = None
    ipv4Netmask: Optional[str] = None
    ipv4Gateway: Optional[str] = None
    ipv4DeviceDNS: Optional[str] = None
    ipv6Prefixlen: Optional[str] = ""
    ipv6Gateway: Optional[str] = None
    ipv6DeviceDNS: Optional[str] = None
    ledMode: Optional[str] = None
    lacpStatus: Optional[str] = None
    switchForQoeRtls: Optional[Union[str,T]] = None
    qoeSwitch: Optional[Union[str,T]] = None
    rtlsSwitch: Optional[Union[str,T]] = None
    flashThreshold: Optional[int] = None
    memoryThreshold: Optional[int] = None
    cpuThreshold: Optional[int] = None
    bleMac: Optional[str] = None
    iotPrivateSwitch: Optional[bool] = False
    iotMode: Optional[str] = None
    advertisingSwitch: Optional[bool] = False
    frequency: Optional[Union[str,T]] = None
    txPower: Optional[Union[str,T]] = None
    txChannel: Optional[List[int]] = []
    beaconMode: Optional[str] = None
    plainUrl: Optional[str] = ""
    nameSpace: Optional[str] = None
    instanceId: Optional[str] = None
    scanningSwitch: Optional[bool] = False
    scanningInterval: Optional[Union[str,T]] = None
    ouiWhiteList: Optional[List[str]] = []
    deviceCountryCode: Optional[str] = None
    apRadioConfigSwitch: Optional[Union[str,T]] = None
    band2: Optional[Union[str,T]] = None
    band5A: Optional[Union[str,T]] = None
    band5H: Optional[Union[str,T]] = None
    band5L: Optional[Union[str,T]] = None
    band6: Optional[Union[str,T]] = None
    _modifiedTS: Optional[datetime] = None
    callHomeInterval: Optional[int] = None
    chassisInfo: Optional[Union[str, T]] = None
    currentRunningDirectory: Optional[str] = None
    dataVpnServerIP: Optional[str] = None
    deviceFeatures: Optional[str] = None
    deviceLicenseMode: Optional[str] = ""
    deviceNaasMode: Optional[str] = None
    devicePrivateKey: Optional[str] = None
    devicePublicKey: Optional[str] = None
    deviceRole: Optional[str] = None
    deviceVpnIP: Optional[str] = None
    endIpAddress: Optional[str] = None
    ipAddressPoolOption: Optional[str] = None
    lengthIpAddress: Optional[str] = None
    manageRapVpnServer: Optional[str] = None
    manageRapVpnServerPort: Optional[int] = 0
    manageRapVpnServerPrivateKey: Optional[str] = None
    manageRapVpnServerPublicKey: Optional[str] = None
    networkIpAddress: Optional[str] = None
    ovEnterpriseServerIP: Optional[str] = None
    partNumber: Optional[str] = None
    pkiUpdateStatus: Optional[str] = None
    pkiUpdateTimestamp: Optional[str] = None
    rap: Optional[bool] = None
    startIpAddress: Optional[str] = None
    subnetMask: Optional[str] = None
    tcpMss: Optional[int] = None
    vcMacAddress: Optional[str] = ""
    upTime: Optional[int] = None
    bridgeApWebPassword: Optional[str] = None
    bridgeApWebSwitch: Optional[bool] = None
    bridgeDefault: Optional[str] = None
    bridgeFarEndApIp: Optional[str] = None
    bridgeFarEndApMac: Optional[str] = None
    bridgeSshPassword: Optional[str] = None
    bridgeSshSwitch: Optional[bool] = None
    bridgeWebCertName: Optional[str] = None
    lastRegisterEpochSecondTime: Optional[int] = None
    meshMode: Optional[str] = None
    meshParentNode: Optional[str] = ""
    channel: Optional[int] = None
    linkStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    registrationStatusReason: Optional[str] = None
    version: Optional[str] = None
    changes: Optional[str] = None
    apName: Optional[str] = None
    encryptionType: Optional[str] = None
    meshMcastRate: Optional[int] = None
    _insertedTS: Optional[datetime] = None
    activationStatus: Optional[str] = None
    currentRunningSoftwareVersion: Optional[str] = None
    lldpSwitch: Optional[bool] = None
    lastHeartBeat: Optional[int] = None
    modelName: Optional[str] = None
    licenseCategory: Optional[str] = None
    deviceLocation: Optional[str] = None
    workMode: Optional[str] = None
    managementConnectivity: Optional[str] = None
    numberOfLicensesUsed: Optional[int] = None
    rfProfile: Optional[str] = None
    upgradeSchedule: Optional[UpgradeSchedule] = None
    desiredSwVersion: Optional[str] = None
    scheduleLevel: Optional[str] = None
    rootMacFriendlyName: Optional[str] = None


class DeviceData(BaseModel):
    deviceLabels: Optional[List[DeviceLabel]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    name: Optional[str] = None
    ipAddress: Optional[str] = None
    ipAddressV6: Optional[str] = None
    friendlyName: Optional[str] = None
    macAddress: Optional[str] = None
    serialNumber: Optional[str] = None
    deviceFamily: Optional[str] = None
    type: Optional[str] = ""
    physicalLocation: Optional[str] = ""
    description: Optional[str] = ""
    systemContact: Optional[str] = None
    location: Optional[Union[str,T]] = None
    floorElevation: Optional[Union[str,T]] = 0
    deviceStatus: Optional[str] = None
    currentSwVer: Optional[str] = None
    workingMode: Optional[str] = None
    lastSeenTime: Optional[int] = None
    imageLocation: Optional[str] = ""
    licenseStatus: Optional[str] = None
    autoChoosingLicenseMode: Optional[str] = None
    markPremium: Optional[bool] = None
    managementMode: Optional[str] = None
    isRap: Optional[bool] = False
    vpnSettingName: Optional[str] = None
    isAutoRegistered: Optional[bool] = False
    vcSerialNumber: Optional[str] = ""
    calculatedMacAddress: Optional[str] = None
    organization: Optional[str] = None
    site: Optional[str] = None
    group: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    license: Optional[License] = None
    iotStatus: Optional[str] = None
    ipMode: Optional[str] = None
    meshEnable: Optional[bool] = False
    meshRole: Optional[str] = ""
    meshIsRoot: Optional[bool] = False
    meshBand: Optional[str] = ""
    meshEssid: Optional[str] = ""
    meshPassphrase: Optional[str] = None
    ipv4Netmask: Optional[str] = None
    ipv4Gateway: Optional[str] = None
    ipv4DeviceDNS: Optional[str] = None
    ipv6Prefixlen: Optional[str] = ""
    ipv6Gateway: Optional[str] = None
    ipv6DeviceDNS: Optional[str] = None
    ledMode: Optional[str] = None
    lacpStatus: Optional[str] = None
    # switchForQoeRtls: Optional[str] = None
    # qoeSwitch: Optional[str] = None
    # rtlsSwitch: Optional[str] = None
    # flashThreshold: Optional[str] = None
    memoryThreshold: Optional[str] = None
    cpuThreshold: Optional[str] = None
    bleMac: Optional[str] = None
    iotPrivateSwitch: Optional[bool] = False
    iotMode: Optional[str] = None
    advertisingSwitch: Optional[bool] = False
    frequency: Optional[int] = None
    txPower: Optional[int] = None
    txChannel: Optional[List[int]] = None
    beaconMode: Optional[str] = None
    plainUrl: Optional[str] = ""
    nameSpace: Optional[str] = None
    instanceId: Optional[str] = None
    scanningSwitch: Optional[bool] = False
    scanningInterval: Optional[int] = None
    ouiWhiteList: Optional[List[str]] = None
    deviceCountryCode: Optional[str] = None
    apRadioConfigSwitch: Optional[str] = None
    band2: Optional[str] = None
    band5A: Optional[str] = None
    band5H: Optional[str] = None
    band5L: Optional[str] = None
    band6: Optional[str] = None
    _modifiedTS: Optional[datetime] = None
    callHomeInterval: Optional[int] = None
    chassisInfo: Optional[str] = None
    currentRunningDirectory: Optional[str] = None
    dataVpnServerIP: Optional[str] = None
    deviceFeatures: Optional[str] = None
    deviceLicenseMode: Optional[str] = ""
    deviceNaasMode: Optional[str] = None
    devicePrivateKey: Optional[str] = None
    devicePublicKey: Optional[str] = None
    deviceRole: Optional[str] = None
    deviceVpnIP: Optional[str] = None
    endIpAddress: Optional[str] = None
    ipAddressPoolOption: Optional[str] = None
    lengthIpAddress: Optional[str] = None
    manageRapVpnServer: Optional[str] = None
    manageRapVpnServerPort: Optional[int] = 0
    manageRapVpnServerPrivateKey: Optional[str] = None
    manageRapVpnServerPublicKey: Optional[str] = None
    networkIpAddress: Optional[str] = None
    ovEnterpriseServerIP: Optional[str] = None
    partNumber: Optional[str] = None
    pkiUpdateStatus: Optional[str] = None
    pkiUpdateTimestamp: Optional[str] = None
    rap: Optional[bool] = False
    startIpAddress: Optional[str] = None
    subnetMask: Optional[str] = None
    tcpMss: Optional[str] = None
    vcMacAddress: Optional[str] = ""
    upTime: Optional[int] = None
    bridgeApWebPassword: Optional[str] = None
    bridgeApWebSwitch: Optional[str] = None
    bridgeDefault: Optional[str] = None
    bridgeFarEndApIp: Optional[str] = None
    bridgeFarEndApMac: Optional[str] = None
    bridgeSshPassword: Optional[str] = None
    bridgeSshSwitch: Optional[str] = None
    bridgeWebCertName: Optional[str] = None
    lastRegisterEpochSecondTime: Optional[int] = None
    meshMode: Optional[str] = None
    meshParentNode: Optional[str] = ""
    channel: Optional[int] = None
    linkStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    registrationStatusReason: Optional[str] = None
    version: Optional[str] = None
    changes: Optional[str] = None
    apName: Optional[str] = None
    encryptionType: Optional[str] = None
    meshMcastRate: Optional[str] = None
    _insertedTS: Optional[datetime] = None
    activationStatus: Optional[str] = None
    currentRunningSoftwareVersion: Optional[str] = None
    lldpSwitch: Optional[bool] = None
    lastHeartBeat: Optional[int] = None
    modelName: Optional[str] = None
    licenseCategory: Optional[str] = None
    deviceLocation: Optional[str] = None
    workMode: Optional[str] = None
    lastEventReceivedAt: Optional[int] = None
    managementConnectivity: Optional[str] = None
    provisioningTemplate: Optional[str] = None
    valueMappingTemplate: Optional[str] = None
    mgmtUsersTemplate: Optional[str] = None
    saveAndCertify: Optional[bool] = None
    provisioningResultState: Optional[str] = None
    rfProfile: Optional[str] = None
    upgradeSchedule: Optional[UpgradeSchedule] = None
    desiredSwVersion: Optional[str] = None
    scheduleLevel: Optional[str] = None
    rootMacFriendlyName: Optional[str] = None
   
class SaveToRunningResponse(BaseModel):
    devicesIds: Optional[List[str]] = []
    macAddresses: Optional[List[str]] = []

class RebootResponse(BaseModel):
    macAddresses: Optional[List[str]] = []  


class Error(BaseModel):
    type: Optional[str] = None
    field: Optional[str] = None
    errorMsg: Optional[str] = None 


class DeviceResponse(BaseModel, Generic[T]):  # Inherit directly from BaseModel
    status: Optional[int] = None
    message: Optional[str] = None
    data: Optional[T] = None
    errorCode: Optional[int] = None
    errorMsg: Optional[str] = None
    errorDetailsCode: Optional[str] = None
    errorDetails: Optional[Union[str, dict]] = None  # Accept both str and dict
    errors: Optional[List[Error]] = None      
