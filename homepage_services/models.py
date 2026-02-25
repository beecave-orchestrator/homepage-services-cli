"""Data models and type definitions for Homepage Services CLI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ServiceConfig:
    """Configuration for a single service."""

    href: str
    icon: Optional[str] = None
    description: Optional[str] = None
    widget: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for YAML serialization.

        Returns:
            Dictionary representation of the service configuration.
        """
        config: Dict[str, Any] = {"href": self.href}
        if self.icon:
            config["icon"] = self.icon
        if self.description:
            config["description"] = self.description
        if self.widget:
            config["widget"] = self.widget
        if self.extra:
            config.update(self.extra)
        return config


@dataclass
class Service:
    """A service entry in the Homepage configuration."""

    name: str
    config: ServiceConfig

    @classmethod
    def from_dict(cls, name: str, config: Dict[str, Any]) -> "Service":
        """Create a Service from a dictionary.

        Args:
            name: Service name.
            config: Service configuration dictionary.

        Returns:
            A new Service instance.
        """
        service_config = ServiceConfig(
            href=config.get("href", ""),
            icon=config.get("icon"),
            description=config.get("description"),
            widget=config.get("widget"),
        )
        # Store any extra fields
        known_keys = {"href", "icon", "description", "widget"}
        extra = {k: v for k, v in config.items() if k not in known_keys}
        if extra:
            service_config.extra = extra

        return cls(name=name, config=service_config)

    def to_entry(self) -> Dict[str, Any]:
        """Convert to a YAML-compatible entry.

        Returns:
            Dictionary with service name as key and config as value.
        """
        return {self.name: self.config.to_dict()}


@dataclass
class Group:
    """A group containing multiple services."""

    name: str
    services: List[Service]

    @classmethod
    def from_dict(cls, name: str, entries: List[Dict[str, Any]]) -> "Group":
        """Create a Group from a dictionary.

        Args:
            name: Group name.
            entries: List of service entries.

        Returns:
            A new Group instance.
        """
        services: List[Service] = []
        for entry in entries:
            if isinstance(entry, dict) and len(entry) == 1:
                svc_name, svc_config = next(iter(entry.items()))
                if isinstance(svc_name, str) and isinstance(svc_config, dict):
                    services.append(Service.from_dict(svc_name, svc_config))
        return cls(name=name, services=services)

    def to_entry(self) -> Dict[str, Any]:
        """Convert to a YAML-compatible entry.

        Returns:
            Dictionary with group name as key and list of services as value.
        """
        return {self.name: [svc.to_entry() for svc in self.services]}


ServiceEntry = Tuple[str, int, int]
"""Type alias for service lookup: (group_name, group_index, service_index)."""
