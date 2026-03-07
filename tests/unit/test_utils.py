"""Unit tests for Homepage Services CLI utilities."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from homepage_services.utils import (
    download_png_icon,
    ensure_group,
    find_group_index,
    find_service,
    get_group_services,
    infer_name_from_href,
    print_group_table,
    print_services,
    read_services_file,
    service_entry_tuple,
    slugify,
    validate_services_file,
    write_services_file,
)


class TestSlugify:
    """Tests for the slugify function."""

    def test_slugify_basic(self) -> None:
        """Test basic slugification."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Test-Service") == "test-service"
        assert slugify("  spaces  ") == "spaces"

    def test_slugify_special_chars(self) -> None:
        """Test slugification with special characters."""
        assert slugify("My Service!!!") == "my-service"
        assert slugify("test@service#name") == "test-service-name"
        assert slugify("123numbers") == "123numbers"

    def test_slugify_empty(self) -> None:
        """Test slugification with empty string."""
        assert slugify("") == "service"
        assert slugify("   ") == "service"


class TestInferNameFromHref:
    """Tests for the infer_name_from_href function."""

    def test_infer_from_url(self) -> None:
        """Test name inference from full URL."""
        assert infer_name_from_href("http://proxmox.local:8006") == "Proxmox"
        assert infer_name_from_href("https://plex.example.com:32400") == "Plex"
        assert infer_name_from_href("http://portainer.local") == "Portainer"

    def test_infer_from_hostname(self) -> None:
        """Test name inference from hostname."""
        assert infer_name_from_href("plex.local") == "Plex"
        assert infer_name_from_href("jellyfin") == "Jellyfin"

    def test_infer_invalid(self) -> None:
        """Test name inference with invalid input."""
        assert infer_name_from_href("") == "Service"
        assert infer_name_from_href("://invalid") == "://invalid"


