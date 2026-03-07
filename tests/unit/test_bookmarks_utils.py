"""Unit tests for Homepage Services CLI bookmarks utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from homepage_services.bookmarks_utils import (
    bookmark_entry_tuple,
    ensure_bookmark_group,
    find_bookmark,
    find_bookmark_group_index,
    print_bookmarks,
    read_bookmarks_file,
    validate_bookmarks_file,
    write_bookmarks_file,
)


class TestReadBookmarksFile:
    """Tests for the read_bookmarks_file function."""

    def test_read_valid_file(self, sample_bookmarks_file: Path) -> None:
        """Test reading a valid bookmarks.yaml file."""
        data = read_bookmarks_file(sample_bookmarks_file)
        assert isinstance(data, list)
        assert len(data) == 2
        assert "Developer" in data[0]

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty bookmarks.yaml file."""
        empty_file = tmp_path / "bookmarks.yaml"
        empty_file.write_text("")
        data = read_bookmarks_file(empty_file)
        assert data == []

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_bookmarks_file(tmp_path / "nonexistent.yaml")


class TestWriteBookmarksFile:
    """Tests for the write_bookmarks_file function."""

    def test_write_creates_backup(
        self, sample_bookmarks_file: Path, tmp_path: Path
    ) -> None:
        """Test that writing creates a backup."""
        backup_file = tmp_path / "bookmarks.yaml.bak"
        assert not backup_file.exists()

        data = read_bookmarks_file(sample_bookmarks_file)
        write_bookmarks_file(sample_bookmarks_file, data)

        assert backup_file.exists()

    def test_write_atomic(self, sample_bookmarks_file: Path) -> None:
        """Test that writing is atomic."""
        data = read_bookmarks_file(sample_bookmarks_file)
        write_bookmarks_file(sample_bookmarks_file, data)

        # File should still be valid
        new_data = read_bookmarks_file(sample_bookmarks_file)
        assert new_data == data


class TestFindBookmarkGroupIndex:
    """Tests for the find_bookmark_group_index function."""

    def test_find_existing_group(self, sample_bookmarks_file: Path) -> None:
        """Test finding an existing group."""
        data = read_bookmarks_file(sample_bookmarks_file)
        idx = find_bookmark_group_index(data, "Developer")
        assert idx is not None
        assert idx == 0

    def test_find_nonexistent_group(self, sample_bookmarks_file: Path) -> None:
        """Test finding a nonexistent group."""
        data = read_bookmarks_file(sample_bookmarks_file)
        idx = find_bookmark_group_index(data, "Nonexistent")
        assert idx is None


class TestEnsureBookmarkGroup:
    """Tests for the ensure_bookmark_group function."""

    def test_ensure_existing_group(self, sample_bookmarks_file: Path) -> None:
        """Test ensuring an existing group returns its index."""
        data = read_bookmarks_file(sample_bookmarks_file)
        idx = ensure_bookmark_group(data, "Developer")
        assert idx == 0

    def test_ensure_new_group(self, sample_bookmarks_file: Path) -> None:
        """Test ensuring a new group creates it."""
        data = read_bookmarks_file(sample_bookmarks_file)
        original_len = len(data)
        idx = ensure_bookmark_group(data, "New Group")
        assert idx == original_len
        assert len(data) == original_len + 1


class TestFindBookmark:
    """Tests for the find_bookmark function."""

    def test_find_existing_bookmark(self, sample_bookmarks_file: Path) -> None:
        """Test finding an existing bookmark."""
        data = read_bookmarks_file(sample_bookmarks_file)
        result = find_bookmark(data, "GitHub")
        assert result is not None
        group_name, gi, bi = result
        assert group_name == "Developer"
        assert gi == 0
        assert bi == 0

    def test_find_nonexistent_bookmark(self, sample_bookmarks_file: Path) -> None:
        """Test finding a nonexistent bookmark."""
        data = read_bookmarks_file(sample_bookmarks_file)
        result = find_bookmark(data, "Nonexistent")
        assert result is None


class TestBookmarkEntryTuple:
    """Tests for the bookmark_entry_tuple function."""

    def test_valid_entry(self) -> None:
        """Test extracting a valid bookmark entry."""
        entry = {"My Bookmark": {"href": "http://example.com", "abbr": "MB"}}
        result = bookmark_entry_tuple(entry)
        assert result is not None
        name, cfg = result
        assert name == "My Bookmark"
        assert cfg["href"] == "http://example.com"
        assert cfg["abbr"] == "MB"

    def test_invalid_entry_not_dict(self) -> None:
        """Test with non-dict entry."""
        result = bookmark_entry_tuple("not a dict")
        assert result is None

    def test_invalid_entry_multiple_keys(self) -> None:
        """Test with entry having multiple keys."""
        entry = {"Key1": "value1", "Key2": "value2"}
        result = bookmark_entry_tuple(entry)
        assert result is None


class TestValidateBookmarksFile:
    """Tests for the validate_bookmarks_file function."""

    def test_validate_valid_file(self, sample_bookmarks_file: Path) -> None:
        """Test validating a valid bookmarks.yaml file."""
        errors = validate_bookmarks_file(sample_bookmarks_file)
        assert errors == []

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validating a nonexistent file."""
        errors = validate_bookmarks_file(tmp_path / "nonexistent.yaml")
        assert len(errors) > 0
        assert "not found" in errors[0].lower()


class TestPrintBookmarks:
    """Tests for the print_bookmarks function."""

    def test_print_bookmarks(
        self, sample_bookmarks_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing bookmarks."""
        data = read_bookmarks_file(sample_bookmarks_file)
        print_bookmarks(data)
        captured = capsys.readouterr()
        assert "Developer" in captured.out
        assert "GitHub" in captured.out

    def test_print_bookmarks_filtered(
        self, sample_bookmarks_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing bookmarks filtered by group."""
        data = read_bookmarks_file(sample_bookmarks_file)
        print_bookmarks(data, group="Developer")
        captured = capsys.readouterr()
        assert "Group: Developer" in captured.out
        assert "GitHub" in captured.out
        assert "Social" not in captured.out
