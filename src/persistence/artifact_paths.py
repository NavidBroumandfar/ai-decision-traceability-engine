"""
Helpers for resolving local decision and trace artifact paths.
"""

import re
from pathlib import Path


_SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def artifact_path(base_dir: str | Path, run_id: str, suffix: str) -> Path:
    """
    Resolve an artifact path for a run_id constrained to a safe filename.

    This reference implementation stores local artifacts directly on disk, so a
    run_id must never be allowed to escape its storage directory.
    """
    if not _SAFE_RUN_ID.fullmatch(run_id):
        raise ValueError("run_id must be a safe filename token")

    base_path = Path(base_dir)
    path = base_path / f"{run_id}{suffix}"
    resolved_base = base_path.resolve()
    resolved_path = path.resolve()

    try:
        resolved_path.relative_to(resolved_base)
    except ValueError as exc:
        raise ValueError("run_id resolved outside the artifact directory") from exc

    return path
