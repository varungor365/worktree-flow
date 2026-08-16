# worktree-flow

**Create clean Git worktrees for parallel branches, AI agents, and focused experiments.**

`worktree-flow` is a small safety-first CLI around `git worktree`. It creates predictable branch directories, lists active worktrees, and removes them only when the user explicitly asks. The default layout keeps worktrees under `.worktrees/`, which makes parallel feature work easy to inspect and clean up.

## Quick start

```bash
pipx install worktree-flow
cd my-repository
worktree-flow create fix-login --base main
worktree-flow list
cd .worktrees/fix-login
worktree-flow remove fix-login
```

Use `--path` when you need a different location. Names are validated against traversal and absolute-path mistakes. Removal refuses dirty worktrees unless `--force` is supplied.

## Why this exists

Git worktrees are excellent for parallel development but easy to misplace or remove incorrectly. This wrapper makes the safe path obvious and works well when several AI-assisted branches need isolated directories without repeatedly memorizing the raw Git commands.

## Why star this repository

Star this project if you work on multiple branches at once, run AI coding agents in isolated worktrees, or want a small Git workflow tool that is easy to audit and extend.

## Development

```bash
git clone https://github.com/varungor365/worktree-flow
cd worktree-flow
python -m pip install -e ".[dev]"
pytest -q
```

## License

MIT.
