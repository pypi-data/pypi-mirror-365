# === api_client/auth.py ===

import requests
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Authenticator:
    def __init__(self):
        self.auth_url: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.app_id: Optional[str] = None
        self.app_secret: Optional[str] = None
        self.token: Optional[str] = None
        self.expires_in: Optional[int] = None
        self.token_expiry: Optional[datetime] = None
        self.isAuthenticated: bool = False

    def setURL(self, auth_url: str):
        self.auth_url = auth_url
        return self

    def setCredentials(self, email: str, password: str):
        self.email = email
        self.password = password
        return self  

    def setApp(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        return self

    def build(self):
        if not all([self.auth_url, self.email, self.password, self.app_id, self.app_secret]):
            raise ValueError("Missing authentication configuration.")
        success = self.login()
        if not success:
            raise ValueError("Authentication failed.")
        return self

    def login(self) -> bool:
        logger.info("Authenticating with API...")

        try:
            response = requests.post(self.auth_url, json={
                "email": self.email,
                "password": self.password,
                "appId": self.app_id,
                "appSecret": self.app_secret
            })

            if response.status_code != 200:
                logger.error(f"Auth failed with status {response.status_code}: {response.reason}")
                logger.error(f"Response body: {response.text}")
                self.isAuthenticated = False
                return False

            data = response.json()
            token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # default to 1 hour

            if not token:
                logger.error("No access_token returned in authentication response.")
                self.isAuthenticated = False
                return False

            self.token = token
            self.expires_in = expires_in
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            self.isAuthenticated = True

            logger.info("Token acquired successfully. Expires in %s seconds.", expires_in)
            return True

        except requests.RequestException as e:
            logger.exception("Exception during authentication:")
            self.isAuthenticated = False
            return False

    def is_token_expired(self) -> bool:
        if not self.token_expiry:
            return True
        # Refresh 5 minutes before expiry
        return datetime.utcnow() >= self.token_expiry - timedelta(minutes=5)

    def get_token(self) -> Optional[str]:
        if not self.token or self.is_token_expired():
            logger.info("Token missing or expired. Re-authenticating...")
            self.login()
        return self.token

    def force_relogin(self) -> bool:
        logger.info("Forcing re-login...")
        return self.login()
