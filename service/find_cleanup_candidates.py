"""Finds the project versions whose intermediate data can be cleaned up."""

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from utils.config import projects_root, retention_days
from utils.dates import to_local_date, today
from utils.node_api import NodeApiError, fetch_versions
from utils.paths import VERSION_FIELDS, has_cleanup_data, version_dir, version_path
from utils.response import ServiceResponse
from utils.training import COMPLETED, has_trained_model


def find_cleanup_candidates() -> ServiceResponse:
    """Lists every version that meets all four conditions:
      1. the Node backend marks its Train step "completed",
      2. a trained model exists in its folder on disk (so the two agree),
      3. training finished at least CLEANUP_RETENTION_DAYS days ago,
      4. it still has something to clean (aug_data, split_data or the zip).

    data = {"cutoff_date", "count", "versions": [{"username", "task",
    "project", "version", "trained_on"}]}. No filesystem paths are returned."""
    try:
        root = projects_root()
        cutoff = today() - timedelta(days=retention_days())
        versions = fetch_versions()
    except (ValueError, NodeApiError) as e:
        return ServiceResponse.failed("Could not load the project versions", e)

    candidates = [c for c in (_check_version(root, v, cutoff) for v in versions) if c]
    return ServiceResponse.success(
        f"{len(candidates)} project versions are ready for cleanup",
        {"cutoff_date": cutoff.isoformat(), "count": len(candidates), "versions": candidates},
    )


def _check_version(root: Path, record: dict, cutoff: date) -> Optional[dict]:
    """The version's identity if it meets every condition, else None. The
    record's own fields are checked first; the disk only for those that pass."""
    if record.get("trainStatus") != COMPLETED:
        return None
    try:
        trained_on = to_local_date(record.get("trainedAt") or "")
    except ValueError:
        return None
    if trained_on > cutoff:
        return None

    identity = {field: record.get(field) for field in VERSION_FIELDS}
    if not all(isinstance(value, str) and value for value in identity.values()):
        return None
    try:
        folder = version_dir(version_path(identity, root), root)
    except ValueError:  # not on disk, or the names do not form a valid version path
        return None
    if not has_trained_model(folder) or not has_cleanup_data(folder):
        return None
    return {**identity, "trained_on": trained_on.isoformat()}
