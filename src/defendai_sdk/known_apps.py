"""GET /scanner/config/known-apps: fetch known-apps list from Wawsdb."""

import logging
import time

import httpx

from defendai_sdk.client import WawsdbClient

logger = logging.getLogger(__name__)


def get_known_apps(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> list[str]:
    """Fetch known-apps list from Wawsdb GET /scanner/config/known-apps.

    Uses sync httpx. On failure returns [] (no cache in SDK).
    Returns lowercase strings only.
    """
    url = client.url("/scanner/config/known-apps")
    try:
        with httpx.Client(timeout=timeout, trust_env=trust_env) as http_client:
            resp = http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch known-apps from API: %s", e)
        return []

    if not isinstance(data, dict):
        return []
    raw = data.get("known_apps")
    if not isinstance(raw, list):
        return []
    return [str(x).lower() for x in raw if isinstance(x, str)]


async def get_known_apps_async(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> list[str]:
    """Async: fetch known-apps list from Wawsdb GET /scanner/config/known-apps."""
    url = client.url("/scanner/config/known-apps")
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as http_client:
            resp = await http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch known-apps from API: %s", e)
        return []

    if not isinstance(data, dict):
        return []
    raw = data.get("known_apps")
    if not isinstance(raw, list):
        return []
    return [str(x).lower() for x in raw if isinstance(x, str)]


class KnownAppsCache:
    """Cached known-apps list: re-use result for a given duration before re-fetching."""

    def __init__(
        self,
        client: WawsdbClient,
        *,
        cache_sec: float = 3600.0,
        timeout: float = 5.0,
    ):
        self._client = client
        self._cache_sec = cache_sec
        self._timeout = timeout
        self._cached: list[str] = []
        self._last_fetch: float = 0.0

    def get(self) -> list[str]:
        """Return known-apps list; use cached result for cache_sec. On error returns [] and logs warning."""
        now = time.monotonic()
        if self._last_fetch > 0 and (now - self._last_fetch) < self._cache_sec:
            return self._cached
        try:
            self._cached = get_known_apps(
                self._client, timeout=self._timeout, trust_env=False
            )
            self._last_fetch = now
            return self._cached
        except Exception as e:
            logger.warning("KnownAppsCache get failed: %s", e)
            return []

    async def get_async(self) -> list[str]:
        """Async: return known-apps list; use cached result for cache_sec. On error returns [] and logs warning."""
        now = time.monotonic()
        if self._last_fetch > 0 and (now - self._last_fetch) < self._cache_sec:
            return self._cached
        try:
            self._cached = await get_known_apps_async(
                self._client, timeout=self._timeout, trust_env=False
            )
            self._last_fetch = now
            return self._cached
        except Exception as e:
            logger.warning("KnownAppsCache get_async failed: %s", e)
            return []
