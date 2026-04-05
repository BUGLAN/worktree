# UV Tool Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the `wt` project to use a lightweight `uv`-friendly build backend and support local installation via `uv tool install .`.

**Architecture:** Keep the existing `src/` package and CLI entry point unchanged. Limit the change to packaging metadata and user-facing setup documentation so the command implementation remains stable while the install workflow becomes `uv` native.

**Tech Stack:** Python 3, `uv`, `hatchling`, `pytest`

---

## File Map

- Modify: `pyproject.toml`
- Create: `README.md`
- Verify: `uv sync`
- Verify: `uv run pytest -v`
- Verify: `uv run wt --help`
- Verify: `uv tool install .`
- Verify: `wt --help`

### Task 1: Switch packaging metadata to hatchling

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update the build backend**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Keep the script entry point and add dev dependency group**

```toml
[project.scripts]
wt = "wt.cli:main"

[dependency-groups]
dev = ["pytest>=8"]
```

- [ ] **Step 3: Remove setuptools-specific configuration**

```toml
# Remove:
[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

- [ ] **Step 4: Verify metadata by syncing the environment**

Run: `uv sync`
Expected: success without packaging metadata errors

### Task 2: Add UV-based usage documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Document development setup**

```markdown
## Development

```bash
uv sync
uv run pytest -v
uv run wt --help
```
```

- [ ] **Step 2: Document local tool installation**

```markdown
## Install As A Tool

```bash
uv tool install .
wt --help
uv tool uninstall wt
```
```

- [ ] **Step 3: Keep the README focused on the supported commands**

```markdown
## Commands

- `wt create`
- `wt list`
- `wt remove`
- `wt restore`
```

### Task 3: Verify the end-to-end UV workflow

**Files:**
- Modify: `pyproject.toml`
- Create: `README.md`

- [ ] **Step 1: Run the test suite through uv**

Run: `uv run pytest -v`
Expected: all tests pass

- [ ] **Step 2: Verify the entry point in the project environment**

Run: `uv run wt --help`
Expected: help output shows the `wt` command and subcommands

- [ ] **Step 3: Install the project as a local uv tool**

Run: `uv tool install .`
Expected: installation succeeds and exposes `wt`

- [ ] **Step 4: Verify the installed tool**

Run: `wt --help`
Expected: help output shows the `wt` command and subcommands

- [ ] **Step 5: Remove the installed tool after verification**

Run: `uv tool uninstall wt`
Expected: uninstall succeeds

## Self-Review

- Spec coverage: build backend, dev dependency group, uv commands, and local tool install all map to Tasks 1 through 3
- Placeholder scan: all file edits and verification commands are explicit
- Type consistency: the plan keeps the existing `wt.cli:main` entry point unchanged

Plan complete and saved to `docs/superpowers/plans/2026-04-05-uv-tool-packaging.md`. The user already requested inline execution, so implementation should continue in this session.
