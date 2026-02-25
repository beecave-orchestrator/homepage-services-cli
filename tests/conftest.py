"""Pytest configuration and fixtures for Homepage Services CLI tests."""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest

# Fixture paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_services_content() -> str:
    """Return a sample services.yaml content.

    Returns:
        YAML content string.
    """
    return """
- My First Group:
    - My First Service:
        href: http://localhost/
        description: Homepage is awesome

    - Plex:
        href: http://plex.local:32400
        icon: mdi:plex

- My Second Group:
    - My Second Service:
        href: http://localhost/
        description: Homepage is the best

- Infrastructure:
    - Proxmox VE:
        href: http://pve.local:8006
        icon: mdi:server
        description: Virtualization platform
        widget:
          type: proxmox
"""


@pytest.fixture
def sample_services_file(
    tmp_path: Path, sample_services_content: str
) -> Generator[Path, None, None]:
    """Create a temporary services.yaml file with sample content.

    Args:
        tmp_path: Temporary directory path.
        sample_services_content: Sample YAML content.

    Yields:
        Path to the temporary services.yaml file.
    """
    services_file = tmp_path / "services.yaml"
    services_file.write_text(sample_services_content)
    yield services_file


@pytest.fixture
def empty_services_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create an empty temporary services.yaml file.

    Args:
        tmp_path: Temporary directory path.

    Yields:
        Path to the empty services.yaml file.
    """
    services_file = tmp_path / "services.yaml"
    services_file.write_text("")
    yield services_file


@pytest.fixture
def sample_png_icon() -> bytes:
    """Return a minimal valid PNG icon.

    Returns:
        PNG file bytes.
    """
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 8  # PNG signature + minimal data


@pytest.fixture
def sample_icon_file(tmp_path: Path, sample_png_icon: bytes) -> Path:
    """Create a temporary PNG icon file.

    Args:
        tmp_path: Temporary directory path.
        sample_png_icon: PNG bytes.

    Returns:
        Path to the temporary PNG file.
    """
    icon_file = tmp_path / "icon.png"
    icon_file.write_bytes(sample_png_icon)
    return icon_file
