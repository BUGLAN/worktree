from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RepoContext:
    repo_root: Path
    git_common_dir: Path
    repo_name: str
    worktrees_root: Path
    archive_repo_root: Path


@dataclass(slots=True)
class WorktreeInfo:
    branch: str
    path: Path
    is_main: bool
    admin_dir_name: str | None


@dataclass(slots=True)
class ArchivedWorktree:
    archive_root: Path
    branch: str
    original_relative_path: Path
    admin_dir_name: str
    archived_at: str

    @property
    def files_path(self) -> Path:
        return self.archive_root / "files"

    @property
    def admin_path(self) -> Path:
        return self.archive_root / "admin" / self.admin_dir_name
