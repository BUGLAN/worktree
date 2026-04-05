from __future__ import annotations

from wt.models import RepoContext
from wt.services.archive import list_archived_worktrees
from wt.services.git import list_active_worktrees


def run_list(context: RepoContext) -> str:
    active = list_active_worktrees(context)
    archived = list_archived_worktrees(context)

    lines = ["Active worktrees:"]
    if active:
        for index, worktree in enumerate(active, start=1):
            lines.append(f"{index}. {worktree.branch}  {worktree.path}")
    else:
        lines.append("(none)")

    lines.append("")
    lines.append("Archived worktrees:")
    if archived:
        for index, item in enumerate(archived, start=1):
            lines.append(f"{index}. {item.branch}  {item.archive_root}")
    else:
        lines.append("(none)")

    return "\n".join(lines)
