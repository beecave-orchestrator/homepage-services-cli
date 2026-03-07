"""Data models and operations for Homepage docker.yaml configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DockerInstance:
    """A Docker instance configuration."""

    name: str
    host: Optional[str] = None
    port: Optional[int] = None
    socket: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for YAML serialization.

        Returns:
            Dictionary representation of the Docker instance.
        """
        config: Dict[str, Any] = {}
        if self.host:
            config["host"] = self.host
        if self.port:
            config["port"] = self.port
        if self.socket:
            config["socket"] = self.socket
        return config

    @classmethod
    def from_dict(cls, name: str, config: Dict[str, Any]) -> "DockerInstance":
        """Create a DockerInstance from a dictionary.

        Args:
            name: Docker instance name.
            config: Docker configuration dictionary.

        Returns:
            A new DockerInstance instance.
        """
        return cls(
            name=name,
            host=config.get("host"),
            port=config.get("port"),
            socket=config.get("socket"),
        )
