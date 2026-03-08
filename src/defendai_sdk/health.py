"""Connection health check: GET wawsdb base URL with optional caching and retry."""

import logging
import time
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from defendai_sdk.client import WawsdbClient

logger = logging.getLogger(__name__)


def is_reachable(
    wawsdb_url: str,
    api_key: str,
    *,
    timeout: float = 3.0,
    trust_env: bool = False,
) -> bool:
    """Sync: return True if Wawsdb base URL responds (GET /). Any response counts as reachable."""
    url = wawsdb_url.rstrip("/") + "/"
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        with httpx.Client(timeout=timeout, trust_env=trust_env) as client:
            client.get(url, headers=headers)
        return True
    except Exception as e:
        logger.debug("Wawsdb reachability check failed: %s", e)
        return False


async def is_reachable_async(
    wawsdb_url: str,
    api_key: str,
    *,
    timeout: float = 3.0,
    trust_env: bool = False,
) -> bool:
    """Async: return True if Wawsdb base URL responds (GET /)."""
    url = wawsdb_url.rstrip("/") + "/"
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as client:
            await client.get(url, headers=headers)
        return True
    except Exception as e:
        logger.debug("Wawsdb reachability check failed: %s", e)
        return False


class ReachabilityCache:
    """Cached reachability check: re-use result for a given duration before re-probing."""

    def __init__(
        self,
        client: "WawsdbClient",
        *,
        cache_sec: float = 30.0,
        timeout: float = 3.0,
    ):
        self._client = client
        self._cache_sec = cache_sec
        self._timeout = timeout
        self._reachable: bool = True
        self._last_check: float = 0.0

    async def is_reachable(self) -> bool:
        """Return True if Wawsdb is reachable; use cached result for cache_sec."""
        now = time.monotonic()
        if self._last_check > 0 and (now - self._last_check) < self._cache_sec:
            return self._reachable
        try:
            url = self._client.wawsdb_url + "/"
            async with httpx.AsyncClient(
                timeout=self._timeout, trust_env=False
            ) as http_client:
                await http_client.get(url, headers=self._client.auth_headers())
        except Exception as e:
            logger.debug("Wawsdb reachability check failed: %s", e)
            self._reachable = False
            self._last_check = now
            return False
        self._reachable = True
        self._last_check = now
        return True
