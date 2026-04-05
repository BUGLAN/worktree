# Worktree CLI Design

## Goal

Build a Python command-line tool named `wt` that helps users manage Git worktrees from inside the current repository. The tool must create worktrees under `.worktrees/<branch>`, archive removed worktrees under `~/.worktree/has/<repo>/<branch>` without deleting user files, and restore archived worktrees back into the repository.

## User-Facing Commands

The first version exposes four commands:

- `wt create`
- `wt list`
- `wt remove`
- `wt restore`

The tool is interactive by default. Each command guides the user through the minimum required prompts and asks for explicit confirmation before any create, archive, or restore action.

## Scope Rules

- The tool only works when executed inside a Git repository.
- The tool only targets the current repository.
- `create` only supports creating a new branch and a matching worktree.
- Worktrees are always created at `.worktrees/<branch>`.
- Archived worktrees are always stored at `~/.worktree/has/<repo>/<branch>`.
- Name collisions for branches, active worktree paths, or archive paths are hard errors.

## Command Behavior

### `wt create`

The command prompts for a new branch name, verifies that the branch does not already exist, verifies that `.worktrees/<branch>` does not already exist, shows a confirmation summary, then creates the worktree with the new branch checked out.

### `wt list`

The command shows two groups:

- active worktrees registered in the current repository
- archived worktrees stored under `~/.worktree/has/<repo>/`

Each entry shows the branch name and path. Archive entries are read from metadata stored in the archive.

### `wt remove`

The command lists removable active worktrees and excludes the main worktree. After the user selects one entry and confirms, the command archives the worktree instead of deleting it.

Archiving has two parts:

1. Move the worktree directory into `~/.worktree/has/<repo>/<branch>/files`
2. Move the Git admin directory from `.git/worktrees/<id>` into `~/.worktree/has/<repo>/<branch>/admin/<id>`

The archive root also stores `.wt-meta.json` describing the branch, active path, admin directory name, and timestamps needed for restore and display.

This design avoids destructive deletion while also removing the worktree from Git's active registry.

### `wt restore`

The command lists archived worktrees for the current repository. After selection and confirmation, it restores the archived files into `.worktrees/<branch>`, restores the matching admin directory into `.git/worktrees/<id>`, and runs `git worktree repair <path>` so Git rewrites any path references to the restored location.

## Internal Model

The implementation keeps four core concepts:

- `RepoContext`: current repository root, git directory, repository name, and `.worktrees` root
- `WorktreeInfo`: active worktree branch, path, whether it is the main worktree, and its admin directory name when applicable
- `ArchivedWorktree`: archive root, branch, original relative path, admin directory name, archive timestamp
- `CommandResult`: concise success messages returned by command handlers for CLI printing

## Archive Metadata

Every archived worktree includes `~/.worktree/has/<repo>/<branch>/.wt-meta.json` with:

```json
{
  "repo_name": "myrepo",
  "branch": "feature-login",
  "original_relative_path": ".worktrees/feature-login",
  "admin_dir_name": "feature-login",
  "archived_at": "2026-04-05T12:34:56+08:00"
}
```

The metadata is intentionally small. It only stores the fields required to list and restore archives reliably.

## CLI Interaction Rules

- Interactive by default
- Numeric menus for selecting active or archived worktrees
- Confirmation prompt before create, remove, or restore
- Pressing Enter accepts the default confirmation
- Fail fast on invalid state instead of prompting for conflict resolution

## Error Handling

User-facing validation errors include:

- not inside a Git repository
- branch already exists
- worktree path already exists
- archive path already exists
- selected worktree is the main worktree
- archive metadata missing or malformed
- archive admin directory missing

System-level failures from Git commands or filesystem moves should preserve the original exception text in the error message.

## Testing Strategy

Use `pytest` with temporary repositories created during tests. Verify:

- `create` creates a new branch and `.worktrees/<branch>`
- `list` shows active and archived worktrees
- `remove` archives files and removes the worktree from Git's active list
- `restore` restores both files and Git admin state, then re-registers the worktree
- collision cases and invalid repository usage fail with readable errors

## Packaging And UV Workflow

The project should be managed with `uv` and installable locally as a tool from the project directory.

- Use a lightweight build backend compatible with `uv`; choose `hatchling`
- Keep the existing `src/` layout
- Keep the CLI entry point `wt = "wt.cli:main"`
- Put developer dependencies under `[dependency-groups]`
- Support these commands:
  - `uv sync`
  - `uv run pytest -v`
  - `uv run wt --help`
  - `uv tool install .`
  - `wt --help`

The packaging change must not alter CLI behavior. It only changes build metadata, local developer workflow, and installation instructions.
