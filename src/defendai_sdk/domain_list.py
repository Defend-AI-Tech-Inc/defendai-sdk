"""GET /api/v1/domain-list: fetch intercept and ignore domain lists from Wawsdb."""

import logging
from typing import TypedDict

import httpx

from defendai_sdk.client import WawsdbClient

logger = logging.getLogger(__name__)


class DomainLists(TypedDict):
    """Result of domain-list API: intercept_domains and ignore_domains."""

    intercept_domains: list[str]
    ignore_domains: list[str]


def get_domain_list(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> DomainLists:
    """Fetch domain list from Wawsdb GET /api/v1/domain-list.

    Uses sync httpx. On failure returns empty lists (no cache in SDK).
    """
    url = client.url("/api/v1/domain-list")
    default: DomainLists = {"intercept_domains": [], "ignore_domains": []}
    try:
        with httpx.Client(timeout=timeout, trust_env=trust_env) as http_client:
            resp = http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch domain list from API: %s", e)
        return default

    if not isinstance(data, dict):
        return default
    intercept = data.get("intercept_domains")
    ignore = data.get("ignore_domains")
    if isinstance(intercept, list) and isinstance(ignore, list):
        return DomainLists(
            intercept_domains=[str(x) for x in intercept if isinstance(x, str)],
            ignore_domains=[str(x) for x in ignore if isinstance(x, str)],
        )
    return default


async def get_domain_list_async(
    client: WawsdbClient,
    *,
    timeout: float = 10.0,
    trust_env: bool = False,
) -> DomainLists:
    """Async: fetch domain list from Wawsdb GET /api/v1/domain-list."""
    url = client.url("/api/v1/domain-list")
    default: DomainLists = {"intercept_domains": [], "ignore_domains": []}
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as http_client:
            resp = await http_client.get(url, headers=client.auth_headers())
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch domain list from API: %s", e)
        return default

    if not isinstance(data, dict):
        return default
    intercept = data.get("intercept_domains")
    ignore = data.get("ignore_domains")
    if isinstance(intercept, list) and isinstance(ignore, list):
        return DomainLists(
            intercept_domains=[str(x) for x in intercept if isinstance(x, str)],
            ignore_domains=[str(x) for x in ignore if isinstance(x, str)],
        )
    return default
