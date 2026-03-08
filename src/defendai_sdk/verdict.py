"""POST /wauzeway-verdict: policy verdict for a prompt."""

import logging
import uuid
from typing import Any

import httpx

from defendai_sdk.client import WawsdbClient

logger = logging.getLogger(__name__)


def fetch_verdict(
    client: WawsdbClient,
    prompt: str,
    *,
    host: str = "",
    model: str = "gpt-4",
    provider: str = "openai",
    eval_id: str | None = None,
    timeout: float = 5.0,
    trust_env: bool = False,
) -> tuple[str, str]:
    """Sync: call Wawsdb POST /wauzeway-verdict. Returns (verdict, eval_id).

    Verdict is typically 'ALLOW' or 'BLOCK'. On timeout/error returns ('ERROR_ALLOW', eval_id).
    """
    url = client.url("/wauzeway-verdict")
    eval_id = eval_id or str(uuid.uuid4())
    headers = client.auth_headers()
    body: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "provider": provider,
        "host": host,
        "eval_id": eval_id,
    }
    try:
        with httpx.Client(timeout=timeout, trust_env=trust_env) as http_client:
            r = http_client.post(url, json=body, headers=headers)
            r.raise_for_status()
            data = r.json()
            return (data.get("verdict", "ALLOW"), eval_id)
    except httpx.TimeoutException:
        logger.warning(
            "Verdict call timed out (%.1fs); returning ALLOW. host=%s",
            timeout,
            host or "unknown",
        )
        return ("TIMEOUT_ALLOW", eval_id)
    except Exception as e:
        logger.warning("Verdict call failed: %s", e)
        return ("ERROR_ALLOW", eval_id)


async def fetch_verdict_async(
    client: WawsdbClient,
    prompt: str,
    *,
    host: str = "",
    model: str = "gpt-4",
    provider: str = "openai",
    eval_id: str | None = None,
    timeout: float = 5.0,
    trust_env: bool = False,
) -> tuple[str, str]:
    """Async: call Wawsdb POST /wauzeway-verdict. Returns (verdict, eval_id)."""
    url = client.url("/wauzeway-verdict")
    eval_id = eval_id or str(uuid.uuid4())
    headers = client.auth_headers()
    body = {
        "prompt": prompt,
        "model": model,
        "provider": provider,
        "host": host,
        "eval_id": eval_id,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as http_client:
            r = await http_client.post(url, json=body, headers=headers)
            r.raise_for_status()
            data = r.json()
            return (data.get("verdict", "ALLOW"), eval_id)
    except httpx.TimeoutException:
        logger.warning(
            "Verdict call timed out (%.1fs); returning ALLOW. host=%s",
            timeout,
            host or "unknown",
        )
        return ("TIMEOUT_ALLOW", eval_id)
    except Exception as e:
        logger.warning("Verdict call failed: %s", e)
        return ("ERROR_ALLOW", eval_id)
