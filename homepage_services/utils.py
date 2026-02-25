"""Utility functions for YAML I/O, validation, and icon download."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from ruamel.yaml import YAML

from homepage_services.models import ServiceEntry, Service

# Default paths
DEFAULT_SERVICES_FILE = Path("services.yaml")
DEFAULT_ICONS_DIR = Path("icons")

# YAML configuration
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


def slugify(value: str) -> str:
    """Convert a string to a URL-safe slug.

    Args:
        value: The string to slugify.

    Returns:
        A slugified string.
    """
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "service"


def infer_name_from_href(href: str) -> str:
    """Infer a service name from a URL hostname.

    Args:
        href: Service URL.

    Returns:
        Inferred service name.
    """
    try:
        p = urlparse(href if "://" in href else f"http://{href}")
        host = p.hostname or href
        host = host.split(".")[0]
        return host.capitalize() if host else "Service"
    except Exception:
        return "Service"


def read_services_file(path: Path) -> List[Dict[str, Any]]:
    """Read and parse a services.yaml file.

    Args:
        path: Path to the services.yaml file.

    Returns:
        Parsed YAML data as a list of group dictionaries.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML structure is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Services file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        return []

    if not isinstance(data, list):
        raise ValueError(f"{path} must be a YAML list (top-level array of groups).")

    return data


def write_services_file(path: Path, data: List[Dict[str, Any]]) -> None:
    """Write data to a services.yaml file with backup.

    Args:
        path: Path to the services.yaml file.
        data: Data to write.

    Raises:
        OSError: If file operations fail.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)

    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)

    tmp.replace(path)


def find_group_index(groups: List[Dict[str, Any]], group_name: str) -> Optional[int]:
    """Find the index of a group by name.

    Args:
        groups: List of group dictionaries.
        group_name: Name of the group to find.

    Returns:
        Index of the group, or None if not found.
    """
    for i, obj in enumerate(groups):
        if isinstance(obj, dict) and group_name in obj:
            return i
    return None


def ensure_group(groups: List[Dict[str, Any]], group_name: str) -> int:
    """Ensure a group exists, creating it if necessary.

    Args:
        groups: List of group dictionaries.
        group_name: Name of the group.

    Returns:
        Index of the group.

    Raises:
        ValueError: If the group exists but is not a list.
    """
    idx = find_group_index(groups, group_name)
    if idx is not None:
        if groups[idx].get(group_name) is None:
            groups[idx][group_name] = []
        if not isinstance(groups[idx][group_name], list):
            raise ValueError(f"Group '{group_name}' is not a list in services.yaml.")
        return idx
    groups.append({group_name: []})
    return len(groups) - 1


def get_group_services(groups: List[Dict[str, Any]], group_name: str) -> List[Any]:
    """Get the list of services for a group.

    Args:
        groups: List of group dictionaries.
        group_name: Name of the group.

    Returns:
        List of service entries.

    Raises:
        ValueError: If the group is not found or is not a list.
    """
    idx = find_group_index(groups, group_name)
    if idx is None:
        raise ValueError(f"Group '{group_name}' not found.")
    services = groups[idx].get(group_name)
    if services is None:
        groups[idx][group_name] = []
    return groups[idx][group_name]
    if not isinstance(services, list):
        raise ValueError(f"Group '{group_name}' is not a list in services.yaml.")
    return services


def service_entry_tuple(entry: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Extract service name and config from a YAML entry.

    Service entries are typically like:
      - My Service:
          href: ...
          icon: ...
    i.e. dict with single key = service name, value = config dict.

    Args:
        entry: A YAML entry (usually a dict).

    Returns:
        Tuple of (name, config) or None if invalid.
    """
    if not isinstance(entry, dict) or len(entry) != 1:
        return None
    (name, cfg), = entry.items()
    if not isinstance(name, str) or not isinstance(cfg, dict):
        return None
    return name, cfg


def find_service(
    groups: List[Dict[str, Any]], service_name: str
) -> Optional[ServiceEntry]:
    """Find a service by name across all groups.

    Args:
        groups: List of group dictionaries.
        service_name: Name of the service to find.

    Returns:
        Tuple of (group_name, group_index, service_index) or None if not found.
    """
    for gi, group_obj in enumerate(groups):
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            continue
        group_name = next(iter(group_obj.keys()))
        service_list = group_obj.get(group_name)
        if not isinstance(service_list, list):
            continue
        for si, entry in enumerate(service_list):
            t = service_entry_tuple(entry)
            if t and t[0] == service_name:
                return group_name, gi, si
    return None


