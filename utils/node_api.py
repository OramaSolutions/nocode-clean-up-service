"""Client for the Node backend's internal API (loopback only, no token; see
docs/internal-api.md in No-Code-Node-Server). URL and timeout come from the
environment (utils.config)."""

import json
import urllib.error
import urllib.request
from typing import List

from .config import node_api_settings


class NodeApiError(Exception):
    pass


def fetch_versions() -> List[dict]:
    """Every project version with its training state: dicts with username,
    task, project, version, trainStatus and trainedAt."""
    settings = node_api_settings()
    request = urllib.request.Request(settings.versions_url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=settings.timeout_seconds) as response:
            body = json.load(response)
    except urllib.error.HTTPError as e:
        raise NodeApiError(f"Node internal API returned HTTP {e.code}") from None
    except urllib.error.URLError as e:
        raise NodeApiError(f"cannot reach the Node internal API: {e.reason}") from None
    except TimeoutError:
        raise NodeApiError("Node internal API request timed out") from None
    except ValueError:
        raise NodeApiError("Node internal API returned invalid JSON") from None
    except OSError as e:
        raise NodeApiError(f"Node internal API request failed: {e.strerror or type(e).__name__}") from None

    versions = body.get("versions") if isinstance(body, dict) else None
    if not isinstance(versions, list):
        raise NodeApiError("unexpected Node internal API response shape")
    return [v for v in versions if isinstance(v, dict)]
