from pydantic import BaseModel, Field, Extra,ConfigDict
from typing import Optional, TypeVar, Generic, Union, List, Dict  # Make sure to import the correct types
from datetime import datetime

T = TypeVar("T")

class AuthRecord(BaseModel):
    id: Optional[str] = None
    deviceMac: Optional[str] = None
    deviceType: Optional[str] = None
    username: Optional[str] = None
    authResult: Optional[str] = None
    rejectReason: Optional[str] = None
    sessionStart: Optional[int] = None
    sessionStop: Optional[int] = None
    sessionTime: Optional[str] = None
    terminateReason: Optional[str] = None
    sessionId: Optional[str] = None
    multiSessionId: Optional[str] = None
    authType: Optional[str] = None
    authMethod: Optional[str] = None
    authResource: Optional[str] = None
    networkType: Optional[str] = None
    nasIpAddress: Optional[str] = None
    nasSourceIp: Optional[str] = None
    nasDeviceMac: Optional[str] = None
    ssid: Optional[str] = None
    accessPolicy: Optional[str] = None
    webAccessPolicy: Optional[str] = None
    finalAccessRoleProfile: Optional[str] = None

class AuthData(BaseModel):
    total: Optional[int] = None
    list: Optional[List[AuthRecord]] = None

class AuthHistoryDetail(BaseModel):
    id: Optional[str] = None
    deviceMac: Optional[str] = None
    deviceType: Optional[str] = None
    username: Optional[str] = None
    authResult: Optional[str] = None
    rejectReason: Optional[str] = None
    sessionStart: Optional[int] = None
    sessionStop: Optional[int] = None
    sessionTime: Optional[str] = None
    terminateReason: Optional[str] = None
    sessionId: Optional[str] = None
    multiSessionId: Optional[str] = None
    authType: Optional[str] = None
    authMethod: Optional[str] = None
    authResource: Optional[str] = None
    networkType: Optional[str] = None
    nasIpAddress: Optional[str] = None
    nasSourceIp: Optional[str] = None
    nasDeviceMac: Optional[str] = None
    ssid: Optional[str] = None
    accessPolicy: Optional[str] = None
    webAccessPolicy: Optional[str] = None
    finalAccessRoleProfile: Optional[str] = None
    serviceType: Optional[str] = None
    accessDeviceSsid: Optional[str] = None
    portDesc: Optional[str] = None
    nasIdentifier: Optional[str] = None
    nasPortId: Optional[str] = None
    nasPortType: Optional[str] = None
    nasPort: Optional[str] = None
    framedMtu: Optional[str] = None
    alcatelDeviceMac: Optional[str] = None
    alcatelDeviceName: Optional[str] = None
    calledStationId: Optional[str] = None
    authenticationMethod: Optional[str] = None
    alcatelDeviceLocation: Optional[str] = None
    alcatelAPGroup: Optional[str] = None
    slotPort: Optional[str] = None
    roamingInformation: Optional[str] = None
    alcatelRedirectUrl: Optional[str] = None
    alcatelRedirectIpb6Url: Optional[str] = None
    sessionTimeout: Optional[str] = None
    terminationAction: Optional[str] = None
    policyList: Optional[str] = None
    filterId: Optional[str] = None
    acctInterimInterval: Optional[str] = None
    wisprBandwidthMaxUp: Optional[str] = None
    wisprBandwidthMaxDown: Optional[str] = None
    acctStatusType: Optional[str] = None
    tunnelPrivateGroupID: Optional[str] = None
    acctAuthentic: Optional[str] = None
    framedIPAddress: Optional[str] = None
    framedIPV6Address: Optional[str] = None
    finalfilterId: Optional[str] = None
    acctSessionId: Optional[str] = None
    acctInputPackets: Optional[str] = None
    acctOutputPackets: Optional[str] = None
    acctInputOctets: Optional[str] = None
    acctOutputOctets: Optional[str] = None
    acctInputGigawords: Optional[str] = None
    acctOutputGigawords: Optional[str] = None
    acctTerminateCause: Optional[str] = None
    acctMultiSessionId: Optional[str] = None    


