import asyncio
import time
import logging

logger = logging.getLogger(__name__)

CACHE_TTL = 3600  # 1 hour


class EnumCache:
    def __init__(self):
        self._cities: list[str] = []
        self._cities_ts: float = 0
        self._exp: list[str] = []
        self._exp_ts: float = 0
        self._work_types: list[str] = []
        self._work_types_ts: float = 0
        self._categories: list[str] = []
        self._categories_ts: float = 0
        self._levels: list[str] = []
        self._levels_ts: float = 0
        self._refresh_task: asyncio.Task | None = None

    # ── Sync properties for Pydantic validators ──────────────────

    @property
    def cities(self) -> list[str]:
        """Sync access to cached cities. Safe for Pydantic validators."""
        return self._cities

    @property
    def exp_buckets(self) -> list[str]:
        """Sync access to cached experience buckets."""
        return self._exp

    @property
    def work_types(self) -> list[str]:
        """Sync access to cached work types."""
        return self._work_types

    @property
    def categories(self) -> list[str]:
        """Sync access to cached categories."""
        return self._categories

    @property
    def levels(self) -> list[str]:
        """Sync access to cached levels."""
        return self._levels

    # ── Async fetch methods ──────────────────────────────────────

    async def get_valid_cities(self) -> list[str]:
        now = time.time()
        if not self._cities or (now - self._cities_ts > CACHE_TTL):
            from data_clients import es_client
            try:
                self._cities = await es_client.get_distinct_cities()
                self._cities_ts = now
            except Exception as e:
                logger.warning(f"Failed to fetch cities from ES: {e}")
        return self._cities

    async def get_valid_exp_buckets(self) -> list[str]:
        now = time.time()
        if not self._exp or (now - self._exp_ts > CACHE_TTL):
            from data_clients import es_client
            try:
                self._exp = await es_client.get_distinct_exp_buckets()
                self._exp_ts = now
            except Exception as e:
                logger.warning(f"Failed to fetch exp buckets from ES: {e}")
        return self._exp

    async def get_valid_work_types(self) -> list[str]:
        now = time.time()
        if not self._work_types or (now - self._work_types_ts > CACHE_TTL):
            from data_clients import es_client
            try:
                self._work_types = await es_client.get_distinct_work_types()
                self._work_types_ts = now
            except Exception as e:
                logger.warning(f"Failed to fetch work types from ES: {e}")
        return self._work_types

    async def get_valid_categories(self) -> list[str]:
        now = time.time()
        if not self._categories or (now - self._categories_ts > CACHE_TTL):
            from data_clients import es_client
            try:
                self._categories = await es_client.get_distinct_categories()
                self._categories_ts = now
            except Exception as e:
                logger.warning(f"Failed to fetch categories from ES: {e}")
        return self._categories

    async def get_valid_levels(self) -> list[str]:
        now = time.time()
        if not self._levels or (now - self._levels_ts > CACHE_TTL):
            from data_clients import es_client
            try:
                self._levels = await es_client.get_distinct_levels()
                self._levels_ts = now
            except Exception as e:
                logger.warning(f"Failed to fetch levels from ES: {e}")
        return self._levels

    # ── Background refresh ───────────────────────────────────────

    async def _refresh_loop(self):
        """Periodically refresh all enum caches from ES."""
        while True:
            await asyncio.sleep(CACHE_TTL)
            logger.info("EnumCache: refreshing from ES")
            try:
                await self.get_valid_cities()
                await self.get_valid_exp_buckets()
                await self.get_valid_work_types()
                await self.get_valid_categories()
                await self.get_valid_levels()
            except Exception as e:
                logger.warning(f"EnumCache refresh failed: {e}")

    def start_refresh_task(self):
        """Start the background refresh loop. Call once during lifespan."""
        if self._refresh_task is None:
            self._refresh_task = asyncio.create_task(self._refresh_loop())
            logger.info("EnumCache: background refresh task started")

    def stop_refresh_task(self):
        """Cancel the background refresh loop."""
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            self._refresh_task = None


enum_cache = EnumCache()
