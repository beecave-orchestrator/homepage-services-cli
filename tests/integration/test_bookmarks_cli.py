"""Integration tests for bookmarks CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from homepage_services.cli import app

runner = CliRunner()


class TestBookmarksValidateCommand:
    """Tests for the bookmarks validate command."""

    def test_validate_valid_file(self, sample_bookmarks_file: Path) -> None:
        """Test validating a valid bookmarks.yaml file."""
        result = runner.invoke(app, ["bookmarks", "validate", "--bookmarks-file", str(sample_bookmarks_file)])
        assert result.exit_code == 0
        assert "OK: bookmarks.yaml structure looks valid" in result.stdout

    def test_validate_invalid_structure(self, tmp_path: Path) -> None:
        """Test validating a file with invalid structure."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("key: value")
        result = runner.invoke(app, ["bookmarks", "validate", "--bookmarks-file", str(invalid_file)])
        assert result.exit_code == 2
        assert "Validation failed" in result.stdout


class TestBookmarksListCommand:
    """Tests for the bookmarks list command."""

    def test_bookmarks_list(self, sample_bookmarks_file: Path) -> None:
        """Test listing all bookmarks."""
        result = runner.invoke(app, ["bookmarks", "list", "--bookmarks-file", str(sample_bookmarks_file)])
        assert result.exit_code == 0
        assert "Developer" in result.stdout
        assert "GitHub" in result.stdout
        assert "Social" in result.stdout

    def test_bookmarks_list_filtered(self, sample_bookmarks_file: Path) -> None:
        """Test listing bookmarks filtered by group."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "list",
                "--group",
                "Developer",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Group: Developer" in result.stdout
        assert "GitHub" in result.stdout
        assert "Social" not in result.stdout


class TestBookmarksAddCommand:
    """Tests for the bookmarks add command."""

    def test_bookmarks_add_basic(self, sample_bookmarks_file: Path) -> None:
        """Test adding a basic bookmark."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "add",
                "--url",
                "https://example.com",
                "--group",
                "Developer",
                "--name",
                "Example",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added bookmark 'Example'" in result.stdout

    def test_bookmarks_add_with_abbr(self, sample_bookmarks_file: Path) -> None:
        """Test adding a bookmark with abbreviation."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "add",
                "--url",
                "https://test.com",
                "--group",
                "Developer",
                "--abbr",
                "TST",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added bookmark 'Test'" in result.stdout

    def test_bookmarks_add_duplicate(self, sample_bookmarks_file: Path) -> None:
        """Test adding a duplicate bookmark."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "add",
                "--url",
                "https://github.com/new",
                "--group",
                "Developer",
                "--name",
                "GitHub",  # Already exists
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 2
        assert "already exists" in (result.stdout + result.stderr)


class TestBookmarksShowCommand:
    """Tests for the bookmarks show command."""

    def test_bookmarks_show(self, sample_bookmarks_file: Path) -> None:
        """Test showing bookmark details."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "show",
                "Developer",
                "GitHub",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Bookmark: GitHub" in result.stdout
        assert "href:" in result.stdout


class TestBookmarksUpdateCommand:
    """Tests for the bookmarks update command."""

    def test_bookmarks_update_url(self, sample_bookmarks_file: Path) -> None:
        """Test updating bookmark URL."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "update",
                "Developer",
                "GitHub",
                "--url",
                "https://github.com/new",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated bookmark 'GitHub'" in result.stdout

    def test_bookmarks_update_abbr(self, sample_bookmarks_file: Path) -> None:
        """Test updating bookmark abbreviation."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "update",
                "Developer",
                "GitHub",
                "--abbr",
                "GHNEW",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated bookmark 'GitHub'" in result.stdout


class TestBookmarksRenameCommand:
    """Tests for the bookmarks rename command."""

    def test_bookmarks_rename(self, sample_bookmarks_file: Path) -> None:
        """Test renaming a bookmark."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "rename",
                "Developer",
                "GitHub",
                "GitHub Repo",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Renamed bookmark 'GitHub' -> 'GitHub Repo'" in result.stdout


class TestBookmarksDeleteCommand:
    """Tests for the bookmarks delete command."""

    def test_bookmarks_delete(self, sample_bookmarks_file: Path) -> None:
        """Test deleting a bookmark."""
        result = runner.invoke(
            app,
            [
                "bookmarks",
                "delete",
                "Developer",
                "GitHub",
                "--bookmarks-file",
                str(sample_bookmarks_file),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted bookmark 'GitHub'" in result.stdout
