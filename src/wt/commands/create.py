from __future__ import annotations

from wt.errors import UserFacingError
from wt.models import RepoContext
from wt.services.git import create_worktree, git_branch_exists
from wt.services.prompts import PromptIO


def run_create(context: RepoContext, prompts: PromptIO[object], branch: str | None, yes: bool) -> str:
    selected_branch = branch or prompts.ask_text("New branch name")
    target_path = context.worktrees_root / selected_branch

    if git_branch_exists(context.repo_root, selected_branch):
        raise UserFacingError(f"Branch already exists: {selected_branch}")
    if target_path.exists():
        raise UserFacingError(f"Worktree path already exists: {target_path}")

    print(f"Repo: {context.repo_name}")
    print(f"Branch: {selected_branch}")
    print(f"Path: {target_path}")

    if not yes and not prompts.confirm("Continue?", default=True):
        return "Cancelled."

    created_path = create_worktree(context, selected_branch)
    return f"Created worktree {selected_branch} at {created_path}"
