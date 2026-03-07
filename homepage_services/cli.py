"""CLI commands for Homepage Services CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from typer import BadParameter, Exit

from homepage_services.utils import (
    DEFAULT_ICONS_DIR,
    DEFAULT_SERVICES_FILE,
    download_png_icon,
    ensure_group,
    find_group_index,
    find_service,
    get_group_services,
    print_group_table,
    print_services,
    read_services_file,
    service_entry_tuple,
    validate_services_file,
    write_services_file,
)
from homepage_services.bookmarks_utils import (
    DEFAULT_BOOKMARKS_FILE,
    bookmark_entry_tuple,
    ensure_bookmark_group,
    find_bookmark,
    find_bookmark_group_index,
    print_bookmarks,
    read_bookmarks_file,
    validate_bookmarks_file,
    write_bookmarks_file,
)
from homepage_services.settings_utils import (
    DEFAULT_SETTINGS_FILE,
    LayoutGroup,
    print_settings,
    read_settings_file,
    Settings,
    validate_settings_file,
    write_settings_file,
)
from homepage_services.docker_utils import (
    DEFAULT_DOCKER_FILE,
    find_docker_instance,
    print_docker_instances,
    read_docker_file,
    validate_docker_file,
    write_docker_file,
)

app = typer.Typer(add_completion=False, no_args_is_help=True)
groups_app = typer.Typer(no_args_is_help=True)
services_app = typer.Typer(no_args_is_help=True)
bookmarks_app = typer.Typer(no_args_is_help=True)
settings_app = typer.Typer(no_args_is_help=True)
docker_app = typer.Typer(no_args_is_help=True)

app.add_typer(groups_app, name="groups")
app.add_typer(services_app, name="services")
app.add_typer(bookmarks_app, name="bookmarks")
app.add_typer(settings_app, name="settings")
app.add_typer(docker_app, name="docker")


# ---------- Root commands ----------


@app.command()
def validate(
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Validate that services.yaml matches the expected structure.

    Args:
        services_file: Path to the services.yaml file to validate.
    """
    errors = validate_services_file(services_file)

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"- {e}")
        raise Exit(code=2)

    print("OK: services.yaml structure looks valid.")


# ---------- Group commands ----------


