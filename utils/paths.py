"""Path checks shared by the service functions. Error messages never include
the paths themselves, so they are safe to return to callers."""

from pathlib import Path
from typing import Optional

from .config import projects_root

# The four folder levels below the projects root, as named in identity dicts.
VERSION_FIELDS = ("username", "task", "project", "version")

# What the cleanup removes from a version folder.
AUG_DATA = "aug_data"
SPLIT_DATA = "split_data"
SPLIT_DATA_ZIP = "split_data.zip"


def has_cleanup_data(version: Path) -> bool:
    """True while anything the cleanup removes is still in the version folder."""
    return (version / AUG_DATA).is_dir() or (version / SPLIT_DATA).is_dir() or (version / SPLIT_DATA_ZIP).is_file()


def version_path(identity: dict, root: Path) -> Path:
    """<root>/<username>/<task>/<project>/<version> for an identity dict.
    Not validated; pass the result through version_dir() before using it."""
    return root.joinpath(*(identity[field] for field in VERSION_FIELDS))


def version_dir(version_path, root: Optional[Path] = None) -> Path:
    """Returns the version folder, or raises ValueError unless `version_path`
    is an existing <root>/<user>/<task>/<project>/<version> folder. `root`
    defaults to NOCODE_PROJECTS_ROOT. This stops a wrong argument (e.g. "/"
    or a project folder) from deleting anything."""
    root = (root or projects_root()).resolve()
    path = Path(version_path).resolve()
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        raise ValueError("path is outside the projects root") from None
    if len(parts) != 4:
        raise ValueError("path is not a version folder (expected <user>/<task>/<project>/<version>)")
    if not path.is_dir():
        raise ValueError("version folder does not exist")
    return path


def refuse_symlink(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"{path.name} is a symlink; refusing to delete")
