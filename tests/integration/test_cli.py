"""Integration tests for Homepage Services CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from homepage_services.cli import app

runner = CliRunner()


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_valid_file(self, sample_services_file: Path) -> None:
        """Test validating a valid services.yaml file."""
        result = runner.invoke(app, ["validate", "--services-file", str(sample_services_file)])
        assert result.exit_code == 0
        assert "OK: services.yaml structure looks valid" in result.stdout

    def test_validate_invalid_structure(self, tmp_path: Path) -> None:
        """Test validating a file with invalid structure."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("key: value")
        result = runner.invoke(app, ["validate", "--services-file", str(invalid_file)])
        assert result.exit_code == 2
        assert "Validation failed" in result.stdout


class TestGroupsListCommand:
    """Tests for the groups list command."""

    def test_groups_list(self, sample_services_file: Path) -> None:
        """Test listing all groups."""
        result = runner.invoke(app, ["groups", "list", "--services-file", str(sample_services_file)])
        assert result.exit_code == 0
        assert "My First Group" in result.stdout
        assert "My Second Group" in result.stdout
        assert "Infrastructure" in result.stdout


class TestGroupsAddCommand:
    """Tests for the groups add command."""

    def test_groups_add(self, sample_services_file: Path) -> None:
        """Test adding a new group."""
        result = runner.invoke(
            app,
            ["groups", "add", "New Group", "--services-file", str(sample_services_file)],
        )
        assert result.exit_code == 0
        assert "Added group 'New Group'" in result.stdout

    def test_groups_add_duplicate(self, sample_services_file: Path) -> None:
        """Test adding a duplicate group."""
        result = runner.invoke(
            app,
            ["groups", "add", "My First Group", "--services-file", str(sample_services_file)],
        )
        assert result.exit_code == 2
        assert "already exists" in result.stdout


