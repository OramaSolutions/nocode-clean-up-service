"""Deletes the split_data/ folder and split_data.zip of a project version."""

import shutil

from utils.paths import SPLIT_DATA, SPLIT_DATA_ZIP, refuse_symlink, version_dir
from utils.response import ServiceResponse


def delete_split_data(version_path) -> ServiceResponse:
    """Deletes <version>/split_data/ and <version>/split_data.zip. Whichever
    is missing is skipped; if both are missing that counts as success.
    data = {"deleted": [names]}; on failure it shows what was already removed
    before the error. No filesystem paths are returned."""
    deleted = []
    try:
        version = version_dir(version_path)
        folder = version / SPLIT_DATA
        zip_file = version / SPLIT_DATA_ZIP
        # Check both before deleting either, so a refusal never leaves half done.
        refuse_symlink(folder)
        refuse_symlink(zip_file)
        if folder.is_dir():
            shutil.rmtree(folder)
            deleted.append(SPLIT_DATA)
        if zip_file.is_file():
            zip_file.unlink()
            deleted.append(SPLIT_DATA_ZIP)
    except (ValueError, OSError) as e:
        return ServiceResponse.failed(f"Could not delete {SPLIT_DATA} and {SPLIT_DATA_ZIP}", e, {"deleted": deleted})
    if not deleted:
        return ServiceResponse.success(f"No {SPLIT_DATA} or {SPLIT_DATA_ZIP}; nothing to delete", {"deleted": []})
    return ServiceResponse.success(f"Deleted {' and '.join(deleted)}", {"deleted": deleted})
