"""Utility functions for docker.yaml operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ruamel.yaml import YAML

from homepage_services.docker import DockerInstance

# YAML configuration
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


# Default paths
DEFAULT_DOCKER_FILE = Path("docker.yaml")


def read_docker_file(path: Path) -> Dict[str, Any]:
    """Read and parse a docker.yaml file.

    Args:
        path: Path to the docker.yaml file.

    Returns:
        Parsed YAML data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Docker file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        return {}

    return data


def write_docker_file(path: Path, data: Dict[str, Any]) -> None:
    """Write data to a docker.yaml file with backup.

    Args:
        path: Path to the docker.yaml file.
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


def find_docker_instance(data: Dict[str, Any], instance_name: str) -> Optional[str]:
    """Find a Docker instance by name.

    Args:
        data: Docker configuration dictionary.
        instance_name: Name of the Docker instance.

    Returns:
        Instance name if found, None otherwise.
    """
    if instance_name in data and isinstance(data[instance_name], dict):
        return instance_name
    return None


def validate_docker_file(path: Path) -> List[str]:
    """Validate a docker.yaml file and return a list of errors.

    Args:
        path: Path to the docker.yaml file.

    Returns:
        List of error messages (empty if valid).
    """
    errors: List[str] = []

    try:
        data = read_docker_file(path)
    except FileNotFoundError as e:
        return [str(e)]

    if not isinstance(data, dict):
        errors.append("Top-level YAML must be a dictionary.")
        return errors

    for instance_name, instance_config in data.items():
        if not isinstance(instance_config, dict):
            errors.append(f"Instance '{instance_name}' must be a dictionary.")
            continue

        # Check that either host/port or socket is defined
        has_host = "host" in instance_config
        has_port = "port" in instance_config
        has_socket = "socket" in instance_config

        if not ((has_host and has_port) or has_socket):
            errors.append(
                f"Instance '{instance_name}' must have either host+port or socket defined."
            )

        # Validate host
        if "host" in instance_config and not isinstance(instance_config["host"], str):
            errors.append(f"Instance '{instance_name}' has non-string host.")

        # Validate port
        if "port" in instance_config and not isinstance(instance_config["port"], int):
            errors.append(f"Instance '{instance_name}' has non-integer port.")

        # Validate socket
        if "socket" in instance_config and not isinstance(instance_config["socket"], str):
            errors.append(f"Instance '{instance_name}' has non-string socket.")

    return errors


def print_docker_instances(data: Dict[str, Any]) -> None:
    """Print all Docker instances.

    Args:
        data: Docker configuration dictionary.
    """
    if not data:
        print("No Docker instances found.")
        return

    for instance_name, instance_config in data.items():
        print(f"Instance: {instance_name}")
        if isinstance(instance_config, dict):
            host = instance_config.get("host", "")
            port = instance_config.get("port", "")
            socket = instance_config.get("socket", "")
            if host and port:
                print(f"  host: {host}:{port}")
            elif socket:
                print(f"  socket: {socket}")
            else:
                print(f"  <invalid configuration>")
        else:
            print(f"  <invalid configuration>")
