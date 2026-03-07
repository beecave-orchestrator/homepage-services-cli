"""Integration tests for settings CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from homepage_services.cli import app

runner = CliRunner()


class TestSettingsValidateCommand:
    """Tests for the settings validate command."""

    def test_validate_valid_file(self, sample_settings_file: Path) -> None:
        """Test validating a valid settings.yaml file."""
        result = runner.invoke(app, ["settings", "validate", "--settings-file", str(sample_settings_file)])
        assert result.exit_code == 0
        assert "OK: settings.yaml structure looks valid" in result.stdout

    def test_validate_invalid_structure(self, tmp_path: Path) -> None:
        """Test validating a file with invalid structure."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("- not a dict\n- list instead")
        result = runner.invoke(app, ["settings", "validate", "--settings-file", str(invalid_file)])
        # Should fail validation (not a dict)
        assert result.exit_code == 2


class TestSettingsSetCommand:
    """Tests for the settings set command."""

    def test_settings_set_title(self, sample_settings_file: Path) -> None:
        """Test setting title."""
        result = runner.invoke(
            app,
            [
                "settings",
                "set",
                "--title",
                "New Title",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Settings updated" in result.stdout

    def test_settings_set_multiple(self, sample_settings_file: Path) -> None:
        """Test setting multiple settings at once."""
        result = runner.invoke(
            app,
            [
                "settings",
                "set",
                "--theme",
                "light",
                "--color",
                "blue",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Settings updated" in result.stdout


class TestSettingsGetCommand:
    """Tests for the settings get command."""

    def test_settings_get_all(self, sample_settings_file: Path) -> None:
        """Test getting all settings."""
        result = runner.invoke(
            app,
            [
                "settings",
                "get",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "title" in result.stdout
        assert "theme" in result.stdout

    def test_settings_get_specific(self, sample_settings_file: Path) -> None:
        """Test getting a specific setting."""
        result = runner.invoke(
            app,
            [
                "settings",
                "get",
                "title",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "My Awesome Homepage" in result.stdout


class TestSettingsListCommand:
    """Tests for the settings list command."""

    def test_settings_list(self, sample_settings_file: Path) -> None:
        """Test listing all settings."""
        result = runner.invoke(
            app,
            [
                "settings",
                "list",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "title" in result.stdout
        assert "theme" in result.stdout
        assert "Layout:" in result.stdout
        assert "Providers:" in result.stdout


class TestProvidersAddCommand:
    """Tests for the providers add command."""

    def test_providers_add(self, sample_settings_file: Path) -> None:
        """Test adding a provider."""
        result = runner.invoke(
            app,
            [
                "settings",
                "providers",
                "add",
                "newprovider",
                "new-api-key",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added provider 'newprovider'" in result.stdout


class TestProvidersListCommand:
    """Tests for the providers list command."""

    def test_providers_list(self, sample_settings_file: Path) -> None:
        """Test listing providers."""
        result = runner.invoke(
            app,
            [
                "settings",
                "providers",
                "list",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Providers:" in result.stdout
        assert "openweathermap" in result.stdout
        assert "weatherapi" in result.stdout


class TestProvidersDeleteCommand:
    """Tests for the providers delete command."""

    def test_providers_delete(self, sample_settings_file: Path) -> None:
        """Test deleting a provider."""
        result = runner.invoke(
            app,
            [
                "settings",
                "providers",
                "delete",
                "openweathermap",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted provider 'openweathermap'" in result.stdout


class TestLayoutSetCommand:
    """Tests for the layout set command."""

    def test_layout_set(self, sample_settings_file: Path) -> None:
        """Test setting layout."""
        result = runner.invoke(
            app,
            [
                "settings",
                "layout",
                "set",
                "Media",
                "--style",
                "row",
                "--columns",
                "3",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated layout for group 'Media'" in result.stdout


class TestLayoutListCommand:
    """Tests for the layout list command."""

    def test_layout_list(self, sample_settings_file: Path) -> None:
        """Test listing layouts."""
        result = runner.invoke(
            app,
            [
                "settings",
                "layout",
                "list",
                "--settings-file",
                str(sample_settings_file),
            ],
        )
        assert result.exit_code == 0
        assert "Layout configurations:" in result.stdout
        assert "Proxmox" in result.stdout
        assert "Media" in result.stdout