def download_png_icon(icon_url: str, icons_dir: Path, base_name: str) -> str:
    """Download a PNG icon from a URL.

    Args:
        icon_url: URL of the PNG icon.
        icons_dir: Directory to save the icon.
        base_name: Base name for the file (will be slugified).

    Returns:
        Filename of the downloaded icon.

    Raises:
        requests.RequestException: If download fails.
        ValueError: If the downloaded file is not a valid PNG.
    """
    icons_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(base_name)}.png"
    dest = icons_dir / filename

    r = requests.get(icon_url, timeout=30)
    r.raise_for_status()
    data = r.content

    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Downloaded icon does not look like a PNG (bad signature).")

    dest.write_bytes(data)
    return filename


def print_group_table(groups: List[Dict[str, Any]]) -> None:
    """Print a table of groups with service counts.

    Args:
        groups: List of group dictionaries.
    """
    if not groups:
        print("No groups found.")
        return
    for group_obj in groups:
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            print("- <invalid group entry>")
            continue
        group_name = next(iter(group_obj.keys()))
        services = group_obj.get(group_name)
        count = len(services) if isinstance(services, list) else 0
        print(f"- {group_name} ({count} services)")


def print_services(groups: List[Dict[str, Any]], group: Optional[str] = None) -> None:
    """Print services, optionally filtered by group.

    Args:
        groups: List of group dictionaries.
        group: Optional group name to filter by.
    """
    if group is not None:
        service_list = get_group_services(groups, group)
        print(f"Group: {group}")
        for entry in service_list:
            t = service_entry_tuple(entry)
            if not t:
                print(" - <invalid service entry>")
                continue
            name, cfg = t
            href = cfg.get("href", "")
            icon = cfg.get("icon", "")
            print(f" - {name} | href={href} | icon={icon}")
        return

    # all groups
    if not groups:
        print("No services found.")
        return
    for group_obj in groups:
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            print("Group: <invalid group entry>")
            continue
        group_name = next(iter(group_obj.keys()))
        print(f"Group: {group_name}")
        service_list = group_obj.get(group_name)
        if not isinstance(service_list, list) or not service_list:
            print(" (no services)")
            continue
        for entry in service_list:
            t = service_entry_tuple(entry)
            if not t:
                print(" - <invalid service entry>")
                continue
            name, cfg = t
            href = cfg.get("href", "")
            icon = cfg.get("icon", "")
            print(f" - {name} | href={href} | icon={icon}")


def validate_services_file(path: Path) -> List[str]:
    """Validate a services.yaml file and return a list of errors.

    Args:
        path: Path to the services.yaml file.

    Returns:
        List of error messages (empty if valid).
    """
    errors: List[str] = []

    try:
        groups = read_services_file(path)
    except (FileNotFoundError, ValueError) as e:
        return [str(e)]

    if not isinstance(groups, list):
        errors.append("Top-level YAML is not a list.")
    else:
        for i, group_obj in enumerate(groups):
            if not isinstance(group_obj, dict) or len(group_obj) != 1:
                errors.append(f"Group index {i} is not a single-key dict.")
                continue
            group_name = next(iter(group_obj.keys()))
            service_list = group_obj.get(group_name)
            if service_list is None:
                continue
            if not isinstance(service_list, list):
                errors.append(f"Group '{group_name}' does not contain a list.")
                continue
            for j, entry in enumerate(service_list):
                t = service_entry_tuple(entry)
                if not t:
                    errors.append(
                        f"Group '{group_name}' service index {j} is not a single-key dict with config."
                    )
                    continue
                _, cfg = t
                if "href" in cfg and not isinstance(cfg["href"], str):
                    errors.append(
                        f"Group '{group_name}' service index {j} has non-string href."
                    )
                if "icon" in cfg and not isinstance(cfg["icon"], str):
                    errors.append(
                        f"Group '{group_name}' service index {j} has non-string icon."
                    )

    return errors
