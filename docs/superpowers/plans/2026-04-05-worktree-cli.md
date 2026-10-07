# Worktree CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an interactive Python CLI named `wt` that creates, lists, archives, and restores Git worktrees without deleting archived files.

**Architecture:** Use a small `argparse` entrypoint that delegates to focused command functions. Keep Git parsing, archive movement, repository context, and prompts in separate service modules so the command layer stays thin and the core behavior is easy to test with temporary repositories.

**Tech Stack:** Python 3, `argparse`, `pathlib`, `subprocess`, `json`, `shutil`, `dataclasses`, `pytest`

---

## File Map

- Create: `pyproject.toml`
- Create: `src/wt/__init__.py`
- Create: `src/wt/__main__.py`
- Create: `src/wt/cli.py`
- Create: `src/wt/errors.py`
- Create: `src/wt/models.py`
- Create: `src/wt/services/repo.py`
- Create: `src/wt/services/git.py`
- Create: `src/wt/services/archive.py`
- Create: `src/wt/services/prompts.py`
- Create: `src/wt/commands/create.py`
- Create: `src/wt/commands/list.py`
- Create: `src/wt/commands/remove.py`
- Create: `src/wt/commands/restore.py`
- Create: `tests/conftest.py`
- Create: `tests/test_cli_flow.py`
- Create: `tests/test_archive_roundtrip.py`

### Task 1: Scaffold the package and command surface

**Files:**
- Create: `pyproject.toml`
- Create: `src/wt/__init__.py`
- Create: `src/wt/__main__.py`
- Create: `src/wt/cli.py`
- Create: `src/wt/errors.py`
- Create: `src/wt/models.py`
- Test: `tests/test_cli_flow.py`

- [ ] **Step 1: Write the failing test**

```python
from wt.cli import build_parser


def test_build_parser_exposes_expected_commands():
    parser = build_parser()

    command_parsers = parser._subparsers._group_actions[0].choices

    assert set(command_parsers) == {"create", "list", "remove", "restore"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_flow.py::test_build_parser_exposes_expected_commands -v`
Expected: FAIL with `ModuleNotFoundError` for `wt`

- [ ] **Step 3: Write minimal implementation**

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wt")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "list", "remove", "restore"):
        subparsers.add_parser(name)
    return parser
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli_flow.py::test_build_parser_exposes_expected_commands -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/wt/__init__.py src/wt/__main__.py src/wt/cli.py src/wt/errors.py src/wt/models.py tests/test_cli_flow.py
git commit -m "feat: scaffold wt command surface"
```

### Task 2: Add repository detection and interactive create

**Files:**
- Modify: `src/wt/cli.py`
- Create: `src/wt/services/repo.py`
- Create: `src/wt/services/git.py`
- Create: `src/wt/services/prompts.py`
- Create: `src/wt/commands/create.py`
- Modify: `tests/conftest.py`
- Modify: `tests/test_cli_flow.py`

- [ ] **Step 1: Write the failing test**

```python
def test_create_command_creates_new_branch_worktree(cli_runner, git_repo):
    result = cli_runner(
        git_repo,
        ["create"],
        inputs=["feature-login", "", ""],
    )

    assert result.exit_code == 0
    assert (git_repo / ".worktrees" / "feature-login").exists()
    assert "feature-login" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_flow.py::test_create_command_creates_new_branch_worktree -v`
Expected: FAIL because `create` does not execute any behavior yet

- [ ] **Step 3: Write minimal implementation**

```python
def run_create(context: RepoContext, prompt: PromptIO) -> str:
    branch = prompt.ask_text("New branch name")
    target = context.worktrees_root / branch
    ensure_branch_missing(context.repo_root, branch)
    ensure_path_missing(target)
    if not prompt.confirm("Continue?", default=True):
        return "Cancelled."
    add_worktree(context.repo_root, target, branch)
    return f"Created {branch} at {target}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli_flow.py::test_create_command_creates_new_branch_worktree -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/wt/cli.py src/wt/services/repo.py src/wt/services/git.py src/wt/services/prompts.py src/wt/commands/create.py tests/conftest.py tests/test_cli_flow.py
git commit -m "feat: add interactive worktree creation"
```

### Task 3: Add active and archived listing

**Files:**
- Create: `src/wt/commands/list.py`
- Create: `src/wt/services/archive.py`
- Modify: `src/wt/cli.py`
- Modify: `tests/test_cli_flow.py`

- [ ] **Step 1: Write the failing test**

```python
def test_list_command_shows_active_and_archived_worktrees(cli_runner, archived_worktree_repo):
    result = cli_runner(archived_worktree_repo.repo_root, ["list"], inputs=[])

    assert result.exit_code == 0
    assert "Active worktrees" in result.output
    assert "Archived worktrees" in result.output
    assert "feature-archived" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_flow.py::test_list_command_shows_active_and_archived_worktrees -v`
Expected: FAIL because `list` does not report archive entries yet

- [ ] **Step 3: Write minimal implementation**

```python
def run_list(context: RepoContext) -> str:
    active = list_active_worktrees(context)
    archived = list_archived_worktrees(context)
    return format_listing(active, archived)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli_flow.py::test_list_command_shows_active_and_archived_worktrees -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/wt/commands/list.py src/wt/services/archive.py src/wt/cli.py tests/test_cli_flow.py
