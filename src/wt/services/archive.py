from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from wt.errors import UserFacingError
from wt.models import ArchivedWorktree, RepoContext, WorktreeInfo
from wt.services.git import write_gitdir_file


def archive_root_for_branch(context: RepoContext, branch: str) -> Path:
    return context.archive_repo_root / branch


def archive_metadata_path(archive_root: Path) -> Path:
    return archive_root / ".wt-meta.json"


def load_archived_worktree(archive_root: Path) -> ArchivedWorktree:
    metadata_path = archive_metadata_path(archive_root)
    if not metadata_path.exists():
        raise UserFacingError(f"Archive metadata is missing: {metadata_path}")
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    return ArchivedWorktree(
        archive_root=archive_root,
        branch=payload["branch"],
        original_relative_path=Path(payload["original_relative_path"]),
        admin_dir_name=payload["admin_dir_name"],
        archived_at=payload["archived_at"],
    )


def list_archived_worktrees(context: RepoContext) -> list[ArchivedWorktree]:
    if not context.archive_repo_root.exists():
        return []
    archived: list[ArchivedWorktree] = []
    for entry in sorted(context.archive_repo_root.iterdir()):
        if not entry.is_dir():
            continue
        metadata_path = archive_metadata_path(entry)
        if not metadata_path.exists():
            continue
        archived.append(load_archived_worktree(entry))
    return archived


def write_archive_metadata(context: RepoContext, archive_root: Path, worktree: WorktreeInfo) -> None:
    payload = {
        "repo_name": context.repo_name,
        "branch": worktree.branch,
        "original_relative_path": str(worktree.path.relative_to(context.repo_root)),
        "admin_dir_name": worktree.admin_dir_name,
        "archived_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }
    archive_metadata_path(archive_root).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def archive_worktree(context: RepoContext, worktree: WorktreeInfo) -> ArchivedWorktree:
    if worktree.is_main:
        raise UserFacingError("The main worktree cannot be archived.")
    if not worktree.admin_dir_name:
        raise UserFacingError(f"Worktree {worktree.branch} is missing its admin directory name.")

    archive_root = archive_root_for_branch(context, worktree.branch)
    if archive_root.exists():
        raise UserFacingError(f"Archive destination already exists: {archive_root}")

    admin_source = context.git_common_dir / "worktrees" / worktree.admin_dir_name
    if not admin_source.exists():
        raise UserFacingError(f"Worktree admin directory is missing: {admin_source}")

    files_target = archive_root / "files"
    admin_parent = archive_root / "admin"
    archive_root.mkdir(parents=True, exist_ok=False)
    admin_parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(worktree.path), str(files_target))
    admin_target = admin_parent / worktree.admin_dir_name
    shutil.move(str(admin_source), str(admin_target))
    write_gitdir_file(files_target, admin_target)
    write_archive_metadata(context, archive_root, worktree)
    return load_archived_worktree(archive_root)


def restore_worktree(context: RepoContext, archived: ArchivedWorktree) -> Path:
    target_path = context.repo_root / archived.original_relative_path
    if target_path.exists():
        raise UserFacingError(f"Worktree destination already exists: {target_path}")

    admin_target = context.git_common_dir / "worktrees" / archived.admin_dir_name
    if admin_target.exists():
        raise UserFacingError(f"Git worktree admin destination already exists: {admin_target}")
    if not archived.files_path.exists():
        raise UserFacingError(f"Archived worktree files are missing: {archived.files_path}")
    if not archived.admin_path.exists():
        raise UserFacingError(f"Archived worktree admin directory is missing: {archived.admin_path}")

    admin_target.parent.mkdir(parents=True, exist_ok=True)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(archived.admin_path), str(admin_target))
    archive_metadata_path(archived.archive_root).unlink(missing_ok=True)
    shutil.move(str(archived.files_path), str(target_path))
    write_gitdir_file(target_path, admin_target)

    admin_parent = archived.archive_root / "admin"
    if admin_parent.exists():
        shutil.rmtree(admin_parent, ignore_errors=True)
    archived.archive_root.rmdir()
    return target_path
