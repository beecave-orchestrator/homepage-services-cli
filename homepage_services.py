#!/usr/bin/env python3
"""
Homepage services CLI tool

Manages Homepage `services.yaml`:
- List groups and services
- CRUD for groups and services
- Move services between groups
- Download PNG icons into ./icons and reference them as /icons/<file>.png

Author: elvee
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
import typer
from ruamel.yaml import YAML

app = typer.Typer(add_completion=False, no_args_is_help=True)
groups_app = typer.Typer(no_args_is_help=True)
services_app = typer.Typer(no_args_is_help=True)

app.add_typer(groups_app, name="groups")
app.add_typer(services_app, name="services")

DEFAULT_SERVICES_FILE = Path("services.yaml")
DEFAULT_ICONS_DIR = Path("icons")


# ---------- Helpers / Data model ----------

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "service"


def _infer_name_from_href(href: str) -> str:
    try:
        p = urlparse(href if "://" in href else f"http://{href}")
        host = p.hostname or href
        host = host.split(".")[0]
        return host.capitalize() if host else "Service"
    except Exception:
        return "Service"


def _read_services_file(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    if data is None:
        return []
    if not isinstance(data, list):
        raise typer.BadParameter(f"{path} must be a YAML list (top-level array of groups).")
    return data


def _write_services_file(path: Path, data: List[Dict[str, Any]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
    tmp.replace(path)


def _find_group_index(groups: List[Dict[str, Any]], group_name: str) -> Optional[int]:
    for i, obj in enumerate(groups):
        if isinstance(obj, dict) and group_name in obj:
            return i
    return None


def _ensure_group(groups: List[Dict[str, Any]], group_name: str) -> int:
    idx = _find_group_index(groups, group_name)
    if idx is not None:
        # Ensure list exists
        if groups[idx].get(group_name) is None:
            groups[idx][group_name] = []
        if not isinstance(groups[idx][group_name], list):
            raise typer.BadParameter(f"Group '{group_name}' is not a list in services.yaml.")
        return idx
    groups.append({group_name: []})
    return len(groups) - 1


def _get_group_services(groups: List[Dict[str, Any]], group_name: str) -> List[Any]:
    idx = _find_group_index(groups, group_name)
    if idx is None:
        raise typer.BadParameter(f"Group '{group_name}' not found.")
    services = groups[idx].get(group_name)
    if services is None:
        groups[idx][group_name] = []
    return groups[idx][group_name]
    if not isinstance(services, list):
        raise typer.BadParameter(f"Group '{group_name}' is not a list in services.yaml.")
    return services


def _service_entry_tuple(entry: Any) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Service entries are typically like:
      - My Service:
          href: ...
          icon: ...
    i.e. dict with single key = service name, value = config dict.
    """
    if not isinstance(entry, dict) or len(entry) != 1:
        return None
    (name, cfg), = entry.items()
    if not isinstance(name, str) or not isinstance(cfg, dict):
        return None
    return name, cfg


def _find_service(groups: List[Dict[str, Any]], service_name: str) -> Optional[Tuple[str, int, int]]:
    """Returns (group_name, group_index, service_index) for the first match."""
    for gi, group_obj in enumerate(groups):
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            continue
        group_name = next(iter(group_obj.keys()))
        service_list = group_obj.get(group_name)
        if not isinstance(service_list, list):
            continue
        for si, entry in enumerate(service_list):
            t = _service_entry_tuple(entry)
            if t and t[0] == service_name:
                return group_name, gi, si
    return None


def _download_png_icon(icon_url: str, icons_dir: Path, base_name: str) -> str:
    icons_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{_slugify(base_name)}.png"
    dest = icons_dir / filename
    r = requests.get(icon_url, timeout=30)
    r.raise_for_status()
    data = r.content
    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise typer.BadParameter("Downloaded icon does not look like a PNG (bad signature).")
    dest.write_bytes(data)
    return filename


def _print_group_table(groups: List[Dict[str, Any]]) -> None:
    if not groups:
        typer.echo("No groups found.")
        return
    for group_obj in groups:
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            typer.echo("- <invalid group entry>")
            continue
        group_name = next(iter(group_obj.keys()))
        services = group_obj.get(group_name)
        count = len(services) if isinstance(services, list) else 0
        typer.echo(f"- {group_name} ({count} services)")