class TestGroupsRenameCommand:
    """Tests for the groups rename command."""

    def test_groups_rename(self, sample_services_file: Path) -> None:
        """Test renaming a group."""
        result = runner.invoke(
            app,
            [
                "groups",
                "rename",
                "My First Group",
                "Renamed Group",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Renamed group 'My First Group' -> 'Renamed Group'" in result.stdout

    def test_groups_rename_nonexistent(self, sample_services_file: Path) -> None:
        """Test renaming a nonexistent group."""
        result = runner.invoke(
            app,
            [
                "groups",
                "rename",
                "Nonexistent",
                "New Name",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 2
        assert "not found" in result.stdout


class TestGroupsDeleteCommand:
    """Tests for the groups delete command."""

    def test_groups_delete_empty(
        self, sample_services_file: Path, tmp_path: Path
    ) -> None:
        """Test deleting an empty group."""
        # First add an empty group
        runner.invoke(
            app,
            ["groups", "add", "To Delete", "--services-file", str(sample_services_file)],
        )
        # Then delete it
        result = runner.invoke(
            app,
            ["groups", "delete", "To Delete", "--services-file", str(sample_services_file)],
        )
        assert result.exit_code == 0
        assert "Deleted group 'To Delete'" in result.stdout

    def test_groups_delete_with_services(
        self, sample_services_file: Path
    ) -> None:
        """Test deleting a group with services without --force."""
        result = runner.invoke(
            app,
            ["groups", "delete", "My First Group", "--services-file", str(sample_services_file)],
        )
        assert result.exit_code == 2
        assert "Use --force to delete" in result.stdout

    def test_groups_delete_with_force(
        self, sample_services_file: Path
    ) -> None:
        """Test deleting a group with services using --force."""
        result = runner.invoke(
            app,
            [
                "groups",
                "delete",
                "My First Group",
                "--force",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted group 'My First Group'" in result.stdout


class TestServicesListCommand:
    """Tests for the services list command."""

    def test_services_list(self, sample_services_file: Path) -> None:
        """Test listing all services."""
        result = runner.invoke(
            app, ["services", "list", "--services-file", str(sample_services_file)]
        )
        assert result.exit_code == 0
        assert "Plex" in result.stdout
        assert "Proxmox VE" in result.stdout

    def test_services_list_filtered(self, sample_services_file: Path) -> None:
        """Test listing services filtered by group."""
        result = runner.invoke(
            app,
            [
                "services",
                "list",
                "--group",
                "My First Group",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Group: My First Group" in result.stdout
        assert "Plex" in result.stdout


class TestServicesAddCommand:
    """Tests for the services add command."""

    def test_services_add_basic(self, sample_services_file: Path) -> None:
        """Test adding a basic service."""
        result = runner.invoke(
            app,
            [
                "services",
                "add",
                "--href",
                "http://test.local",
                "--group",
                "My First Group",
                "--name",
                "Test Service",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added service 'Test Service'" in result.stdout

    def test_services_add_with_icon(self, sample_services_file: Path) -> None:
        """Test adding a service with icon."""
        result = runner.invoke(
            app,
            [
                "services",
                "add",
                "--href",
                "http://test.local",
                "--group",
                "My First Group",
                "--icon",
                "mdi:test",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added service 'Test'" in result.stdout

    def test_services_add_duplicate(self, sample_services_file: Path) -> None:
        """Test adding a duplicate service."""
        result = runner.invoke(
            app,
            [
                "services",
                "add",
                "--href",
                "http://test.local",
                "--group",
                "My First Group",
                "--name",
                "Plex",  # Already exists
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 2
        assert "already exists" in result.stdout


class TestServicesShowCommand:
    """Tests for the services show command."""

    def test_services_show(self, sample_services_file: Path) -> None:
        """Test showing service details."""
        result = runner.invoke(
            app,
            [
                "services",
                "show",
                "Plex",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Service: Plex" in result.stdout
        assert "href=" in result.stdout


class TestServicesUpdateCommand:
    """Tests for the services update command."""

    def test_services_update_href(self, sample_services_file: Path) -> None:
        """Test updating service href."""
        result = runner.invoke(
            app,
            [
                "services",
                "update",
                "Plex",
                "--href",
                "http://plex-new.local:32400",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated service 'Plex'" in result.stdout

    def test_services_update_icon(self, sample_services_file: Path) -> None:
        """Test updating service icon."""
        result = runner.invoke(
            app,
            [
                "services",
                "update",
                "Plex",
                "--icon",
                "mdi:plex-new",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated service 'Plex'" in result.stdout


class TestServicesRenameCommand:
    """Tests for the services rename command."""

    def test_services_rename(self, sample_services_file: Path) -> None:
        """Test renaming a service."""
        result = runner.invoke(
            app,
            [
                "services",
                "rename",
                "Plex",
                "Plex Media",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Renamed service 'Plex' -> 'Plex Media'" in result.stdout


class TestServicesDeleteCommand:
    """Tests for the services delete command."""

    def test_services_delete(self, sample_services_file: Path) -> None:
        """Test deleting a service."""
        result = runner.invoke(
            app,
            [
                "services",
                "delete",
                "Plex",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted service 'Plex'" in result.stdout


class TestServicesMoveCommand:
    """Tests for the services move command."""

    def test_services_move(self, sample_services_file: Path) -> None:
        """Test moving a service between groups."""
        result = runner.invoke(
            app,
            [
                "services",
                "move",
                "Plex",
                "Infrastructure",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Moved service 'Plex' from 'My First Group' -> 'Infrastructure'" in result.stdout


class TestServicesSetFieldCommand:
    """Tests for the services set-field command."""

    def test_services_set_field_simple(self, sample_services_file: Path) -> None:
        """Test setting a simple field."""
        result = runner.invoke(
            app,
            [
                "services",
                "set-field",
                "Proxmox VE",
                "description",
                "Virtualization platform",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Set Proxmox VE.description = Virtualization platform" in result.stdout

    def test_services_set_field_nested(self, sample_services_file: Path) -> None:
        """Test setting a nested field."""
        result = runner.invoke(
            app,
            [
                "services",
                "set-field",
                "Proxmox VE",
                "widget.type",
                "proxmox",
                "--services-file",
                str(sample_services_file),
            ],
        )
        assert result.exit_code == 0
        assert "Set Proxmox VE.widget.type = proxmox" in result.stdout
