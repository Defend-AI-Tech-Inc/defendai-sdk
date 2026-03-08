# defendai-sdk

DefendAI Wawsdb platform SDK: connection, auth, domain-list, verdict, activities, and health check. No proxy or interception logic.

## Install

```bash
pip install -e /path/to/defendai-sdk
```

## Usage

```python
from defendai_sdk import WawsdbClient, get_domain_list, fetch_verdict_async, post_activity_async, is_reachable_async, ReachabilityCache

client = WawsdbClient(
    wawsdb_url="https://wauzeway.defendai.ai",
    api_key="your-api-key",
    tenant_token="optional-tenant-token",
    user_email="user@example.com",
    device_id="device-001",
)

# Auth headers (e.g. for custom HTTP calls)
headers = client.auth_headers()  # Authorization, X-DefendAI-Tenant-Token, etc.

# GET /api/v1/domain-list
domain_lists = get_domain_list(client)

# POST /wauzeway-verdict (async)
verdict, eval_id = await fetch_verdict_async(client, prompt="Hello", host="chatgpt.com")

# POST /activities (async)
await post_activity_async(client, host="chatgpt.com", path="/api/...", prompt="...", verdict="ALLOW", eval_id=eval_id)

# Health check (one-shot or cached)
ok = await is_reachable_async(client.wawsdb_url, client.api_key)
cache = ReachabilityCache(client, cache_sec=30.0, timeout=3.0)
ok = await cache.is_reachable()
```

## API

- **Connection / auth**: `WawsdbClient(wawsdb_url, api_key, tenant_token=..., user_email=..., device_id=...)`, `auth_headers(api_key, tenant_token=..., ...)`
- **Domain list**: `get_domain_list(client)` → `DomainLists`, `get_domain_list_async(client)`
- **Verdict**: `fetch_verdict(client, prompt, ...)` / `fetch_verdict_async(...)` → `(verdict, eval_id)`
- **Activities**: `post_activity(client, ...)` / `post_activity_async(client, ...)`
- **Health**: `is_reachable(wawsdb_url, api_key, timeout=...)` / `is_reachable_async(...)`, `ReachabilityCache(client, cache_sec=..., timeout=...)`

## License

MIT
