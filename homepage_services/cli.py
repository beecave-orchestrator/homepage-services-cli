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

app = typer.Typer(add_completion=False, no_args_is_help=True)
groups_app = typer.Typer(no_args_is_help=True)
services_app = typer.Typer(no_args_is_help=True)

app.add_typer(groups_app, name="groups")
app.add_typer(services_app, name="services")


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


# ---------- Entry point ----------


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
