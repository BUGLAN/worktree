from __future__ import annotations


def test_build_parser_exposes_expected_commands() -> None:
    from wt.cli import build_parser

    parser = build_parser()
    command_parsers = parser._subparsers.choices

    assert set(command_parsers) == {"create", "list", "remove", "restore"}


def test_create_command_creates_new_branch_worktree(
    cli_runner,
    git_repo,
) -> None:
    result = cli_runner(git_repo.repo_root, ["create"], inputs=["feature-login", ""])

    assert result.exit_code == 0
    assert (git_repo.repo_root / ".worktrees" / "feature-login").exists()
    assert "feature-login" in git_repo.git_worktree_names()


def test_list_command_shows_active_and_archived_worktrees(
    cli_runner,
    archived_worktree_repo,
) -> None:
    result = cli_runner(archived_worktree_repo.repo_root, ["list"], inputs=[])

    assert result.exit_code == 0
    assert "Active worktrees" in result.output
    assert "Archived worktrees" in result.output
    assert "feature-login" in result.output
