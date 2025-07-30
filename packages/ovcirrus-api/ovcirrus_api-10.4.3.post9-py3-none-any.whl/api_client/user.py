# === api_client/user.py ===

import logging
from typing import Optional, Dict, List, Any, Type

import httpx
import backoff
from .auth import Authenticator
from models.user import UserProfile, UserResponse

from utilities.model_validator import safe_model_validate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === api_client/user_client.py ===

class UserClient:
    def __init__(self, base_client: 'BaseClient'):
        self.base = base_client

    async def getUserProfile(self) -> Optional[Any]:
        endpoint = "api/ov/v1/user/profile"
        rawResponse = await self.base.get(endpoint)  # Access base.get() here
        return safe_model_validate(UserResponse[UserProfile], rawResponse)

    async def updateUserProfile(self, userProfile: UserProfile) -> Optional[Any]:
        endpoint = "api/ov/v1/user/profile"
        rawResponse = await self.base.put(endpoint, userProfile.model_dump(mode="json"))
        if rawResponse:
            return safe_model_validate(UserResponse[UserProfile], rawResponse)
        return rawResponse

