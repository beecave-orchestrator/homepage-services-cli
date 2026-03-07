"""Utility functions for settings.yaml operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ruamel.yaml import YAML

from homepage_services.settings import Settings, LayoutGroup

# YAML configuration
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


# Default paths
DEFAULT_SETTINGS_FILE = Path("settings.yaml")


def read_settings_file(path: Path) -> Dict[str, Any]:
    """Read and parse a settings.yaml file.

    Args:
        path: Path to the settings.yaml file.

    Returns:
        Parsed YAML data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        return {}

    return data


def write_settings_file(path: Path, data: Dict[str, Any]) -> None:
    """Write data to a settings.yaml file with backup.

    Args:
        path: Path to the settings.yaml file.
        data: Data to write.

    Raises:
        OSError: If file operations fail.
    """
    import shutil

    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)

    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)

    tmp.replace(path)


def validate_settings_file(path: Path) -> List[str]:
    """Validate a settings.yaml file and return a list of errors.

    Args:
        path: Path to the settings.yaml file.

    Returns:
        List of error messages (empty if valid).
    """
    errors: List[str] = []

    try:
        data = read_settings_file(path)
    except FileNotFoundError as e:
        return [str(e)]

    if not isinstance(data, dict):
        errors.append("Top-level YAML must be a dictionary.")
        return errors

    # Validate known top-level keys
    known_keys = {"title", "theme", "color", "layout", "providers"}
    for key in data:
        if key not in known_keys:
            errors.append(f"Unknown top-level key: '{key}'")

    # Validate layout
    if "layout" in data:
        layout = data["layout"]
        if not isinstance(layout, dict):
            errors.append("'layout' must be a dictionary.")
        else:
            for group_name, group_layout in layout.items():
                if not isinstance(group_layout, dict):
                    errors.append(f"Layout group '{group_name}' must be a dictionary.")
                else:
                    for key in group_layout:
                        if key not in {"style", "columns"}:
                            errors.append(
                                f"Unknown layout key '{key}' in group '{group_name}'."
                            )

    # Validate providers
    if "providers" in data:
        providers = data["providers"]
        if not isinstance(providers, dict):
            errors.append("'providers' must be a dictionary.")
        else:
            for provider_name, provider_value in providers.items():
                if not isinstance(provider_value, str):
                    errors.append(
                        f"Provider '{provider_name}' must have a string value (API key)."
                    )

    return errors


def print_settings(settings: Settings) -> None:
    """Print current settings.

    Args:
        settings: Settings object to print.
    """
    print("Settings:")
    if settings.title:
        print(f"  title: {settings.title}")
    if settings.theme:
        print(f"  theme: {settings.theme}")
    if settings.color:
        print(f"  color: {settings.color}")

    if settings.layout:
        print("\nLayout:")
        for group_name, layout in settings.layout.items():
            print(f"  {group_name}:")
            if layout.style:
                print(f"    style: {layout.style}")
            if layout.columns:
                print(f"    columns: {layout.columns}")

    if settings.providers:
        print("\nProviders:")
        for provider_name, api_key in settings.providers.items():
            # Mask API key for security
            masked_key = api_key[:4] + "..." if len(api_key) > 4 else "***"
            print(f"  {provider_name}: {masked_key}")
