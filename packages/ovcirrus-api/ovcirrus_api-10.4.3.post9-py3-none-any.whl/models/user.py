from pydantic import BaseModel, Field, Extra,ConfigDict
from typing import Optional, TypeVar, Generic, Union, List  # Make sure to import the correct types
from datetime import datetime

T = TypeVar("T")

class UserProfile(BaseModel):
    failedTry: Optional[int] = 0
    lockedUntilDate: Optional[int] = 0
    lastLoginDate: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    id: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    verified: Optional[bool] = None
    preferredLanguage: Optional[str] = None
    country: Optional[str] = None
    closestRegion: Optional[str] = None
    companyName: Optional[str] = None
    avatarLocation: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    zipCode: Optional[str] = None
    phoneNumber: Optional[str] = None
    isTwoFAEnabled: Optional[bool] = None
    faMethod: Optional[str] = None
    tempSecret: Optional[str] = None
    secret: Optional[str] = None
    enforcementPolicy: Optional[str] = None
    accessLevelRole: Optional[str] = None
    # msp: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

class Error(BaseModel):
    type: Optional[str] = None
    field: Optional[str] = None
    errorMsg: Optional[str] = None 


class UserResponse(BaseModel, Generic[T]):  # Inherit directly from BaseModel
    status: Optional[int] = None
    message: Optional[str] = None
    data: Optional[T] = None
    errorCode: Optional[int] = None
    errorMsg: Optional[str] = None
    errorDetailsCode: Optional[str] = None
    errorDetails: Optional[Union[str, dict]] = None  # Accept both str and dict
    errors: Optional[List[Error]] = None
