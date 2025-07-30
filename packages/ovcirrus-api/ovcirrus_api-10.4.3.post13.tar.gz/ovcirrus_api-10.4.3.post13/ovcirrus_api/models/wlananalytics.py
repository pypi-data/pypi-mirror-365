from pydantic import BaseModel, Field, Extra,ConfigDict
from typing import Optional, TypeVar, Generic, Union, List, Dict  # Make sure to import the correct types
from datetime import datetime

T = TypeVar("T")

class WirelessClientSummary(BaseModel):
    avgRssi: Optional[int] = None
    deviceName: Optional[str] = None
    nbDistinctAps: Optional[int] = None
    nbRoamings: Optional[int] = None
    nbSessions: Optional[int] = None
    pmf: Optional[bool] = None
    staMac: Optional[str] = None
    totalRxBytes: Optional[int] = None
    totalSessionsDuration: Optional[int] = None
    totalTxBytes: Optional[int] = None


class Error(BaseModel):
    type: Optional[str] = None
    field: Optional[str] = None
    errorMsg: Optional[str] = None 

class WirelessAnalyticsResponse(BaseModel, Generic[T]):  # Inherit directly from BaseModel
    status: Optional[int] = None
    message: Optional[str] = None
    data: Optional[T] = None
    errorCode: Optional[int] = None
    errorMsg: Optional[str] = None
    errorDetailsCode: Optional[str] = None
    errorDetails: Optional[Union[str, dict]] = None  # Accept both str and dict
    errors: Optional[List[Error]] = None
