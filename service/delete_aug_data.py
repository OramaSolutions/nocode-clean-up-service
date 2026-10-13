"""Deletes the aug_data/ folder of a project version."""

import shutil

from utils.paths import AUG_DATA, refuse_symlink, version_dir
from utils.response import ServiceResponse


def delete_aug_data(version_path) -> ServiceResponse:
    """Deletes <version>/aug_data/. A missing folder counts as success.
    data = {"deleted": [folder names]}; no filesystem paths are returned."""
    try:
        target = version_dir(version_path) / AUG_DATA
        refuse_symlink(target)
        if not target.is_dir():
            return ServiceResponse.success(f"No {AUG_DATA} folder; nothing to delete", {"deleted": []})
        shutil.rmtree(target)
    except (ValueError, OSError) as e:
        return ServiceResponse.failed(f"Could not delete {AUG_DATA}", e, {"deleted": []})
    return ServiceResponse.success(f"Deleted {AUG_DATA}", {"deleted": [AUG_DATA]})