git commit -m "feat: list active and archived worktrees"
```

### Task 4: Archive remove behavior

**Files:**
- Create: `src/wt/commands/remove.py`
- Modify: `src/wt/services/archive.py`
- Modify: `src/wt/services/git.py`
- Modify: `src/wt/cli.py`
- Create: `tests/test_archive_roundtrip.py`

- [ ] **Step 1: Write the failing test**

```python
def test_remove_command_archives_worktree_and_unregisters_it(cli_runner, repo_with_feature_worktree):
    result = cli_runner(repo_with_feature_worktree.repo_root, ["remove"], inputs=["1", ""])

    assert result.exit_code == 0
    assert not (repo_with_feature_worktree.repo_root / ".worktrees" / "feature-login").exists()
    assert repo_with_feature_worktree.archive_root.joinpath("feature-login", "files").exists()
    assert "feature-login" not in repo_with_feature_worktree.git_worktree_paths()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_archive_roundtrip.py::test_remove_command_archives_worktree_and_unregisters_it -v`
Expected: FAIL because removal and archive movement are not implemented

- [ ] **Step 3: Write minimal implementation**

```python
def archive_registered_worktree(context: RepoContext, worktree: WorktreeInfo) -> ArchivedWorktree:
    archive_root = build_archive_root(context, worktree.branch)
    shutil.move(str(worktree.path), str(archive_root / "files"))
    shutil.move(str(context.git_dir / "worktrees" / worktree.admin_dir_name), str(archive_root / "admin" / worktree.admin_dir_name))
    write_archive_metadata(archive_root, worktree)
    return load_archived_worktree(archive_root)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_archive_roundtrip.py::test_remove_command_archives_worktree_and_unregisters_it -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/wt/commands/remove.py src/wt/services/archive.py src/wt/services/git.py src/wt/cli.py tests/test_archive_roundtrip.py
git commit -m "feat: archive worktrees instead of deleting them"
```

### Task 5: Restore archived worktrees

**Files:**
- Create: `src/wt/commands/restore.py`
- Modify: `src/wt/services/archive.py`
- Modify: `src/wt/services/git.py`
- Modify: `src/wt/cli.py`
- Modify: `tests/test_archive_roundtrip.py`

- [ ] **Step 1: Write the failing test**

```python
def test_restore_command_restores_archived_worktree(cli_runner, archived_worktree_repo):
    result = cli_runner(archived_worktree_repo.repo_root, ["restore"], inputs=["1", ""])

    restored_path = archived_worktree_repo.repo_root / ".worktrees" / "feature-archived"

    assert result.exit_code == 0
    assert restored_path.exists()
    assert "feature-archived" in archived_worktree_repo.git_worktree_paths()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_archive_roundtrip.py::test_restore_command_restores_archived_worktree -v`
Expected: FAIL because restore and `git worktree repair` are not implemented

- [ ] **Step 3: Write minimal implementation**

```python
def restore_archived_worktree(context: RepoContext, archived: ArchivedWorktree) -> WorktreeInfo:
    target = context.worktrees_root / archived.branch
    shutil.move(str(archived.files_path), str(target))
    shutil.move(str(archived.admin_path), str(context.git_dir / "worktrees" / archived.admin_dir_name))
    run_git(context.repo_root, "worktree", "repair", str(target))
    return find_worktree_by_path(context, target)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_archive_roundtrip.py::test_restore_command_restores_archived_worktree -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/wt/commands/restore.py src/wt/services/archive.py src/wt/services/git.py src/wt/cli.py tests/test_archive_roundtrip.py
git commit -m "feat: restore archived worktrees"
```

### Task 6: Validate error cases and polish output

**Files:**
- Modify: `src/wt/cli.py`
- Modify: `src/wt/services/archive.py`
- Modify: `src/wt/services/git.py`
- Modify: `tests/test_cli_flow.py`
- Modify: `tests/test_archive_roundtrip.py`

- [ ] **Step 1: Write the failing test**

```python
def test_remove_fails_when_archive_destination_exists(cli_runner, repo_with_feature_worktree):
    archive_root = repo_with_feature_worktree.archive_root / "feature-login"
    archive_root.mkdir(parents=True)

    result = cli_runner(repo_with_feature_worktree.repo_root, ["remove"], inputs=["1", ""])

    assert result.exit_code == 1
    assert "already exists" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_archive_roundtrip.py::test_remove_fails_when_archive_destination_exists -v`
Expected: FAIL because collisions are not reported correctly yet

- [ ] **Step 3: Write minimal implementation**

```python
if archive_root.exists():
    raise UserFacingError(f"Archive destination already exists: {archive_root}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_archive_roundtrip.py::test_remove_fails_when_archive_destination_exists -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/wt/cli.py src/wt/services/archive.py src/wt/services/git.py tests/test_cli_flow.py tests/test_archive_roundtrip.py
git commit -m "feat: harden validation and output"
```

## Self-Review

- Spec coverage: commands, archive layout, metadata, and error handling all map to tasks 1 through 6
- Placeholder scan: no TODO or implementation gaps remain in the task list
- Type consistency: `RepoContext`, `WorktreeInfo`, and `ArchivedWorktree` names are consistent across tasks

Plan complete and saved to `docs/superpowers/plans/2026-04-05-worktree-cli.md`. The user already requested inline execution, so implementation should continue in this session.




1