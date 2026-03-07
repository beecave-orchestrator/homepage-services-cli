"""Integration tests for docker CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from homepage_services.cli import app

runner = CliRunner()


class TestDockerValidateCommand:
    """Tests for the docker validate command."""

    def test_validate_valid_file(self, sample_docker_file: Path) -> None:
        """Test validating a valid docker.yaml file."""
        result = runner.invoke(app, ["docker", "validate", "--docker-file", str(sample_docker_file)])
        assert result.exit_code == 0
        assert "OK: docker.yaml structure looks valid" in result.stdout

    def test_validate_invalid_structure(self, tmp_path: Path) -> None:
        """Test validating a file with invalid structure."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("- not a dict\n- list instead")
        result = runner.invoke(app, ["docker", "validate", "--docker-file", str(invalid_file)])
        # Should fail validation (not a dict)
        assert result.exit_code == 2


class TestDockerListCommand:
    """Tests for the docker list command."""

    def test_docker_list(self, sample_docker_file: Path) -> None:
        """Test listing all Docker instances."""
        result = runner.invoke(app, ["docker", "list", "--docker-file", str(sample_docker_file)])
        assert result.exit_code == 0
        assert "my-docker" in result.stdout
        assert "other-docker" in result.stdout
        assert "127.0.0.1:2375" in result.stdout
        assert "/var/run/docker.sock" in result.stdout


class TestDockerAddCommand:
    """Tests for the docker add command."""

    def test_docker_add_host_port(self, sample_docker_file: Path) -> None:
        """Test adding a Docker instance with host and port."""
        result = runner.invoke(
            app,
            [
                "docker",
                "add",
                "test-docker",
                "--host",
                "192.168.1.100",
                "--port",
                "2376",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added Docker instance 'test-docker'" in result.stdout

    def test_docker_add_socket(self, sample_docker_file: Path) -> None:
        """Test adding a Docker instance with socket."""
        result = runner.invoke(
            app,
            [
                "docker",
                "add",
                "socket-docker",
                "--socket",
                "/path/to/docker.sock",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 0
        assert "Added Docker instance 'socket-docker'" in result.stdout

    def test_docker_add_duplicate(self, sample_docker_file: Path) -> None:
        """Test adding a duplicate Docker instance."""
        result = runner.invoke(
            app,
            [
                "docker",
                "add",
                "my-docker",  # Already exists
                "--host",
                "127.0.0.1",
                "--port",
                "2376",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 2
        assert "already exists" in (result.stdout + result.stderr)

    def test_docker_add_invalid_config(self, sample_docker_file: Path) -> None:
        """Test adding with invalid configuration (host without port)."""
        result = runner.invoke(
            app,
            [
                "docker",
                "add",
                "invalid-docker",
                "--host",
                "127.0.0.1",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 2
        assert "Must specify either --host and --port together" in (result.stdout + result.stderr)


class TestDockerShowCommand:
    """Tests for the docker show command."""

    def test_docker_show(self, sample_docker_file: Path) -> None:
        """Test showing Docker instance details."""
        result = runner.invoke(
            app,
            [
                "docker",
                "show",
                "my-docker",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 0
        assert "Docker instance: my-docker" in result.stdout
        assert "host:" in result.stdout
        assert "port:" in result.stdout


class TestDockerUpdateCommand:
    """Tests for the docker update command."""

    def test_docker_update_port(self, sample_docker_file: Path) -> None:
        """Test updating Docker instance port."""
        result = runner.invoke(
            app,
            [
                "docker",
                "update",
                "my-docker",
                "--port",
                "2376",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated Docker instance 'my-docker'" in result.stdout

    def test_docker_update_host(self, sample_docker_file: Path) -> None:
        """Test updating Docker instance host."""
        result = runner.invoke(
            app,
            [
                "docker",
                "update",
                "my-docker",
                "--host",
                "192.168.1.200",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 0
        assert "Updated Docker instance 'my-docker'" in result.stdout

    def test_docker_update_nonexistent(self, sample_docker_file: Path) -> None:
        """Test updating a nonexistent Docker instance."""
        result = runner.invoke(
            app,
            [
                "docker",
                "update",
                "nonexistent",
                "--port",
                "2376",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 2
        assert "not found" in (result.stdout + result.stderr)


class TestDockerDeleteCommand:
    """Tests for the docker delete command."""

    def test_docker_delete(self, sample_docker_file: Path) -> None:
        """Test deleting a Docker instance."""
        result = runner.invoke(
            app,
            [
                "docker",
                "delete",
                "my-docker",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted Docker instance 'my-docker'" in result.stdout

    def test_docker_delete_nonexistent(self, sample_docker_file: Path) -> None:
        """Test deleting a nonexistent Docker instance."""
        result = runner.invoke(
            app,
            [
                "docker",
                "delete",
                "nonexistent",
                "--docker-file",
                str(sample_docker_file),
            ],
        )
        assert result.exit_code == 2
        assert "not found" in (result.stdout + result.stderr)
