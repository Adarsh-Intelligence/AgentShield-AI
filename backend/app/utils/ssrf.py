from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse
from backend.app.config import settings
from backend.app.core.exceptions import SSRFException


METADATA_HOSTNAMES = {
    "metadata.google.internal",
    "instance-data",
    "169.254.169.254",
}


def is_ip_private_or_restricted(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        return True


def validate_outbound_url(url: str, allow_private: bool | None = None) -> str:
    """
    Validates outbound URL against Server-Side Request Forgery (SSRF) vulnerabilities.
    """
    if allow_private is None:
        allow_private = settings.ALLOW_PRIVATE_IPS_FOR_TESTING

    if not url or not isinstance(url, str):
        raise SSRFException(str(url), "URL cannot be empty.")

    try:
        parsed = urlparse(url.strip())
    except Exception as exc:
        raise SSRFException(url, f"Malformed URL: {exc}")

    if parsed.scheme.lower() not in ("http", "https"):
        raise SSRFException(url, f"Invalid scheme '{parsed.scheme}'. Only http and https are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFException(url, "URL must contain a valid host.")

    hostname_lower = hostname.lower()

    if hostname_lower in METADATA_HOSTNAMES:
        raise SSRFException(url, "Access to cloud metadata service is strictly prohibited.")

    # Check allowlist if configured
    if settings.ALLOWED_AGENT_HOSTS:
        if hostname_lower not in [h.lower() for h in settings.ALLOWED_AGENT_HOSTS]:
            raise SSRFException(url, f"Host '{hostname}' is not in the allowed agent hosts list.")

    # Resolve IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise SSRFException(url, f"DNS resolution failed for '{hostname}': {exc}")

    resolved_ips = set()
    for item in addr_info:
        sockaddr = item[4]
        ip = sockaddr[0]
        resolved_ips.add(ip)

    if not resolved_ips:
        raise SSRFException(url, f"Could not resolve any IP address for host '{hostname}'.")

    if not allow_private:
        for ip in resolved_ips:
            if is_ip_private_or_restricted(ip):
                raise SSRFException(
                    url,
                    f"Resolved destination '{ip}' is a private, loopback, or reserved network address.",
                )

    return url

