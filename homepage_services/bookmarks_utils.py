"""Utility functions for bookmarks.yaml operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ruamel.yaml import YAML

from homepage_services.bookmarks import BookmarkEntry, Bookmark

# YAML configuration
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


# Default paths
DEFAULT_BOOKMARKS_FILE = Path("bookmarks.yaml")


def read_bookmarks_file(path: Path) -> List[Dict[str, Any]]:
    """Read and parse a bookmarks.yaml file.

    Args:
        path: Path to the bookmarks.yaml file.

    Returns:
        Parsed YAML data as a list of group dictionaries.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML structure is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Bookmarks file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        return []

    if not isinstance(data, list):
        raise ValueError(f"{path} must be a YAML list (top-level array of groups).")

    return data


def write_bookmarks_file(path: Path, data: List[Dict[str, Any]]) -> None:
    """Write data to a bookmarks.yaml file with backup.

    Args:
        path: Path to the bookmarks.yaml file.
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


def find_bookmark_group_index(
    groups: List[Dict[str, Any]], group_name: str
) -> Optional[int]:
    """Find the index of a bookmark group by name.

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


def ensure_bookmark_group(
    groups: List[Dict[str, Any]], group_name: str
) -> int:
    """Ensure a bookmark group exists, creating it if necessary.

    Args:
        groups: List of group dictionaries.
        group_name: Name of the group.

    Returns:
        Index of the group.

    Raises:
        ValueError: If the group exists but is not a list.
    """
    idx = find_bookmark_group_index(groups, group_name)
    if idx is not None:
        if groups[idx].get(group_name) is None:
            groups[idx][group_name] = []
        if not isinstance(groups[idx][group_name], list):
            raise ValueError(
                f"Bookmark group '{group_name}' is not a list in bookmarks.yaml."
            )
        return idx
    groups.append({group_name: []})
    return len(groups) - 1


def bookmark_entry_tuple(entry: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Extract bookmark name and config from a YAML entry.

    Bookmark entries are typically like:
      - My Bookmark:
          href: ...
          icon: ...
    i.e. dict with single key = bookmark name, value = config dict.

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


def find_bookmark(
    groups: List[Dict[str, Any]], bookmark_name: str
) -> Optional[BookmarkEntry]:
    """Find a bookmark by name across all groups.

    Args:
        groups: List of group dictionaries.
        bookmark_name: Name of the bookmark to find.

    Returns:
        Tuple of (group_name, group_index, bookmark_index) or None if not found.
    """
    for gi, group_obj in enumerate(groups):
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            continue
        group_name = next(iter(group_obj.keys()))
        bookmark_list = group_obj.get(group_name)
        if not isinstance(bookmark_list, list):
            continue
        for bi, entry in enumerate(bookmark_list):
            t = bookmark_entry_tuple(entry)
            if t and t[0] == bookmark_name:
                return group_name, gi, bi
    return None


def validate_bookmarks_file(path: Path) -> List[str]:
    """Validate a bookmarks.yaml file and return a list of errors.

    Args:
        path: Path to the bookmarks.yaml file.

    Returns:
        List of error messages (empty if valid).
    """
    errors: List[str] = []

    try:
        groups = read_bookmarks_file(path)
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
            bookmark_list = group_obj.get(group_name)
            if bookmark_list is None:
                continue
            if not isinstance(bookmark_list, list):
                errors.append(f"Group '{group_name}' does not contain a list.")
                continue
            for j, entry in enumerate(bookmark_list):
                t = bookmark_entry_tuple(entry)
                if not t:
                    errors.append(
                        f"Group '{group_name}' bookmark index {j} is not a single-key dict with config."
                    )
                    continue
                _, cfg = t
                if "href" in cfg and not isinstance(cfg["href"], str):
                    errors.append(
                        f"Group '{group_name}' bookmark index {j} has non-string href."
                    )

    return errors


def print_bookmarks(groups: List[Dict[str, Any]], group: Optional[str] = None) -> None:
    """Print bookmarks, optionally filtered by group.

    Args:
        groups: List of group dictionaries.
        group: Optional group name to filter by.
    """
    if group is not None:
        idx = find_bookmark_group_index(groups, group)
        if idx is None:
            print(f"Group '{group}' not found.")
            return
        bookmark_list = groups[idx].get(group)
        if not isinstance(bookmark_list, list):
            print(f"Group '{group}' is not a list.")
            return
        print(f"Group: {group}")
        for entry in bookmark_list:
            t = bookmark_entry_tuple(entry)
            if not t:
                print(" - <invalid bookmark entry>")
                continue
            name, cfg = t
            href = cfg.get("href", "")
            abbr = cfg.get("abbr", "")
            icon = cfg.get("icon", "")
            desc = cfg.get("description", "")
            info_parts = [f"href={href}"]
            if abbr:
                info_parts.append(f"abbr={abbr}")
            if icon:
                info_parts.append(f"icon={icon}")
            if desc:
                info_parts.append(f"desc={desc}")
            print(f" - {name} | " + " | ".join(info_parts))
        return

    # all groups
    if not groups:
        print("No bookmarks found.")
        return
    for group_obj in groups:
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            print("Group: <invalid group entry>")
            continue
        group_name = next(iter(group_obj.keys()))
        print(f"Group: {group_name}")
        bookmark_list = group_obj.get(group_name)
        if not isinstance(bookmark_list, list) or not bookmark_list:
            print(" (no bookmarks)")
            continue
        for entry in bookmark_list:
            t = bookmark_entry_tuple(entry)
            if not t:
                print(" - <invalid bookmark entry>")
                continue
            name, cfg = t
            href = cfg.get("href", "")
            abbr = cfg.get("abbr", "")
            icon = cfg.get("icon", "")
            desc = cfg.get("description", "")
            info_parts = [f"href={href}"]
            if abbr:
                info_parts.append(f"abbr={abbr}")
            if icon:
                info_parts.append(f"icon={icon}")
            if desc:
                info_parts.append(f"desc={desc}")
            print(f" - {name} | " + " | ".join(info_parts))
