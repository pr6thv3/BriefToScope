from typing import Optional
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self):
        self.settings = get_settings()

    async def get_or_create_user(self, clerk_user_id: str, email: str, name: str = "") -> dict:
        from app.services.storage_service import StorageService
        storage = StorageService()
        existing = await storage.get_user_by_clerk_id(clerk_user_id)
        if existing:
            return existing
        user = await storage.create_user(clerk_user_id, email, name)
        logger.info(f"Created new user: {user.get('id')}")
        return user
