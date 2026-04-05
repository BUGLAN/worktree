from __future__ import annotations

import os
import subprocess
from pathlib import Path

from wt.errors import UserFacingError
from wt.models import RepoContext, WorktreeInfo


def run_git(cwd: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        message = process.stderr.strip() or process.stdout.strip() or f"git {' '.join(args)} failed"
        raise UserFacingError(message)
    return process.stdout.strip()


def git_branch_exists(repo_root: Path, branch: str) -> bool:
    process = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return process.returncode == 0


def ensure_worktrees_ignored(context: RepoContext) -> None:
    info_dir = context.git_common_dir / "info"
    info_dir.mkdir(parents=True, exist_ok=True)
    exclude_path = info_dir / "exclude"
    entry = ".worktrees/"
    existing = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    lines = [line.strip() for line in existing.splitlines()]
    if entry not in lines:
        with exclude_path.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(f"{entry}\n")


def create_worktree(context: RepoContext, branch: str) -> Path:
    ensure_worktrees_ignored(context)
    target_path = context.worktrees_root / branch
    run_git(context.repo_root, "worktree", "add", "-b", branch, str(target_path))
    return target_path


def parse_gitdir_file(path: Path) -> Path:
    git_file = path / ".git"
    content = git_file.read_text(encoding="utf-8").strip()
    prefix = "gitdir: "
    if not content.startswith(prefix):
        raise UserFacingError(f"Expected a linked worktree gitdir file at {git_file}")
    gitdir = Path(content[len(prefix) :])
    if not gitdir.is_absolute():
        gitdir = (path / gitdir).resolve()
    return gitdir.resolve()


def write_gitdir_file(path: Path, admin_dir: Path) -> None:
    git_file = path / ".git"
    if git_file.exists():
        os.chmod(git_file, 0o666)
        if git_file.is_file():
            git_file.unlink()
    git_file.write_text(f"gitdir: {admin_dir}\n", encoding="utf-8")


def list_active_worktrees(context: RepoContext) -> list[WorktreeInfo]:
    output = run_git(context.repo_root, "worktree", "list", "--porcelain")
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, value = line.split(" ", 1)
        current[key] = value
    if current:
        entries.append(current)

    worktrees: list[WorktreeInfo] = []
    for entry in entries:
        worktree_path = Path(entry["worktree"]).resolve()
        branch_ref = entry.get("branch")
        branch = branch_ref.removeprefix("refs/heads/") if branch_ref else "(detached)"
        is_main = worktree_path == context.repo_root.resolve()
        admin_dir_name = None if is_main else parse_gitdir_file(worktree_path).name
        worktrees.append(
            WorktreeInfo(
                branch=branch,
                path=worktree_path,
                is_main=is_main,
                admin_dir_name=admin_dir_name,
            )
        )
    return sorted(worktrees, key=lambda item: (item.is_main, item.branch))


def find_worktree_by_branch(context: RepoContext, branch: str) -> WorktreeInfo:
    for worktree in list_active_worktrees(context):
        if worktree.branch == branch:
            return worktree
    raise UserFacingError(f"Unknown worktree branch: {branch}")