class TestReadServicesFile:
    """Tests for the read_services_file function."""

    def test_read_valid_file(self, sample_services_file: Path) -> None:
        """Test reading a valid services.yaml file."""
        data = read_services_file(sample_services_file)
        assert isinstance(data, list)
        assert len(data) == 3
        assert "My First Group" in data[0]

    def test_read_empty_file(self, empty_services_file: Path) -> None:
        """Test reading an empty services.yaml file."""
        data = read_services_file(empty_services_file)
        assert data == []

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_services_file(tmp_path / "nonexistent.yaml")

    def test_read_invalid_structure(self, tmp_path: Path) -> None:
        """Test reading a file with invalid structure."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("key: value")  # Not a list
        with pytest.raises(ValueError, match="must be a YAML list"):
            read_services_file(invalid_file)


class TestWriteServicesFile:
    """Tests for the write_services_file function."""

    def test_write_creates_backup(
        self, sample_services_file: Path, tmp_path: Path
    ) -> None:
        """Test that writing creates a backup."""
        backup_file = tmp_path / "services.yaml.bak"
        assert not backup_file.exists()

        data = read_services_file(sample_services_file)
        write_services_file(sample_services_file, data)

        assert backup_file.exists()

    def test_write_atomic(self, sample_services_file: Path) -> None:
        """Test that writing is atomic."""
        data = read_services_file(sample_services_file)
        write_services_file(sample_services_file, data)

        # File should still be valid
        new_data = read_services_file(sample_services_file)
        assert new_data == data


class TestFindGroupIndex:
    """Tests for the find_group_index function."""

    def test_find_existing_group(self, sample_services_file: Path) -> None:
        """Test finding an existing group."""
        data = read_services_file(sample_services_file)
        idx = find_group_index(data, "My First Group")
        assert idx is not None
        assert idx == 0

    def test_find_nonexistent_group(self, sample_services_file: Path) -> None:
        """Test finding a nonexistent group."""
        data = read_services_file(sample_services_file)
        idx = find_group_index(data, "Nonexistent")
        assert idx is None


class TestEnsureGroup:
    """Tests for the ensure_group function."""

    def test_ensure_existing_group(self, sample_services_file: Path) -> None:
        """Test ensuring an existing group returns its index."""
        data = read_services_file(sample_services_file)
        idx = ensure_group(data, "My First Group")
        assert idx == 0

    def test_ensure_new_group(self, sample_services_file: Path) -> None:
        """Test ensuring a new group creates it."""
        data = read_services_file(sample_services_file)
        original_len = len(data)
        idx = ensure_group(data, "New Group")
        assert idx == original_len
        assert len(data) == original_len + 1


class TestFindService:
    """Tests for the find_service function."""

    def test_find_existing_service(self, sample_services_file: Path) -> None:
        """Test finding an existing service."""
        data = read_services_file(sample_services_file)
        result = find_service(data, "Plex")
        assert result is not None
        group_name, gi, si = result
        assert group_name == "My First Group"
        assert gi == 0
        assert si == 1

    def test_find_nonexistent_service(self, sample_services_file: Path) -> None:
        """Test finding a nonexistent service."""
        data = read_services_file(sample_services_file)
        result = find_service(data, "Nonexistent")
        assert result is None


class TestGetGroupServices:
    """Tests for the get_group_services function."""

    def test_get_existing_group_services(
        self, sample_services_file: Path
    ) -> None:
        """Test getting services from an existing group."""
        data = read_services_file(sample_services_file)
        services = get_group_services(data, "My First Group")
        assert isinstance(services, list)
        assert len(services) == 2

    def test_get_nonexistent_group(self, sample_services_file: Path) -> None:
        """Test getting services from a nonexistent group."""
        data = read_services_file(sample_services_file)
        with pytest.raises(ValueError, match="not found"):
            get_group_services(data, "Nonexistent")


class TestServiceEntryTuple:
    """Tests for the service_entry_tuple function."""

    def test_valid_entry(self) -> None:
        """Test extracting a valid service entry."""
        entry = {"My Service": {"href": "http://example.com", "icon": "mdi:test"}}
        result = service_entry_tuple(entry)
        assert result is not None
        name, cfg = result
        assert name == "My Service"
        assert cfg["href"] == "http://example.com"

    def test_invalid_entry_not_dict(self) -> None:
        """Test with non-dict entry."""
        result = service_entry_tuple("not a dict")
        assert result is None

    def test_invalid_entry_multiple_keys(self) -> None:
        """Test with entry having multiple keys."""
        entry = {"Key1": "value1", "Key2": "value2"}
        result = service_entry_tuple(entry)
        assert result is None


class TestDownloadPngIcon:
    """Tests for the download_png_icon function."""

    def test_download_valid_png(
        self, tmp_path: Path, sample_png_icon: bytes, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test downloading a valid PNG icon."""

        def mock_get(url: str, timeout: int) -> object:
            class MockResponse:
                def raise_for_status(self) -> None:
                    pass

            response = MockResponse()
            response.content = sample_png_icon
            return response

        monkeypatch.setattr(requests, "get", mock_get)

        icons_dir = tmp_path / "icons"
        filename = download_png_icon("http://example.com/icon.png", icons_dir, "test")

        assert filename == "test.png"
        assert (icons_dir / filename).exists()

    def test_download_invalid_png(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test downloading an invalid PNG file."""

        def mock_get(url: str, timeout: int) -> object:
            class MockResponse:
                def raise_for_status(self) -> None:
                    pass

            response = MockResponse()
            response.content = b"not a png"
            return response

        monkeypatch.setattr(requests, "get", mock_get)

        icons_dir = tmp_path / "icons"
        with pytest.raises(ValueError, match="does not look like a PNG"):
            download_png_icon("http://example.com/icon.png", icons_dir, "test")


class TestValidateServicesFile:
    """Tests for the validate_services_file function."""

    def test_validate_valid_file(self, sample_services_file: Path) -> None:
        """Test validating a valid services.yaml file."""
        errors = validate_services_file(sample_services_file)
        assert errors == []

    def test_validate_empty_file(self, empty_services_file: Path) -> None:
        """Test validating an empty services.yaml file."""
        errors = validate_services_file(empty_services_file)
        assert errors == []

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validating a nonexistent file."""
        errors = validate_services_file(tmp_path / "nonexistent.yaml")
        assert len(errors) > 0
        assert "not found" in errors[0].lower()


class TestPrintFunctions:
    """Tests for print functions."""

    def test_print_group_table(self, sample_services_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test printing group table."""
        data = read_services_file(sample_services_file)
        print_group_table(data)
        captured = capsys.readouterr()
        assert "My First Group" in captured.out
        assert "services" in captured.out

    def test_print_services(self, sample_services_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test printing services."""
        data = read_services_file(sample_services_file)
        print_services(data)
        captured = capsys.readouterr()
        assert "Plex" in captured.out

    def test_print_services_filtered(
        self, sample_services_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing services filtered by group."""
        data = read_services_file(sample_services_file)
        print_services(data, group="My First Group")
        captured = capsys.readouterr()
        assert "Group: My First Group" in captured.out
        assert "Plex" in captured.out
