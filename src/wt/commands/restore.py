from __future__ import annotations

from wt.errors import UserFacingError
from wt.models import ArchivedWorktree, RepoContext
from wt.services.archive import list_archived_worktrees, restore_worktree
from wt.services.git import ensure_worktrees_ignored, list_active_worktrees, run_git
from wt.services.prompts import PromptIO


def select_archive(
    context: RepoContext,
    prompts: PromptIO[object],
    branch: str | None,
) -> ArchivedWorktree:
    archived = list_archived_worktrees(context)
    if not archived:
        raise UserFacingError("There are no archived worktrees.")
    if branch:
        for item in archived:
            if item.branch == branch:
                return item
        raise UserFacingError(f"Unknown archived worktree branch: {branch}")
    return prompts.choose_one("Select archived worktree:", archived, lambda item: f"{item.branch}  {item.archive_root}")


def run_restore(context: RepoContext, prompts: PromptIO[object], branch: str | None, yes: bool) -> str:
    archived = select_archive(context, prompts, branch)
    target_path = context.repo_root / archived.original_relative_path

    if any(worktree.branch == archived.branch for worktree in list_active_worktrees(context)):
        raise UserFacingError(f"An active worktree already uses branch: {archived.branch}")
    if target_path.exists():
        raise UserFacingError(f"Worktree destination already exists: {target_path}")

    print(f"Branch: {archived.branch}")
    print(f"From: {archived.archive_root}")
    print(f"To: {target_path}")

    if not yes and not prompts.confirm("Continue?", default=True):
        return "Cancelled."

    ensure_worktrees_ignored(context)
    restored_path = restore_worktree(context, archived)
    run_git(context.repo_root, "worktree", "repair", str(restored_path))
    return f"Restored worktree {archived.branch} to {restored_path}"