@groups_app.command("list")
def groups_list(
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """List all groups with service counts.

    Args:
        services_file: Path to the services.yaml file.
    """
    groups = read_services_file(services_file)
    print_group_table(groups)


@groups_app.command("add")
def groups_add(
    name: str = typer.Argument(..., help="Group name"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Add a new group to services.yaml.

    Args:
        name: Name of the group to add.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the group already exists.
    """
    groups = read_services_file(services_file)
    if find_group_index(groups, name) is not None:
        raise BadParameter(f"Group '{name}' already exists.")
    groups.append({name: []})
    write_services_file(services_file, groups)
    print(f"Added group '{name}'.")


@groups_app.command("rename")
def groups_rename(
    old: str = typer.Argument(..., help="Existing group name"),
    new: str = typer.Argument(..., help="New group name"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Rename an existing group.

    Args:
        old: Current name of the group.
        new: New name for the group.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the old group doesn't exist or the new name already exists.
    """
    groups = read_services_file(services_file)
    old_idx = find_group_index(groups, old)
    if old_idx is None:
        raise BadParameter(f"Group '{old}' not found.")
    if find_group_index(groups, new) is not None:
        raise BadParameter(f"Group '{new}' already exists.")
    service_list = groups[old_idx].pop(old)
    groups[old_idx][new] = service_list
    write_services_file(services_file, groups)
    print(f"Renamed group '{old}' -> '{new}'.")


@groups_app.command("delete")
def groups_delete(
    name: str = typer.Argument(..., help="Group name"),
    force: bool = typer.Option(
        False, "--force", help="Delete even if group has services"
    ),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Delete a group from services.yaml.

    Args:
        name: Name of the group to delete.
        force: If True, delete even if the group has services.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the group doesn't exist or has services without --force.
    """
    groups = read_services_file(services_file)
    idx = find_group_index(groups, name)
    if idx is None:
        raise BadParameter(f"Group '{name}' not found.")
    service_list = groups[idx].get(name)
    if isinstance(service_list, list) and service_list and not force:
        raise BadParameter(
            f"Group '{name}' has {len(service_list)} services. Use --force to delete."
        )
    groups.pop(idx)
    write_services_file(services_file, groups)
    print(f"Deleted group '{name}'.")


# ---------- Service commands ----------


@services_app.command("list")
def services_list(
    group: Optional[str] = typer.Option(
        None, help="If set, list only this group"
    ),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """List services, optionally filtered by group.

    Args:
        group: Optional group name to filter by.
        services_file: Path to the services.yaml file.
    """
    groups = read_services_file(services_file)
    print_services(groups, group=group)


@services_app.command("add")
def services_add(
    href: str = typer.Option(
        ..., help="Service URL (href), e.g. http://proxmox.local:8006"
    ),
    group: str = typer.Option(..., help="Group name to add into"),
    name: Optional[str] = typer.Option(
        None, help="Service display name (defaults inferred from href)"
    ),
    icon: Optional[str] = typer.Option(
        None, help="Icon reference (e.g. /icons/proxmox.png or mdi:server)"
    ),
    icon_url: Optional[str] = typer.Option(
        None, help="If set, download PNG into ./icons and set icon=/icons/<file>.png"
    ),
    icons_dir: Path = typer.Option(
        DEFAULT_ICONS_DIR, help="Local icons directory (./icons)"
    ),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Add a new service to a group.

    Args:
        href: Service URL.
        group: Group name to add the service to.
        name: Service display name. Defaults to inferred from href.
        icon: Icon reference (Material Design Icons or local path).
        icon_url: URL to download a PNG icon from.
        icons_dir: Directory to save downloaded icons.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the service name already exists.
    """
    from homepage_services.utils import infer_name_from_href

    groups = read_services_file(services_file)
    service_name = name or infer_name_from_href(href)
    if find_service(groups, service_name) is not None:
        raise BadParameter(
            f"Service '{service_name}' already exists (service names must be unique)."
        )
    idx = ensure_group(groups, group)
    service_list = groups[idx][group]
    icon_ref = icon
    if icon_url:
        filename = download_png_icon(icon_url, icons_dir, service_name)
        icon_ref = f"/icons/{filename}"
    config: dict[str, any] = {"href": href}
    if icon_ref:
        config["icon"] = icon_ref
    service_list.append({service_name: config})
    write_services_file(services_file, groups)
    print(f"Added service '{service_name}' to group '{group}'.")


@services_app.command("show")
def services_show(
    name: str = typer.Argument(..., help="Service name"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Show detailed information about a service.

    Args:
        name: Name of the service to show.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the service is not found.
    """
    groups = read_services_file(services_file)
    found = find_service(groups, name)
    if not found:
        raise BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    svc_name, cfg = service_entry_tuple(entry)  # type: ignore[assignment]
    print(f"Service: {svc_name}")
    print(f"Group: {group_name}")
    for k, v in cfg.items():
        print(f"- {k}: {v}")


@services_app.command("update")
def services_update(
    name: str = typer.Argument(..., help="Service name"),
    href: Optional[str] = typer.Option(None, help="New href"),
    icon: Optional[str] = typer.Option(
        None, help="New icon reference (e.g. /icons/x.png or mdi:...)"
    ),
    icon_url: Optional[str] = typer.Option(
        None, help="Download PNG into ./icons and set icon=/icons/<file>.png"
    ),
    icons_dir: Path = typer.Option(
        DEFAULT_ICONS_DIR, help="Local icons directory (./icons)"
    ),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Update a service's properties.

    Args:
        name: Name of the service to update.
        href: New service URL.
        icon: New icon reference.
        icon_url: URL to download a new PNG icon from.
        icons_dir: Directory to save downloaded icons.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the service is not found.
    """
    groups = read_services_file(services_file)
    found = find_service(groups, name)
    if not found:
        raise BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    t = service_entry_tuple(entry)
    if not t:
        raise BadParameter(
            "Service entry has unexpected format; cannot update safely."
        )
    _, cfg = t
    if href is not None:
        cfg["href"] = href
    if icon_url:
        filename = download_png_icon(icon_url, icons_dir, name)
        cfg["icon"] = f"/icons/{filename}"
    elif icon is not None:
        cfg["icon"] = icon
    write_services_file(services_file, groups)
    print(f"Updated service '{name}'.")


@services_app.command("rename")
def services_rename(
    old: str = typer.Argument(..., help="Existing service name"),
    new: str = typer.Argument(..., help="New service name"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Rename a service.

    Args:
        old: Current name of the service.
        new: New name for the service.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the old service doesn't exist or the new name already exists.
    """
    groups = read_services_file(services_file)
    if find_service(groups, new) is not None:
        raise BadParameter(f"Service '{new}' already exists.")
    found = find_service(groups, old)
    if not found:
        raise BadParameter(f"Service '{old}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    t = service_entry_tuple(entry)
    if not t:
        raise BadParameter(
            "Service entry has unexpected format; cannot rename safely."
        )
    _, cfg = t
    groups[gi][group_name][si] = {new: cfg}
    write_services_file(services_file, groups)
    print(f"Renamed service '{old}' -> '{new}'.")


@services_app.command("delete")
def services_delete(
    name: str = typer.Argument(..., help="Service name"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Delete a service from its group.

    Args:
        name: Name of the service to delete.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the service is not found.
    """
    groups = read_services_file(services_file)
    found = find_service(groups, name)
    if not found:
        raise BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    groups[gi][group_name].pop(si)
    write_services_file(services_file, groups)
    print(f"Deleted service '{name}' (from group '{group_name}').")


@services_app.command("move")
def services_move(
    name: str = typer.Argument(..., help="Service name"),
    to_group: str = typer.Argument(..., help="Destination group"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Move a service from one group to another.

    Args:
        name: Name of the service to move.
        to_group: Name of the destination group.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the service or destination group is not found.
    """
    groups = read_services_file(services_file)
    found = find_service(groups, name)
    if not found:
        raise BadParameter(f"Service '{name}' not found.")
    from_group, from_gi, from_si = found
    entry = groups[from_gi][from_group].pop(from_si)
    to_idx = ensure_group(groups, to_group)
    groups[to_idx][to_group].append(entry)
    write_services_file(services_file, groups)
    print(f"Moved service '{name}' from '{from_group}' -> '{to_group}'.")


@services_app.command("set-field")
def services_set_field(
    name: str = typer.Argument(..., help="Service name"),
    key: str = typer.Argument(
        ..., help="Config key to set (e.g. description, widget.type, server)"
    ),
    value: str = typer.Argument(..., help="String value to set"),
    services_file: Path = typer.Option(
        DEFAULT_SERVICES_FILE, help="Path to services.yaml"
    ),
) -> None:
    """Set an arbitrary field in the service config using dot-notation.

    Example:
        services set-field "Proxmox" "widget.type" "proxmox"

    Args:
        name: Name of the service.
        key: Config key to set (supports dot notation for nested keys).
        value: String value to set.
        services_file: Path to the services.yaml file.

    Raises:
        BadParameter: If the service is not found or the key cannot be set.
    """
    from typing import Any, Dict

    groups = read_services_file(services_file)
    found = find_service(groups, name)
    if not found:
        raise BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    t = service_entry_tuple(entry)
    if not t:
        raise BadParameter(
            "Service entry has unexpected format; cannot edit safely."
        )
    _, cfg = t
    parts = key.split(".")
    cur: Dict[str, Any] = cfg
    for p in parts[:-1]:
        nxt = cur.get(p)
        if nxt is None:
            cur[p] = {}
            nxt = cur[p]
        if not isinstance(nxt, dict):
            raise BadParameter(
                f"Cannot set '{key}': '{p}' is not a dict in existing config."
            )
        cur = nxt
    cur[parts[-1]] = value
    write_services_file(services_file, groups)
    print(f"Set {name}.{key} = {value}")


# ---------- Bookmarks commands ----------


@bookmarks_app.command("validate")
def bookmarks_validate(
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """Validate that bookmarks.yaml matches the expected structure.

    Args:
        bookmarks_file: Path to the bookmarks.yaml file to validate.
    """
    errors = validate_bookmarks_file(bookmarks_file)

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"- {e}")
        raise Exit(code=2)

    print("OK: bookmarks.yaml structure looks valid.")


@bookmarks_app.command("list")
def bookmarks_list(
    group: Optional[str] = typer.Option(
        None, help="If set, list only this group"
    ),
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """List bookmarks, optionally filtered by group.

    Args:
        group: Optional group name to filter by.
        bookmarks_file: Path to the bookmarks.yaml file.
    """
    groups = read_bookmarks_file(bookmarks_file)
    print_bookmarks(groups, group=group)


@bookmarks_app.command("add")
def bookmarks_add(
    url: str = typer.Option(..., help="Bookmark URL (href)"),
    group: str = typer.Option(..., help="Group name to add into"),
    name: Optional[str] = typer.Option(
        None, help="Bookmark display name (defaults to URL hostname)"
    ),
    abbr: Optional[str] = typer.Option(None, help="Abbreviation"),
    icon: Optional[str] = typer.Option(None, help="Icon reference"),
    description: Optional[str] = typer.Option(None, help="Bookmark description"),
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """Add a new bookmark to a group.

    Args:
        url: Bookmark URL.
        group: Group name to add the bookmark to.
        name: Bookmark display name.
        abbr: Abbreviation.
        icon: Icon reference.
        description: Bookmark description.
        bookmarks_file: Path to the bookmarks.yaml file.

    Raises:
        BadParameter: If the bookmark name already exists.
    """
    from homepage_services.utils import infer_name_from_href

    groups = read_bookmarks_file(bookmarks_file)
    bookmark_name = name or infer_name_from_href(url)
    if find_bookmark(groups, bookmark_name) is not None:
        raise BadParameter(
            f"Bookmark '{bookmark_name}' already exists (bookmark names must be unique)."
        )
    idx = ensure_bookmark_group(groups, group)
    bookmark_list = groups[idx][group]
    config: dict[str, any] = {"href": url}
    if abbr:
        config["abbr"] = abbr
    if icon:
        config["icon"] = icon
    if description:
        config["description"] = description
    bookmark_list.append({bookmark_name: config})
    write_bookmarks_file(bookmarks_file, groups)
    print(f"Added bookmark '{bookmark_name}' to group '{group}'.")


@bookmarks_app.command("show")
def bookmarks_show(
    group: str = typer.Argument(..., help="Group name"),
    name: str = typer.Argument(..., help="Bookmark name"),
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """Show detailed information about a bookmark.

    Args:
        group: Group name.
        name: Bookmark name.
        bookmarks_file: Path to the bookmarks.yaml file.

    Raises:
        BadParameter: If the bookmark is not found.
    """
    groups = read_bookmarks_file(bookmarks_file)
    group_idx = find_bookmark_group_index(groups, group)
    if group_idx is None:
        raise BadParameter(f"Group '{group}' not found.")

    bookmark_list = groups[group_idx][group]
    if not isinstance(bookmark_list, list):
        raise BadParameter(f"Group '{group}' is not a list.")

    found = None
    for entry in bookmark_list:
        t = bookmark_entry_tuple(entry)
        if t and t[0] == name:
            found = t
            break

    if not found:
        raise BadParameter(f"Bookmark '{name}' not found in group '{group}'.")

    bookmark_name, cfg = found
    print(f"Bookmark: {bookmark_name}")
    print(f"Group: {group}")
    for k, v in cfg.items():
        print(f"- {k}: {v}")


@bookmarks_app.command("update")
def bookmarks_update(
    group: str = typer.Argument(..., help="Group name"),
    name: str = typer.Argument(..., help="Bookmark name"),
    url: Optional[str] = typer.Option(None, help="New URL"),
    abbr: Optional[str] = typer.Option(None, help="New abbreviation"),
    icon: Optional[str] = typer.Option(None, help="New icon reference"),
    description: Optional[str] = typer.Option(None, help="New description"),
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """Update a bookmark's properties.

    Args:
        group: Group name.
        name: Bookmark name.
        url: New URL.
        abbr: New abbreviation.
        icon: New icon reference.
        description: New description.
        bookmarks_file: Path to the bookmarks.yaml file.

    Raises:
        BadParameter: If the bookmark is not found.
    """
    groups = read_bookmarks_file(bookmarks_file)
    group_idx = find_bookmark_group_index(groups, group)
    if group_idx is None:
        raise BadParameter(f"Group '{group}' not found.")

    bookmark_list = groups[group_idx][group]
    if not isinstance(bookmark_list, list):
        raise BadParameter(f"Group '{group}' is not a list.")

    found = None
    bookmark_idx = None
    for idx, entry in enumerate(bookmark_list):
        t = bookmark_entry_tuple(entry)
        if t and t[0] == name:
            found = t
            bookmark_idx = idx
            break

    if not found or bookmark_idx is None:
        raise BadParameter(f"Bookmark '{name}' not found in group '{group}'.")

    _, cfg = found
    if url is not None:
        cfg["href"] = url
    if abbr is not None:
        cfg["abbr"] = abbr
    if icon is not None:
        cfg["icon"] = icon
    if description is not None:
        cfg["description"] = description

    write_bookmarks_file(bookmarks_file, groups)
    print(f"Updated bookmark '{name}' in group '{group}'.")


@bookmarks_app.command("rename")
def bookmarks_rename(
    group: str = typer.Argument(..., help="Group name"),
    old: str = typer.Argument(..., help="Existing bookmark name"),
    new: str = typer.Argument(..., help="New bookmark name"),
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """Rename a bookmark.

    Args:
        group: Group name.
        old: Current name of the bookmark.
        new: New name for the bookmark.
        bookmarks_file: Path to the bookmarks.yaml file.

    Raises:
        BadParameter: If the bookmark is not found or the new name already exists.
    """
    groups = read_bookmarks_file(bookmarks_file)

    # Check if new name already exists in any group
    if find_bookmark(groups, new) is not None:
        raise BadParameter(f"Bookmark '{new}' already exists.")

    group_idx = find_bookmark_group_index(groups, group)
    if group_idx is None:
        raise BadParameter(f"Group '{group}' not found.")

    bookmark_list = groups[group_idx][group]
    if not isinstance(bookmark_list, list):
        raise BadParameter(f"Group '{group}' is not a list.")

    found = None
    bookmark_idx = None
    for idx, entry in enumerate(bookmark_list):
        t = bookmark_entry_tuple(entry)
        if t and t[0] == old:
            found = t
            bookmark_idx = idx
            break

    if not found or bookmark_idx is None:
        raise BadParameter(f"Bookmark '{old}' not found in group '{group}'.")

    _, cfg = found
    bookmark_list[bookmark_idx] = {new: cfg}
    write_bookmarks_file(bookmarks_file, groups)
    print(f"Renamed bookmark '{old}' -> '{new}' in group '{group}'.")


@bookmarks_app.command("delete")
def bookmarks_delete(
    group: str = typer.Argument(..., help="Group name"),
    name: str = typer.Argument(..., help="Bookmark name"),
    bookmarks_file: Path = typer.Option(
        DEFAULT_BOOKMARKS_FILE, help="Path to bookmarks.yaml"
    ),
) -> None:
    """Delete a bookmark from its group.

    Args:
        group: Group name.
        name: Name of the bookmark to delete.
        bookmarks_file: Path to the bookmarks.yaml file.

    Raises:
        BadParameter: If the bookmark is not found.
    """
    groups = read_bookmarks_file(bookmarks_file)
    group_idx = find_bookmark_group_index(groups, group)
    if group_idx is None:
        raise BadParameter(f"Group '{group}' not found.")

    bookmark_list = groups[group_idx][group]
    if not isinstance(bookmark_list, list):
        raise BadParameter(f"Group '{group}' is not a list.")

    found_idx = None
    for idx, entry in enumerate(bookmark_list):
        t = bookmark_entry_tuple(entry)
        if t and t[0] == name:
            found_idx = idx
            break

    if found_idx is None:
        raise BadParameter(f"Bookmark '{name}' not found in group '{group}'.")

    bookmark_list.pop(found_idx)
    write_bookmarks_file(bookmarks_file, groups)
    print(f"Deleted bookmark '{name}' from group '{group}'.")


# ---------- Settings commands ----------


@settings_app.command("validate")
def settings_validate(
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """Validate that settings.yaml matches the expected structure.

    Args:
        settings_file: Path to the settings.yaml file to validate.
    """
    errors = validate_settings_file(settings_file)

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"- {e}")
        raise Exit(code=2)

    print("OK: settings.yaml structure looks valid.")


@settings_app.command("set")
def settings_set(
    title: Optional[str] = typer.Option(None, help="Set title"),
    theme: Optional[str] = typer.Option(None, help="Set theme"),
    color: Optional[str] = typer.Option(None, help="Set color"),
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """Set global settings.

    Args:
        title: Homepage title.
        theme: Theme (e.g., dark, light).
        color: Color scheme.
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    if title is not None:
        data["title"] = title
    if theme is not None:
        data["theme"] = theme
    if color is not None:
        data["color"] = color
    write_settings_file(settings_file, data)
    print("Settings updated.")


@settings_app.command("get")
def settings_get(
    key: Optional[str] = typer.Argument(None, help="Key to get (title|theme|color)"),
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """Get a setting value.

    Args:
        key: Setting key to get.
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    settings = Settings.from_dict(data)

    if key:
        if key == "title" and settings.title:
            print(settings.title)
        elif key == "theme" and settings.theme:
            print(settings.theme)
        elif key == "color" and settings.color:
            print(settings.color)
        else:
            print(f"Key '{key}' not set or invalid.")
    else:
        print_settings(settings)


@settings_app.command("list")
def settings_list(
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """List all settings.

    Args:
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    settings = Settings.from_dict(data)
    print_settings(settings)


# ---------- Providers commands (sub-command of settings) ----------


providers_app = typer.Typer(no_args_is_help=True)
settings_app.add_typer(providers_app, name="providers")


@providers_app.command("add")
def providers_add(
    service: str = typer.Argument(..., help="Service name (e.g., openweathermap)"),
    key: str = typer.Argument(..., help="API key"),
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """Add a provider with an API key.

    Args:
        service: Service name.
        key: API key.
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    if "providers" not in data:
        data["providers"] = {}
    data["providers"][service] = key
    write_settings_file(settings_file, data)
    print(f"Added provider '{service}'.")


@providers_app.command("list")
def providers_list(
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """List all providers.

    Args:
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    settings = Settings.from_dict(data)

    if not settings.providers:
        print("No providers configured.")
        return

    print("Providers:")
    for provider_name, api_key in settings.providers.items():
        masked_key = api_key[:4] + "..." if len(api_key) > 4 else "***"
        print(f"  {provider_name}: {masked_key}")


@providers_app.command("delete")
def providers_delete(
    service: str = typer.Argument(..., help="Service name to delete"),
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """Delete a provider.

    Args:
        service: Service name.
        settings_file: Path to the settings.yaml file.

    Raises:
        BadParameter: If the provider is not found.
    """
    data = read_settings_file(settings_file)
    if "providers" not in data or service not in data["providers"]:
        raise BadParameter(f"Provider '{service}' not found.")

    del data["providers"][service]
    write_settings_file(settings_file, data)
    print(f"Deleted provider '{service}'.")


# ---------- Layout commands (sub-command of settings) ----------


layout_app = typer.Typer(no_args_is_help=True)
settings_app.add_typer(layout_app, name="layout")


@layout_app.command("set")
def layout_set(
    group: str = typer.Argument(..., help="Group name"),
    style: Optional[str] = typer.Option(None, help="Layout style"),
    columns: Optional[int] = typer.Option(None, help="Number of columns"),
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """Set layout configuration for a group.

    Args:
        group: Group name.
        style: Layout style (e.g., row, column).
        columns: Number of columns.
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    if "layout" not in data:
        data["layout"] = {}
    if group not in data["layout"]:
        data["layout"][group] = {}
    if style is not None:
        data["layout"][group]["style"] = style
    if columns is not None:
        data["layout"][group]["columns"] = columns
    write_settings_file(settings_file, data)
    print(f"Updated layout for group '{group}'.")


@layout_app.command("list")
def layout_list(
    settings_file: Path = typer.Option(
        DEFAULT_SETTINGS_FILE, help="Path to settings.yaml"
    ),
) -> None:
    """List all layout configurations.

    Args:
        settings_file: Path to the settings.yaml file.
    """
    data = read_settings_file(settings_file)
    settings = Settings.from_dict(data)

    if not settings.layout:
        print("No layout configurations found.")
        return

    print("Layout configurations:")
    for group_name, layout in settings.layout.items():
        print(f"  {group_name}:")
        if layout.style:
            print(f"    style: {layout.style}")
        if layout.columns:
            print(f"    columns: {layout.columns}")


# ---------- Docker commands ----------


@docker_app.command("validate")
def docker_validate(
    docker_file: Path = typer.Option(
        DEFAULT_DOCKER_FILE, help="Path to docker.yaml"
    ),
) -> None:
    """Validate that docker.yaml matches the expected structure.

    Args:
        docker_file: Path to the docker.yaml file to validate.
    """
    errors = validate_docker_file(docker_file)

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"- {e}")
        raise Exit(code=2)

    print("OK: docker.yaml structure looks valid.")


@docker_app.command("list")
def docker_list(
    docker_file: Path = typer.Option(
        DEFAULT_DOCKER_FILE, help="Path to docker.yaml"
    ),
) -> None:
    """List all Docker instances.

    Args:
        docker_file: Path to the docker.yaml file.
    """
    data = read_docker_file(docker_file)
    print_docker_instances(data)


@docker_app.command("add")
def docker_add(
    name: str = typer.Argument(..., help="Docker instance name"),
    host: Optional[str] = typer.Option(None, help="Docker host"),
    port: Optional[int] = typer.Option(None, help="Docker port"),
    socket: Optional[str] = typer.Option(None, help="Docker socket path"),
    docker_file: Path = typer.Option(
        DEFAULT_DOCKER_FILE, help="Path to docker.yaml"
    ),
) -> None:
    """Add a new Docker instance.

    Args:
        name: Docker instance name.
        host: Docker host (use with port).
        port: Docker port (use with host).
        socket: Docker socket path (use instead of host+port).
        docker_file: Path to the docker.yaml file.

    Raises:
        BadParameter: If the instance name already exists or invalid configuration.
    """
    data = read_docker_file(docker_file)

    if name in data:
        raise BadParameter(f"Docker instance '{name}' already exists.")

    # Validate configuration
    has_host_port = host is not None and port is not None
    has_socket = socket is not None

    if not (has_host_port or has_socket):
        raise BadParameter(
            "Must specify either --host and --port together, or --socket."
        )

    if has_host_port and has_socket:
        raise BadParameter("Cannot specify both host+port and socket.")

    config: dict[str, any] = {}
    if host:
        config["host"] = host
    if port:
        config["port"] = port
    if socket:
        config["socket"] = socket

    data[name] = config
    write_docker_file(docker_file, data)
    print(f"Added Docker instance '{name}'.")


@docker_app.command("show")
def docker_show(
    name: str = typer.Argument(..., help="Docker instance name"),
    docker_file: Path = typer.Option(
        DEFAULT_DOCKER_FILE, help="Path to docker.yaml"
    ),
) -> None:
    """Show detailed information about a Docker instance.

    Args:
        name: Docker instance name.
        docker_file: Path to the docker.yaml file.

    Raises:
        BadParameter: If the instance is not found.
    """
    data = read_docker_file(docker_file)
    instance_name = find_docker_instance(data, name)

    if not instance_name:
        raise BadParameter(f"Docker instance '{name}' not found.")

    instance_config = data[instance_name]
    print(f"Docker instance: {instance_name}")
    if isinstance(instance_config, dict):
        for key, value in instance_config.items():
            print(f"- {key}: {value}")


@docker_app.command("update")
def docker_update(
    name: str = typer.Argument(..., help="Docker instance name"),
    host: Optional[str] = typer.Option(None, help="New Docker host"),
    port: Optional[int] = typer.Option(None, help="New Docker port"),
    socket: Optional[str] = typer.Option(None, help="New Docker socket path"),
    docker_file: Path = typer.Option(
        DEFAULT_DOCKER_FILE, help="Path to docker.yaml"
    ),
) -> None:
    """Update a Docker instance's configuration.

    Args:
        name: Docker instance name.
        host: New Docker host.
        port: New Docker port.
        socket: New Docker socket path.
        docker_file: Path to the docker.yaml file.

    Raises:
        BadParameter: If the instance is not found or invalid configuration.
    """
    data = read_docker_file(docker_file)
    instance_name = find_docker_instance(data, name)

    if not instance_name:
        raise BadParameter(f"Docker instance '{name}' not found.")

    instance_config = data[instance_name]
    if not isinstance(instance_config, dict):
        raise BadParameter(f"Instance '{name}' has invalid configuration.")

    # Validate updated configuration
    current_has_socket = "socket" in instance_config
    new_has_host_port = host is not None or port is not None
    new_has_socket = socket is not None

    if new_has_host_port and new_has_socket:
        raise BadParameter("Cannot specify both host+port and socket.")

    if current_has_socket and (host or port):
        raise BadParameter(
            "Cannot switch from socket to host+port. Delete and recreate the instance."
        )
    if not current_has_socket and socket:
        raise BadParameter(
            "Cannot switch from host+port to socket. Delete and recreate the instance."
        )

    if host is not None:
        instance_config["host"] = host
    if port is not None:
        instance_config["port"] = port
    if socket is not None:
        instance_config["socket"] = socket

    write_docker_file(docker_file, data)
    print(f"Updated Docker instance '{name}'.")


@docker_app.command("delete")
def docker_delete(
    name: str = typer.Argument(..., help="Docker instance name"),
    docker_file: Path = typer.Option(
        DEFAULT_DOCKER_FILE, help="Path to docker.yaml"
    ),
) -> None:
    """Delete a Docker instance.

    Args:
        name: Docker instance name.
        docker_file: Path to the docker.yaml file.

    Raises:
        BadParameter: If the instance is not found.
    """
    data = read_docker_file(docker_file)
    instance_name = find_docker_instance(data, name)

    if not instance_name:
        raise BadParameter(f"Docker instance '{name}' not found.")

    del data[instance_name]
    write_docker_file(docker_file, data)
    print(f"Deleted Docker instance '{name}'.")


# ---------- Entry point ----------


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
