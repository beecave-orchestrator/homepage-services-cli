"""Unit tests for Homepage Services CLI settings utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from homepage_services.settings_utils import (
    print_settings,
    read_settings_file,
    Settings,
    validate_settings_file,
    write_settings_file,
)


class TestReadSettingsFile:
    """Tests for the read_settings_file function."""

    def test_read_valid_file(self, sample_settings_file: Path) -> None:
        """Test reading a valid settings.yaml file."""
        data = read_settings_file(sample_settings_file)
        assert isinstance(data, dict)
        assert "title" in data
        assert "theme" in data

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty settings.yaml file."""
        empty_file = tmp_path / "settings.yaml"
        empty_file.write_text("")
        data = read_settings_file(empty_file)
        assert data == {}

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_settings_file(tmp_path / "nonexistent.yaml")


class TestWriteSettingsFile:
    """Tests for the write_settings_file function."""

    def test_write_creates_backup(
        self, sample_settings_file: Path, tmp_path: Path
    ) -> None:
        """Test that writing creates a backup."""
        backup_file = tmp_path / "settings.yaml.bak"
        assert not backup_file.exists()

        data = read_settings_file(sample_settings_file)
        write_settings_file(sample_settings_file, data)

        assert backup_file.exists()

    def test_write_atomic(self, sample_settings_file: Path) -> None:
        """Test that writing is atomic."""
        data = read_settings_file(sample_settings_file)
        write_settings_file(sample_settings_file, data)

        # File should still be valid
        new_data = read_settings_file(sample_settings_file)
        assert new_data == data


class TestValidateSettingsFile:
    """Tests for the validate_settings_file function."""

    def test_validate_valid_file(self, sample_settings_file: Path) -> None:
        """Test validating a valid settings.yaml file."""
        errors = validate_settings_file(sample_settings_file)
        assert errors == []

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validating a nonexistent file."""
        errors = validate_settings_file(tmp_path / "nonexistent.yaml")
        assert len(errors) > 0
        assert "not found" in errors[0].lower()

    def test_validate_invalid_layout(self, tmp_path: Path) -> None:
        """Test validating a file with invalid layout."""
        invalid_file = tmp_path / "settings.yaml"
        invalid_file.write_text("layout: not-a-dict")
        errors = validate_settings_file(invalid_file)
        assert any("'layout' must be a dictionary" in e for e in errors)

    def test_validate_invalid_providers(self, tmp_path: Path) -> None:
        """Test validating a file with invalid providers."""
        invalid_file = tmp_path / "settings.yaml"
        invalid_file.write_text("providers: not-a-dict")
        errors = validate_settings_file(invalid_file)
        assert any("'providers' must be a dictionary" in e for e in errors)


class TestPrintSettings:
    """Tests for the print_settings function."""

    def test_print_settings(
        self, sample_settings_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing settings."""
        data = read_settings_file(sample_settings_file)
        settings = Settings.from_dict(data)
        print_settings(settings)
        captured = capsys.readouterr()
        assert "title" in captured.out
        assert "theme" in captured.out
        assert "Layout:" in captured.out
        assert "Providers:" in captured.out


class TestSettingsModel:
    """Tests for the Settings data model."""

    def test_settings_from_dict(self, sample_settings_file: Path) -> None:
        """Test creating Settings from a dictionary."""
        data = read_settings_file(sample_settings_file)
        settings = Settings.from_dict(data)

        assert settings.title == "My Awesome Homepage"
        assert settings.theme == "dark"
        assert settings.color == "slate"
        assert settings.layout is not None
        assert settings.providers is not None

    def test_settings_to_dict(self) -> None:
        """Test converting Settings to a dictionary."""
        settings = Settings(
            title="Test Title",
            theme="light",
            color="blue",
        )
        data = settings.to_dict()

        assert data["title"] == "Test Title"
        assert data["theme"] == "light"
        assert data["color"] == "blue"
