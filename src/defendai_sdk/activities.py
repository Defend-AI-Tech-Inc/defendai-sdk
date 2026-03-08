"""POST /activities: write audit activity to Wawsdb."""

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from defendai_sdk.client import WawsdbClient

logger = logging.getLogger(__name__)


def post_activity(
    client: WawsdbClient,
    host: str,
    path: str,
    prompt: str,
    verdict: str,
    eval_id: str,
    *,
    policy_checked: bool = False,
    note: str = "",
    blocked: bool = False,
    timeout: float = 5.0,
    trust_env: bool = False,
) -> None:
    """Sync: POST to Wawsdb /activities (audit record). Logs and ignores errors."""
    url = client.url("/activities")
    headers = client.auth_headers()
    body: dict[str, Any] = {
        "host": host,
        "path": path,
        "prompt": prompt[:500],
        "verdict": verdict,
        "eval_id": eval_id,
        "policy_checked": policy_checked,
        "note": note or "Audit activity from SDK.",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "llm_provider": host,
        "blocked": blocked,
    }
    try:
        with httpx.Client(timeout=timeout, trust_env=trust_env) as http_client:
            http_client.post(url, json=body, headers=headers)
    except Exception as e:
        logger.warning("Failed to post activity to Wawsdb: %s", e)


async def post_activity_async(
    client: WawsdbClient,
    host: str,
    path: str,
    prompt: str,
    verdict: str,
    eval_id: str,
    *,
    policy_checked: bool = False,
    note: str = "",
    blocked: bool = False,
    timeout: float = 5.0,
    trust_env: bool = False,
) -> None:
    """Async: POST to Wawsdb /activities (audit record). Logs and ignores errors."""
    url = client.url("/activities")
    headers = client.auth_headers()
    body = {
        "host": host,
        "path": path,
        "prompt": prompt[:500],
        "verdict": verdict,
        "eval_id": eval_id,
        "policy_checked": policy_checked,
        "note": note or "Audit activity from SDK.",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "llm_provider": host,
        "blocked": blocked,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as http_client:
            await http_client.post(url, json=body, headers=headers)
    except Exception as e:
        logger.warning("Failed to post activity to Wawsdb: %s", e)
