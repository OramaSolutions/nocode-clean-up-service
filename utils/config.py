"""Service settings, read only from environment variables. A .env file in the
project root is loaded first (real environment variables win); example.env
lists every variable."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

# The Node internal API has no token: it is protected by listening on
# loopback only. Sending requests anywhere else would mean talking to an
# unprotected service, so only these hosts are accepted.
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class NodeApiSettings:
    versions_url: str
    timeout_seconds: float


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"{name} is not set (see example.env)")
    return value


def _positive(name: str, cast):
    raw = _required(name)
    try:
        value = cast(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a number") from None
    if value <= 0:
        raise ConfigError(f"{name} must be greater than 0")
    return value


def projects_root() -> Path:
    """Folder that holds <user>/<task>/<project>/<version>/."""
    return Path(_required("NOCODE_PROJECTS_ROOT"))


def node_api_settings() -> NodeApiSettings:
    url = _required("NODE_INTERNAL_VERSIONS_URL")
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in LOOPBACK_HOSTS:
        raise ConfigError("NODE_INTERNAL_VERSIONS_URL must be an http:// URL on this machine (127.0.0.1)")
    return NodeApiSettings(
        versions_url=url,
        timeout_seconds=_positive("NODE_INTERNAL_TIMEOUT_SECONDS", float),
    )


def retention_days() -> int:
    """Days after training completes before a version's data may be cleaned."""
    return _positive("CLEANUP_RETENTION_DAYS", int)
