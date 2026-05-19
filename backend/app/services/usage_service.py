from app.services.storage_service import StorageService
from app.utils.logger import get_logger

logger = get_logger(__name__)

ESTIMATED_COST_PER_1K_TOKENS = 0.005  # placeholder for gpt-4o-mini pricing


class UsageService:
    def __init__(self):
        self.storage = StorageService()

    async def track_event(self, user_id: str, event_type: str, token_count: int = 0):
        estimated_cost = (token_count / 1000) * ESTIMATED_COST_PER_1K_TOKENS
        try:
            await self.storage.create_usage_event(user_id, event_type, token_count, estimated_cost)
            logger.info(f"Tracked usage event: {event_type} for user {user_id}")
        except Exception as e:
            logger.error(f"Usage tracking failed: {e}")
