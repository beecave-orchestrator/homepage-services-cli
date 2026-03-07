"""Unit tests for Homepage Services CLI docker utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from homepage_services.docker_utils import (
    find_docker_instance,
    print_docker_instances,
    read_docker_file,
    validate_docker_file,
    write_docker_file,
)


class TestReadDockerFile:
    """Tests for the read_docker_file function."""

    def test_read_valid_file(self, sample_docker_file: Path) -> None:
        """Test reading a valid docker.yaml file."""
        data = read_docker_file(sample_docker_file)
        assert isinstance(data, dict)
        assert "my-docker" in data
        assert "other-docker" in data

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty docker.yaml file."""
        empty_file = tmp_path / "docker.yaml"
        empty_file.write_text("")
        data = read_docker_file(empty_file)
        assert data == {}

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_docker_file(tmp_path / "nonexistent.yaml")


class TestWriteDockerFile:
    """Tests for the write_docker_file function."""

    def test_write_creates_backup(
        self, sample_docker_file: Path, tmp_path: Path
    ) -> None:
        """Test that writing creates a backup."""
        backup_file = tmp_path / "docker.yaml.bak"
        assert not backup_file.exists()

        data = read_docker_file(sample_docker_file)
        write_docker_file(sample_docker_file, data)

        assert backup_file.exists()

    def test_write_atomic(self, sample_docker_file: Path) -> None:
        """Test that writing is atomic."""
        data = read_docker_file(sample_docker_file)
        write_docker_file(sample_docker_file, data)

        # File should still be valid
        new_data = read_docker_file(sample_docker_file)
        assert new_data == data


class TestFindDockerInstance:
    """Tests for the find_docker_instance function."""

    def test_find_existing_instance(self, sample_docker_file: Path) -> None:
        """Test finding an existing Docker instance."""
        data = read_docker_file(sample_docker_file)
        result = find_docker_instance(data, "my-docker")
        assert result is not None
        assert result == "my-docker"

    def test_find_nonexistent_instance(self, sample_docker_file: Path) -> None:
        """Test finding a nonexistent Docker instance."""
        data = read_docker_file(sample_docker_file)
        result = find_docker_instance(data, "nonexistent")
        assert result is None


class TestValidateDockerFile:
    """Tests for the validate_docker_file function."""

    def test_validate_valid_file(self, sample_docker_file: Path) -> None:
        """Test validating a valid docker.yaml file."""
        errors = validate_docker_file(sample_docker_file)
        assert errors == []

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validating a nonexistent file."""
        errors = validate_docker_file(tmp_path / "nonexistent.yaml")
        assert len(errors) > 0
        assert "not found" in errors[0].lower()

    def test_validate_missing_host_or_socket(self, tmp_path: Path) -> None:
        """Test validating a file with missing host+port or socket."""
        invalid_file = tmp_path / "docker.yaml"
        invalid_file.write_text("my-docker:\n  host: 127.0.0.1")
        errors = validate_docker_file(invalid_file)
        assert any("must have either host+port or socket" in e for e in errors)

    def test_validate_invalid_config(self, tmp_path: Path) -> None:
        """Test validating a file with invalid configuration."""
        invalid_file = tmp_path / "docker.yaml"
        invalid_file.write_text("my-docker: not-a-dict")
        errors = validate_docker_file(invalid_file)
        assert any("must be a dictionary" in e for e in errors)


class TestPrintDockerInstances:
    """Tests for the print_docker_instances function."""

    def test_print_docker_instances(
        self, sample_docker_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing Docker instances."""
        data = read_docker_file(sample_docker_file)
        print_docker_instances(data)
        captured = capsys.readouterr()
        assert "my-docker" in captured.out
        assert "other-docker" in captured.out
        assert "127.0.0.1:2375" in captured.out
        assert "/var/run/docker.sock" in captured.out
