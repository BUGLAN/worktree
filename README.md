# wt

`wt` is an interactive Python CLI for creating, listing, archiving, and restoring Git worktrees from inside the current repository.

## Development

```bash
uv sync
uv run pytest -v
uv run wt --help
```

## Install As A Tool

```bash
uv tool install .
wt --help
uv tool uninstall wt
```

## Commands

- `wt create`
- `wt list`
- `wt remove`
- `wt restore`

## Notes

- Run `wt` inside a Git repository.
- New worktrees are created under `.worktrees/<branch>`.
- Archived worktrees are moved to `~/.worktree/has/<repo>/<branch>`.