def _print_services(groups: List[Dict[str, Any]], group: Optional[str] = None) -> None:
    if group is not None:
        service_list = _get_group_services(groups, group)
        typer.echo(f"Group: {group}")
        for entry in service_list:
            t = _service_entry_tuple(entry)
            if not t:
                typer.echo(" - <invalid service entry>")
                continue
            name, cfg = t
            href = cfg.get("href", "")
            icon = cfg.get("icon", "")
            typer.echo(f" - {name} | href={href} | icon={icon}")
        return

    # all groups
    if not groups:
        typer.echo("No services found.")
        return
    for group_obj in groups:
        if not isinstance(group_obj, dict) or len(group_obj) != 1:
            typer.echo("Group: <invalid group entry>")
            continue
        group_name = next(iter(group_obj.keys()))
        typer.echo(f"Group: {group_name}")
        service_list = group_obj.get(group_name)
        if not isinstance(service_list, list) or not service_list:
            typer.echo(" (no services)")
            continue
        for entry in service_list:
            t = _service_entry_tuple(entry)
            if not t:
                typer.echo(" - <invalid service entry>")
                continue
            name, cfg = t
            href = cfg.get("href", "")
            icon = cfg.get("icon", "")
            typer.echo(f" - {name} | href={href} | icon={icon}")


# ---------- Root commands ----------

