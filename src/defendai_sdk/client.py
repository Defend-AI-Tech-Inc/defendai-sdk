"""Platform connection (wawsdb_url, api_key, tenant token) and auth headers."""


def auth_headers(
    api_key: str,
    tenant_token: str = "",
    user_email: str = "",
    device_id: str = "",
) -> dict[str, str]:
    """Build auth and identity headers for Wawsdb API calls.

    - Authorization: Bearer {api_key}
    - X-DefendAI-Tenant-Token: {tenant_token} (if set)
    - X-DefendAI-User: {user_email} (if set)
    - X-DefendAI-Device-Id: {device_id} (if set)
    """
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if tenant_token:
        headers["X-DefendAI-Tenant-Token"] = tenant_token
    if user_email:
        headers["X-DefendAI-User"] = user_email
    if device_id:
        headers["X-DefendAI-Device-Id"] = device_id
    return headers


class WawsdbClient:
    """Client for Wawsdb platform: holds connection params and builds auth headers."""

    def __init__(
        self,
        wawsdb_url: str,
        api_key: str,
        *,
        tenant_token: str = "",
        user_email: str = "",
        device_id: str = "",
    ):
        """Initialize with platform connection parameters.

        Args:
            wawsdb_url: Base URL for Wawsdb (e.g. https://wauzeway.defendai.ai).
            api_key: API key for Bearer auth.
            tenant_token: Optional tenant token (X-DefendAI-Tenant-Token).
            user_email: Optional user email (X-DefendAI-User).
            device_id: Optional device id (X-DefendAI-Device-Id).
        """
        self.wawsdb_url = wawsdb_url.rstrip("/")
        self.api_key = api_key
        self.tenant_token = tenant_token or ""
        self.user_email = user_email or ""
        self.device_id = device_id or ""

    def auth_headers(self) -> dict[str, str]:
        """Return headers dict for Authorization, X-DefendAI-Tenant-Token, and optional identity headers."""
        return auth_headers(
            api_key=self.api_key,
            tenant_token=self.tenant_token,
            user_email=self.user_email,
            device_id=self.device_id,
        )

    def url(self, path: str) -> str:
        """Return full URL for a path (path should start with /)."""
        return f"{self.wawsdb_url}{path}" if path.startswith("/") else f"{self.wawsdb_url}/{path}"

    def __repr__(self) -> str:
        return f"WawsdbClient(wawsdb_url={self.wawsdb_url!r})"
