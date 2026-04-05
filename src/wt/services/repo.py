from __future__ import annotations

import os
from pathlib import Path

from wt.errors import UserFacingError
from wt.models import RepoContext
from wt.services.git import run_git


def discover_repo_context(cwd: Path | None = None) -> RepoContext:
    current = (cwd or Path.cwd()).resolve()

    try:
        common_dir_raw = run_git(current, "rev-parse", "--path-format=absolute", "--git-common-dir")
    except UserFacingError as exc:
        raise UserFacingError("wt must be run inside a Git repository.") from exc

    git_common_dir = Path(common_dir_raw).resolve()
    repo_root = git_common_dir.parent
    repo_name = repo_root.name
    archive_home = Path(os.path.expanduser("~"))

    return RepoContext(
        repo_root=repo_root,
        git_common_dir=git_common_dir,
        repo_name=repo_name,
        worktrees_root=repo_root / ".worktrees",
        archive_repo_root=archive_home / ".worktree" / "has" / repo_name,
    )
