from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def repo_root() -> Path:
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError("not inside a Git repository")
    return Path(result.stdout.strip()).resolve()


def validate_name(name: str) -> str:
    slug = name.strip().lower()
    if not SAFE_NAME.fullmatch(slug) or slug in {".", ".."}:
        raise ValueError("name must use lowercase letters, numbers, dots, hyphens, or underscores")
    return slug


def worktree_path(root: Path, name: str, custom: str | None = None) -> Path:
    path = Path(custom).expanduser() if custom else root / ".worktrees" / validate_name(name)
    path = path.resolve()
    if custom is None and root not in path.parents:
        raise ValueError("default worktree path escaped repository root")
    if custom and path == root:
        raise ValueError("worktree path cannot be the repository root")
    return path


def run_git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def list_worktrees() -> list[dict[str, str]]:
    raw = run_git("worktree", "list", "--porcelain")
    records = []
    current: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Safe Git worktree workflows")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("name")
    create.add_argument("--base", default="HEAD")
    create.add_argument("--path")
    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--json", action="store_true", dest="as_json")
    remove = sub.add_parser("remove")
    remove.add_argument("name")
    remove.add_argument("--path")
    remove.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    root = repo_root()
    if args.command == "create":
        name = validate_name(args.name)
        path = worktree_path(root, name, args.path)
        if path.exists():
            parser.error(f"worktree path already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        run_git("worktree", "add", "-b", name, str(path), args.base)
        print(f"created {name}: {path}")
        return 0
    if args.command == "list":
        records = list_worktrees()
        if args.as_json:
            print(json.dumps(records, indent=2))
        else:
            for record in records:
                print(f"{record.get('worktree', '')}	{record.get('branch', '(detached)')}")
        return 0
    name = validate_name(args.name)
    path = worktree_path(root, name, args.path)
    command = ["worktree", "remove"]
    if args.force:
        command.append("--force")
    command.append(str(path))
    run_git(*command)
    print(f"removed {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
