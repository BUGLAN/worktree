from __future__ import annotations

from wt.errors import UserFacingError
from wt.models import RepoContext, WorktreeInfo
from wt.services.archive import archive_root_for_branch, archive_worktree
from wt.services.git import find_worktree_by_branch, list_active_worktrees
from wt.services.prompts import PromptIO


def select_worktree(
    context: RepoContext,
    prompts: PromptIO[object],
    branch: str | None,
) -> WorktreeInfo:
    removable = [worktree for worktree in list_active_worktrees(context) if not worktree.is_main]
    if not removable:
        raise UserFacingError("There are no removable worktrees.")
    if branch:
        selected = find_worktree_by_branch(context, branch)
        if selected.is_main:
            raise UserFacingError("The main worktree cannot be archived.")
        return selected
    return prompts.choose_one("Select worktree to archive:", removable, lambda item: f"{item.branch}  {item.path}")


def run_remove(context: RepoContext, prompts: PromptIO[object], branch: str | None, yes: bool) -> str:
    selected = select_worktree(context, prompts, branch)
    archive_root = archive_root_for_branch(context, selected.branch)
    if archive_root.exists():
        raise UserFacingError(f"Archive destination already exists: {archive_root}")

    print(f"Branch: {selected.branch}")
    print(f"From: {selected.path}")
    print(f"To: {archive_root}")

    if not yes and not prompts.confirm("Continue?", default=True):
        return "Cancelled."

    archived = archive_worktree(context, selected)
    return f"Archived worktree {archived.branch} to {archived.archive_root}"
