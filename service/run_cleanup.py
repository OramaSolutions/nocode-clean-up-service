"""Runs the whole cleanup once: find the eligible versions, then delete each
one's intermediate data (aug_data, then split_data + split_data.zip)."""

from utils.config import projects_root
from utils.paths import version_path
from utils.response import ServiceResponse, Status

from .delete_aug_data import delete_aug_data
from .delete_split_data import delete_split_data
from .find_cleanup_candidates import find_cleanup_candidates

STEPS = (("aug_data", delete_aug_data), ("split_data", delete_split_data))


def run_cleanup(dry_run: bool = False) -> ServiceResponse:
    """With dry_run, only reports the versions that would be cleaned.

    data = {"cutoff_date", "cleaned", "failed", "versions": [{username, task,
    project, version, trained_on, "steps": {"aug_data": response,
    "split_data": response}}]}. A failing version does not stop the others;
    any failure makes the overall status "failed"."""
    found = find_cleanup_candidates()
    if found.status != Status.SUCCESS:
        return found
    versions = found.data["versions"]
    if dry_run:
        return ServiceResponse.success(f"Dry run: {len(versions)} project versions would be cleaned", found.data)

    try:
        root = projects_root()
    except ValueError as e:
        return ServiceResponse.failed("Could not start the cleanup", e)

    results = []
    for version in versions:
        folder = version_path(version, root)
        steps = {name: step(folder).to_dict() for name, step in STEPS}
        results.append({**version, "steps": steps})

    failed = sum(any(s["status"] != Status.SUCCESS.value for s in r["steps"].values()) for r in results)
    data = {"cutoff_date": found.data["cutoff_date"], "cleaned": len(results) - failed, "failed": failed,
            "versions": results}
    if failed:
        return ServiceResponse.failed(f"Cleaned {len(results) - failed} of {len(results)} project versions",
                                      f"{failed} project versions had a failed step; see data.versions", data)
    return ServiceResponse.success(f"Cleaned {len(results)} project versions", data)
