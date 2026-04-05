from __future__ import annotations

import contextlib
import io
import json
import subprocess
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def parse_worktree_admin_path(worktree_path: Path) -> Path:
    git_file = worktree_path / ".git"
    content = git_file.read_text(encoding="utf-8").strip()
    _, raw_path = content.split(": ", 1)
    return Path(raw_path)


def list_worktree_paths(repo_root: Path) -> list[str]:
    output = run(["git", "worktree", "list", "--porcelain"], cwd=repo_root).stdout
    paths: list[str] = []
    for line in output.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line.split(" ", 1)[1]).name)
    return paths


@dataclass(slots=True)
class RepoFixture:
    repo_root: Path
    home: Path

    @property
    def archive_repo_root(self) -> Path:
        return self.home / ".worktree" / "has" / self.repo_root.name

    def git_worktree_names(self) -> list[str]:
        return list_worktree_paths(self.repo_root)


@pytest.fixture()
def git_repo(tmp_path: Path) -> RepoFixture:
    repo_root = tmp_path / "demo-repo"
    home = tmp_path / "home"
    repo_root.mkdir(parents=True)
    home.mkdir(parents=True)

    run(["git", "init", "-b", "main"], cwd=repo_root)
    run(["git", "config", "user.name", "Test User"], cwd=repo_root)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo_root)
    (repo_root / "README.md").write_text("hello\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=repo_root)
    run(["git", "commit", "-m", "init"], cwd=repo_root)

    return RepoFixture(repo_root=repo_root, home=home)


@pytest.fixture()
def repo_with_feature_worktree(git_repo: RepoFixture) -> RepoFixture:
    target = git_repo.repo_root / ".worktrees" / "feature-login"
    run(["git", "worktree", "add", "-b", "feature-login", str(target)], cwd=git_repo.repo_root)
    return git_repo


@pytest.fixture()
def archived_worktree_repo(repo_with_feature_worktree: RepoFixture) -> RepoFixture:
    repo_root = repo_with_feature_worktree.repo_root
    archive_root = repo_with_feature_worktree.archive_repo_root / "feature-login"
    files_root = archive_root / "files"
    admin_root = archive_root / "admin"
    worktree_path = repo_root / ".worktrees" / "feature-login"
    admin_path = parse_worktree_admin_path(worktree_path)

    archive_root.mkdir(parents=True, exist_ok=True)
    admin_root.mkdir(parents=True, exist_ok=True)

    worktree_path.rename(files_root)
    admin_target = admin_root / admin_path.name
    admin_path.rename(admin_target)
    (archive_root / ".wt-meta.json").write_text(
        json.dumps(
            {
                "repo_name": repo_root.name,
                "branch": "feature-login",
                "original_relative_path": ".worktrees/feature-login",
                "admin_dir_name": admin_path.name,
                "archived_at": "2026-04-05T00:00:00+08:00",
            }
        ),
        encoding="utf-8",
    )

    return repo_with_feature_worktree


@dataclass(slots=True)
class CliResult:
    exit_code: int
    output: str


@pytest.fixture()
def cli_runner(monkeypatch: pytest.MonkeyPatch) -> Callable[[Path, list[str], list[str], Path | None], CliResult]:
    def _run(repo_root: Path, args: list[str], inputs: list[str], home: Path | None = None) -> CliResult:
        from wt.cli import main

        values = iter(inputs)
        stdout = io.StringIO()
        stderr = io.StringIO()
        selected_home = home or repo_root.parent / "home"

        def fake_input(prompt: str = "") -> str:
            print(prompt, end="", file=stdout)
            return next(values)

        monkeypatch.chdir(repo_root)
        monkeypatch.setenv("HOME", str(selected_home))
        monkeypatch.setenv("USERPROFILE", str(selected_home))
        monkeypatch.setattr("builtins.input", fake_input)

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                exit_code = main(args)
            except SystemExit as exc:  # pragma: no cover
                exit_code = int(exc.code)

        return CliResult(exit_code=exit_code, output=stdout.getvalue() + stderr.getvalue())

    return _run
