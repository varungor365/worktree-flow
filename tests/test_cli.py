from pathlib import Path
import pytest
from worktree_flow.cli import validate_name, worktree_path


def test_validate_name_rejects_traversal():
    with pytest.raises(ValueError):
        validate_name("../escape")


def test_validate_name_normalizes_safe_slug():
    assert validate_name("Fix-Login") == "fix-login"


def test_default_worktree_is_inside_repo(tmp_path: Path):
    assert worktree_path(tmp_path, "feature-x") == (tmp_path / ".worktrees" / "feature-x").resolve()