@app.command()
def validate(
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    """Validate that services.yaml matches the expected structure."""
    groups = _read_services_file(services_file)
    errors: List[str] = []

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
                t = _service_entry_tuple(entry)
                if not t:
                    errors.append(f"Group '{group_name}' service index {j} is not a single-key dict with config.")
                    continue
                _, cfg = t
                if "href" in cfg and not isinstance(cfg["href"], str):
                    errors.append(f"Group '{group_name}' service index {j} has non-string href.")
                if "icon" in cfg and not isinstance(cfg["icon"], str):
                    errors.append(f"Group '{group_name}' service index {j} has non-string icon.")

    if errors:
        typer.echo("Validation failed:")
        for e in errors:
            typer.echo(f"- {e}")
        raise typer.Exit(code=2)

    typer.echo("OK: services.yaml structure looks valid.")


# ---------- Group commands ----------

@groups_app.command("list")
def groups_list(
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    _print_group_table(groups)


@groups_app.command("add")
def groups_add(
    name: str = typer.Argument(..., help="Group name"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    if _find_group_index(groups, name) is not None:
        raise typer.BadParameter(f"Group '{name}' already exists.")
    groups.append({name: []})
    _write_services_file(services_file, groups)
    typer.echo(f"Added group '{name}'.")


@groups_app.command("rename")
def groups_rename(
    old: str = typer.Argument(..., help="Existing group name"),
    new: str = typer.Argument(..., help="New group name"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    old_idx = _find_group_index(groups, old)
    if old_idx is None:
        raise typer.BadParameter(f"Group '{old}' not found.")
    if _find_group_index(groups, new) is not None:
        raise typer.BadParameter(f"Group '{new}' already exists.")
    service_list = groups[old_idx].pop(old)
    groups[old_idx][new] = service_list
    _write_services_file(services_file, groups)
    typer.echo(f"Renamed group '{old}' -> '{new}'.")


@groups_app.command("delete")
def groups_delete(
    name: str = typer.Argument(..., help="Group name"),
    force: bool = typer.Option(False, "--force", help="Delete even if group has services"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    idx = _find_group_index(groups, name)
    if idx is None:
        raise typer.BadParameter(f"Group '{name}' not found.")
    service_list = groups[idx].get(name)
    if isinstance(service_list, list) and service_list and not force:
        raise typer.BadParameter(f"Group '{name}' has {len(service_list)} services. Use --force to delete.")
    groups.pop(idx)
    _write_services_file(services_file, groups)
    typer.echo(f"Deleted group '{name}'.")


# ---------- Service commands ----------

@services_app.command("list")
def services_list(
    group: Optional[str] = typer.Option(None, help="If set, list only this group"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    _print_services(groups, group=group)


@services_app.command("add")
def services_add(
    href: str = typer.Option(..., help="Service URL (href), e.g. http://proxmox.local:8006"),
    group: str = typer.Option(..., help="Group name to add into"),
    name: Optional[str] = typer.Option(None, help="Service display name (defaults inferred from href)"),
    icon: Optional[str] = typer.Option(None, help="Icon reference (e.g. /icons/proxmox.png or mdi:server)"),
    icon_url: Optional[str] = typer.Option(None, help="If set, download PNG into ./icons and set icon=/icons/<file>.png"),
    icons_dir: Path = typer.Option(DEFAULT_ICONS_DIR, help="Local icons directory (./icons)"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    service_name = name or _infer_name_from_href(href)
    if _find_service(groups, service_name) is not None:
        raise typer.BadParameter(f"Service '{service_name}' already exists (service names must be unique).")
    idx = _ensure_group(groups, group)
    service_list = groups[idx][group]
    icon_ref = icon
    if icon_url:
        filename = _download_png_icon(icon_url, icons_dir, service_name)
        icon_ref = f"/icons/{filename}"
    cfg: Dict[str, Any] = {"href": href}
    if icon_ref:
        cfg["icon"] = icon_ref
    service_list.append({service_name: cfg})
    _write_services_file(services_file, groups)
    typer.echo(f"Added service '{service_name}' to group '{group}'.")


@services_app.command("show")
def services_show(
    name: str = typer.Argument(..., help="Service name"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    found = _find_service(groups, name)
    if not found:
        raise typer.BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    svc_name, cfg = _service_entry_tuple(entry)  # type: ignore[assignment]
    typer.echo(f"Service: {svc_name}")
    typer.echo(f"Group: {group_name}")
    for k, v in cfg.items():
        typer.echo(f"- {k}: {v}")


@services_app.command("update")
def services_update(
    name: str = typer.Argument(..., help="Service name"),
    href: Optional[str] = typer.Option(None, help="New href"),
    icon: Optional[str] = typer.Option(None, help="New icon reference (e.g. /icons/x.png or mdi:...)"),
    icon_url: Optional[str] = typer.Option(None, help="Download PNG into ./icons and set icon=/icons/<file>.png"),
    icons_dir: Path = typer.Option(DEFAULT_ICONS_DIR, help="Local icons directory (./icons)"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    found = _find_service(groups, name)
    if not found:
        raise typer.BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    t = _service_entry_tuple(entry)
    if not t:
        raise typer.BadParameter("Service entry has unexpected format; cannot update safely.")
    _, cfg = t
    if href is not None:
        cfg["href"] = href
    if icon_url:
        filename = _download_png_icon(icon_url, icons_dir, name)
        cfg["icon"] = f"/icons/{filename}"
    elif icon is not None:
        cfg["icon"] = icon
    _write_services_file(services_file, groups)
    typer.echo(f"Updated service '{name}'.")


@services_app.command("rename")
def services_rename(
    old: str = typer.Argument(..., help="Existing service name"),
    new: str = typer.Argument(..., help="New service name"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    if _find_service(groups, new) is not None:
        raise typer.BadParameter(f"Service '{new}' already exists.")
    found = _find_service(groups, old)
    if not found:
        raise typer.BadParameter(f"Service '{old}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    t = _service_entry_tuple(entry)
    if not t:
        raise typer.BadParameter("Service entry has unexpected format; cannot rename safely.")
    _, cfg = t
    groups[gi][group_name][si] = {new: cfg}
    _write_services_file(services_file, groups)
    typer.echo(f"Renamed service '{old}' -> '{new}'.")


@services_app.command("delete")
def services_delete(
    name: str = typer.Argument(..., help="Service name"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    found = _find_service(groups, name)
    if not found:
        raise typer.BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    groups[gi][group_name].pop(si)
    _write_services_file(services_file, groups)
    typer.echo(f"Deleted service '{name}' (from group '{group_name}').")


@services_app.command("move")
def services_move(
    name: str = typer.Argument(..., help="Service name"),
    to_group: str = typer.Argument(..., help="Destination group"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    groups = _read_services_file(services_file)
    found = _find_service(groups, name)
    if not found:
        raise typer.BadParameter(f"Service '{name}' not found.")
    from_group, from_gi, from_si = found
    entry = groups[from_gi][from_group].pop(from_si)
    to_idx = _ensure_group(groups, to_group)
    groups[to_idx][to_group].append(entry)
    _write_services_file(services_file, groups)
    typer.echo(f"Moved service '{name}' from '{from_group}' -> '{to_group}'.")


@services_app.command("set-field")
def services_set_field(
    name: str = typer.Argument(..., help="Service name"),
    key: str = typer.Argument(..., help="Config key to set (e.g. description, widget.type, server)"),
    value: str = typer.Argument(..., help="String value to set"),
    services_file: Path = typer.Option(DEFAULT_SERVICES_FILE, help="Path to services.yaml"),
) -> None:
    """Set an arbitrary field in the service config using dot-notation.

    Example:
        services set-field "Proxmox" "widget.type" "proxmox"
    """
    groups = _read_services_file(services_file)
    found = _find_service(groups, name)
    if not found:
        raise typer.BadParameter(f"Service '{name}' not found.")
    group_name, gi, si = found
    entry = groups[gi][group_name][si]
    t = _service_entry_tuple(entry)
    if not t:
        raise typer.BadParameter("Service entry has unexpected format; cannot edit safely.")
    _, cfg = t
    parts = key.split(".")
    cur: Dict[str, Any] = cfg
    for p in parts[:-1]:
        nxt = cur.get(p)
        if nxt is None:
            cur[p] = {}
            nxt = cur[p]
        if not isinstance(nxt, dict):
            raise typer.BadParameter(f"Cannot set '{key}': '{p}' is not a dict in existing config.")
        cur = nxt
    cur[parts[-1]] = value
    _write_services_file(services_file, groups)
    typer.echo(f"Set {name}.{key} = {value}")


# ---------- Entry point ----------

def main() -> None:
    app()


if __name__ == "__main__":
    main()
