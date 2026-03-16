"""High-risk agent types and MCP publisher config from Wawsdb.

Wawsdb endpoints (implement in wawsdb):

  GET /scanner/config/high-risk-agents
    Auth: X-API-Key (same as /scanner/config/known-apps)
    Response: {"high_risk_agents": ["openclaw", "autogpt", "babyagi"]}
    No auth required for platform defaults (same pattern as known-apps)

  GET /scanner/config/mcp-publishers
    Auth: X-API-Key
    Response: {"publishers": {"@salesforce/mcp-server": {...}, ...}}
    Returns VERIFIED_MCP_PUBLISHERS merged with any tenant additions
"""

import logging
import time

import httpx

from defendai_sdk.client import WawsdbClient

logger = logging.getLogger(__name__)


def get_high_risk_agent_types(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> list[str]:
    """GET /scanner/config/high-risk-agents.

    Returns list of agent type slugs the platform considers high-risk.
    e.g. ["openclaw", "autogpt", "babyagi"]
    Returns [] on any error.
    """
    url = client.url("/scanner/config/high-risk-agents")
    try:
        with httpx.Client(timeout=timeout, trust_env=trust_env) as http_client:
            resp = http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch high-risk-agents from API: %s", e)
        return []

    if not isinstance(data, dict):
        return []
    raw = data.get("high_risk_agents")
    if not isinstance(raw, list):
        return []
    return [str(x).lower() for x in raw if isinstance(x, str)]


async def get_high_risk_agent_types_async(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> list[str]:
    """Async: GET /scanner/config/high-risk-agents. Returns [] on any error."""
    url = client.url("/scanner/config/high-risk-agents")
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as http_client:
            resp = await http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch high-risk-agents from API: %s", e)
        return []

    if not isinstance(data, dict):
        return []
    raw = data.get("high_risk_agents")
    if not isinstance(raw, list):
        return []
    return [str(x).lower() for x in raw if isinstance(x, str)]


def get_mcp_publishers(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> dict:
    """GET /scanner/config/mcp-publishers.

    Returns verified MCP publisher registry from platform.
    Returns {} on any error.
    """
    url = client.url("/scanner/config/mcp-publishers")
    try:
        with httpx.Client(timeout=timeout, trust_env=trust_env) as http_client:
            resp = http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch mcp-publishers from API: %s", e)
        return {}

    if not isinstance(data, dict):
        return {}
    raw = data.get("publishers")
    if not isinstance(raw, dict):
        return {}
    return raw


async def get_mcp_publishers_async(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> dict:
    """Async: GET /scanner/config/mcp-publishers. Returns {} on any error."""
    url = client.url("/scanner/config/mcp-publishers")
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as http_client:
            resp = await http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch mcp-publishers from API: %s", e)
        return {}

    if not isinstance(data, dict):
        return {}
    raw = data.get("publishers")
    if not isinstance(raw, dict):
        return {}
    return raw


class HighRiskAgentCache:
    """In-memory cache for high-risk agent types; 1-hour TTL, same pattern as KnownAppsCache."""

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
        """Return high-risk agent type slugs; use cached result for cache_sec. On error returns []."""
        now = time.monotonic()
        if self._last_fetch > 0 and (now - self._last_fetch) < self._cache_sec:
            return self._cached
        try:
            self._cached = get_high_risk_agent_types(
                self._client, timeout=self._timeout, trust_env=False
            )
            self._last_fetch = now
            return self._cached
        except Exception as e:
            logger.warning("HighRiskAgentCache get failed: %s", e)
            return []

    async def get_async(self) -> list[str]:
        """Async: return high-risk agent type slugs; use cached result for cache_sec. On error returns []."""
        now = time.monotonic()
        if self._last_fetch > 0 and (now - self._last_fetch) < self._cache_sec:
            return self._cached
        try:
            self._cached = await get_high_risk_agent_types_async(
                self._client, timeout=self._timeout, trust_env=False
            )
            self._last_fetch = now
            return self._cached
        except Exception as e:
            logger.warning("HighRiskAgentCache get_async failed: %s", e)
            return []


class McpPublisherCache:
    """In-memory cache for MCP publisher registry; 24-hour TTL (changes infrequently)."""

    def __init__(
        self,
        client: WawsdbClient,
        *,
        cache_sec: float = 86400.0,
        timeout: float = 5.0,
    ):
        self._client = client
        self._cache_sec = cache_sec
        self._timeout = timeout
        self._cached: dict = {}
        self._last_fetch: float = 0.0

    def get(self) -> dict:
        """Return MCP publisher registry; use cached result for cache_sec. On error returns {}."""
        now = time.monotonic()
        if self._last_fetch > 0 and (now - self._last_fetch) < self._cache_sec:
            return self._cached
        try:
            self._cached = get_mcp_publishers(
                self._client, timeout=self._timeout, trust_env=False
            )
            self._last_fetch = now
            return self._cached
        except Exception as e:
            logger.warning("McpPublisherCache get failed: %s", e)
            return {}

    async def get_async(self) -> dict:
        """Async: return MCP publisher registry; use cached result for cache_sec. On error returns {}."""
        now = time.monotonic()
        if self._last_fetch > 0 and (now - self._last_fetch) < self._cache_sec:
            return self._cached
        try:
            self._cached = await get_mcp_publishers_async(
                self._client, timeout=self._timeout, trust_env=False
            )
            self._last_fetch = now
            return self._cached
        except Exception as e:
            logger.warning("McpPublisherCache get_async failed: %s", e)
            return {}
