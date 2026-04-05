from __future__ import annotations


def test_remove_command_archives_worktree_and_unregisters_it(
    cli_runner,
    repo_with_feature_worktree,
) -> None:
    result = cli_runner(repo_with_feature_worktree.repo_root, ["remove"], inputs=["1", ""])

    archive_root = repo_with_feature_worktree.archive_repo_root / "feature-login"

    assert result.exit_code == 0
    assert not (repo_with_feature_worktree.repo_root / ".worktrees" / "feature-login").exists()
    assert (archive_root / "files").exists()
    assert (archive_root / "admin").exists()
    assert (archive_root / ".wt-meta.json").exists()
    assert "feature-login" not in repo_with_feature_worktree.git_worktree_names()


def test_restore_command_restores_archived_worktree(
    cli_runner,
    archived_worktree_repo,
) -> None:
    result = cli_runner(archived_worktree_repo.repo_root, ["restore"], inputs=["1", ""])

    restored_path = archived_worktree_repo.repo_root / ".worktrees" / "feature-login"

    assert result.exit_code == 0
    assert restored_path.exists()
    assert "feature-login" in archived_worktree_repo.git_worktree_names()


def test_remove_fails_when_archive_destination_exists(
    cli_runner,
    repo_with_feature_worktree,
) -> None:
    archive_root = repo_with_feature_worktree.archive_repo_root / "feature-login"
    archive_root.mkdir(parents=True)

    result = cli_runner(repo_with_feature_worktree.repo_root, ["remove"], inputs=["1"])

    assert result.exit_code == 1
    assert "already exists" in result.output