class BasicAuthInfo(BaseModel):
    id: Optional[str] = None
    deviceMac: Optional[str] = None
    deviceType: Optional[str] = None
    username: Optional[str] = None
    authResult: Optional[str] = None
    rejectReason: Optional[str] = None
    sessionStart: Optional[int] = None
    sessionUpdate: Optional[int] = None
    sessionStop: Optional[int] = None
    sessionTime: Optional[str] = None
    terminateReason: Optional[str] = None
    sessionId: Optional[str] = None
    multiSessionId: Optional[str] = None
    authType: Optional[str] = None
    authMethod: Optional[str] = None
    authResource: Optional[str] = None
    networkType: Optional[str] = None
    nasIpAddress: Optional[str] = None
    nasSourceIp: Optional[str] = None
    nasDeviceMac: Optional[str] = None
    ssid: Optional[str] = None
    accessPolicy: Optional[str] = None
    webAccessPolicy: Optional[str] = None
    finalAccessRoleProfile: Optional[str] = None
    finalDynamicVlanId: Optional[str] = None
    deviceIpv4: Optional[str] = None
    deviceIpv6: Optional[str] = None


class AccessRequest(BaseModel):
    serviceType: Optional[str] = None
    accessDeviceSsid: Optional[str] = None
    portDesc: Optional[str] = None
    nasIpAddress: Optional[str] = None
    nasIdentifier: Optional[str] = None
    nasPortId: Optional[str] = None
    nasPortType: Optional[str] = None
    nasPort: Optional[str] = None
    framedMtu: Optional[str] = None
    username: Optional[str] = None
    alcatelDeviceMac: Optional[str] = None
    alcatelDeviceName: Optional[str] = None
    calledStationId: Optional[str] = None
    authenticationMethod: Optional[str] = None
    alcatelDeviceLocation: Optional[str] = None
    alcatelAPGroup: Optional[str] = None
    slotPort: Optional[str] = None
    rejectReason: Optional[str] = None
    roamingInformation: Optional[str] = None


class AccessAccept(BaseModel):
    alcatelRedirectUrl: Optional[str] = None
    alcatelRedirectIpv6Url: Optional[str] = None
    sessionTimeout: Optional[str] = None
    terminationAction: Optional[str] = None
    policyList: Optional[str] = None
    filterId: Optional[str] = None
    acctInterimInterval: Optional[str] = None
    wisprBandwidthMaxUp: Optional[str] = None
    wisprBandwidthMaxDown: Optional[str] = None
    tunnelPrivateGroupId: Optional[str] = None


class Accounting(BaseModel):
    acctStatusType: Optional[str] = None
    finalTunnelPrivateGroupId: Optional[str] = None
    acctAuthentic: Optional[str] = None
    framedIPAddress: Optional[str] = None
    framedIPV6Address: Optional[str] = None
    finalFilterId: Optional[str] = None
    acctSessionId: Optional[str] = None
    acctMultiSessionId: Optional[str] = None
    acctInputPackets: Optional[int] = None
    acctOutputPackets: Optional[int] = None
    acctInputOctets: Optional[int] = None
    acctOutputOctets: Optional[int] = None
    acctInputGigawords: Optional[int] = None
    acctOutputGigawords: Optional[int] = None
    acctTerminateCause: Optional[str] = None


class Packet(BaseModel):
    id: Optional[str] = None
    deviceMac: Optional[str] = None
    callingStationId: Optional[str] = None
    acctSessionId: Optional[str] = None
    acctMultiSessionId: Optional[str] = None
    packetType: Optional[str] = None
    packetTime: Optional[int] = None
    packetDetail: Optional[str] = None


class AuthDetailData(BaseModel):
    lastPacketTime: Optional[int] = None
    coaFlag: Optional[bool] = None
    roamingFlag: Optional[bool] = None
    dmFlag: Optional[bool] = None
    basicAuthInfo: Optional[BasicAuthInfo] = None
    accessRequest: Optional[AccessRequest] = None
    accessAccept: Optional[AccessAccept] = None
    coaRequest: Optional[Dict] = None
    accounting: Optional[Accounting] = None
    packets: Optional[List[Packet]] = None    

class Error(BaseModel):
    type: Optional[str] = None
    field: Optional[str] = None
    errorMsg: Optional[str] = None 

class AuthResponse(BaseModel, Generic[T]):  # Inherit directly from BaseModel
    status: Optional[int] = None
    message: Optional[str] = None
    data: Optional[T] = None
    errorCode: Optional[int] = None
    errorMsg: Optional[str] = None
    errorDetailsCode: Optional[str] = None
    errorDetails: Optional[Union[str, dict]] = None  # Accept both str and dict
    errors: Optional[List[Error]] = None
