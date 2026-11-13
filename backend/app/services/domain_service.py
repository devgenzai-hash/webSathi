from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse


def normalize_domain(value: Optional[str]) -> Optional[str]:
    """Normalize a user-entered domain or URL to a comparable host value."""
    if not value:
        return None

    raw_value = value.strip().lower()
    if not raw_value or raw_value in {"null", "undefined"}:
        return None

    try:
        parsed = urlparse(raw_value if "://" in raw_value else f"//{raw_value}")
        host = (parsed.hostname or "").strip().rstrip(".")
        if not host:
            return None

        port = parsed.port
        if port and not _is_default_port(parsed.scheme, port):
            return f"{host}:{port}"

        return host
    except ValueError:
        return None


def domains_match(registered_domain: str, request_domain: Optional[str]) -> bool:
    registered = normalize_domain(registered_domain)
    requested = normalize_domain(request_domain)
    if not registered or not requested:
        return False

    if registered == requested:
        return True

    return _strip_www(registered) == _strip_www(requested)


def _strip_www(host: str) -> str:
    return host[4:] if host.startswith("www.") else host


def _is_default_port(scheme: str, port: int) -> bool:
    return (scheme == "http" and port == 80) or (scheme == "https" and port == 443)