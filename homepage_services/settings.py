"""Data models and operations for Homepage settings.yaml configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LayoutGroup:
    """Layout configuration for a specific group."""

    style: Optional[str] = None
    columns: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for YAML serialization.

        Returns:
            Dictionary representation of the layout group.
        """
        config: Dict[str, Any] = {}
        if self.style:
            config["style"] = self.style
        if self.columns:
            config["columns"] = self.columns
        return config

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "LayoutGroup":
        """Create a LayoutGroup from a dictionary.

        Args:
            config: Layout configuration dictionary.

        Returns:
            A new LayoutGroup instance.
        """
        return cls(
            style=config.get("style"),
            columns=config.get("columns"),
        )


@dataclass
class Settings:
    """Global settings for Homepage."""

    title: Optional[str] = None
    theme: Optional[str] = None
    color: Optional[str] = None
    layout: Optional[Dict[str, LayoutGroup]] = field(default_factory=dict)
    providers: Optional[Dict[str, str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for YAML serialization.

        Returns:
            Dictionary representation of the settings.
        """
        config: Dict[str, Any] = {}
        if self.title:
            config["title"] = self.title
        if self.theme:
            config["theme"] = self.theme
        if self.color:
            config["color"] = self.color
        if self.layout:
            layout_dict = {
                group_name: layout.to_dict() for group_name, layout in self.layout.items()
            }
            if layout_dict:
                config["layout"] = layout_dict
        if self.providers:
            config["providers"] = self.providers
        return config

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Settings":
        """Create a Settings from a dictionary.

        Args:
            config: Settings configuration dictionary.

        Returns:
            A new Settings instance.
        """
        layout = None
        if "layout" in config:
            layout_config = config["layout"]
            if isinstance(layout_config, dict):
                layout = {
                    group_name: LayoutGroup.from_dict(group_layout)
                    for group_name, group_layout in layout_config.items()
                    if isinstance(group_layout, dict)
                }

        return cls(
            title=config.get("title"),
            theme=config.get("theme"),
            color=config.get("color"),
            layout=layout,
            providers=config.get("providers"),
        )
