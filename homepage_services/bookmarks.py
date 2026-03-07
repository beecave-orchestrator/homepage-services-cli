"""Data models and operations for Homepage bookmarks.yaml configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BookmarkConfig:
    """Configuration for a single bookmark."""

    href: str
    abbr: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for YAML serialization.

        Returns:
            Dictionary representation of the bookmark configuration.
        """
        config: Dict[str, Any] = {"href": self.href}
        if self.abbr:
            config["abbr"] = self.abbr
        if self.icon:
            config["icon"] = self.icon
        if self.description:
            config["description"] = self.description
        return config


@dataclass
class Bookmark:
    """A bookmark entry in the Homepage configuration."""

    name: str
    config: BookmarkConfig

    @classmethod
    def from_dict(cls, name: str, config: Dict[str, Any]) -> "Bookmark":
        """Create a Bookmark from a dictionary.

        Args:
            name: Bookmark name.
            config: Bookmark configuration dictionary.

        Returns:
            A new Bookmark instance.
        """
        bookmark_config = BookmarkConfig(
            href=config.get("href", ""),
            abbr=config.get("abbr"),
            icon=config.get("icon"),
            description=config.get("description"),
        )
        return cls(name=name, config=bookmark_config)

    def to_entry(self) -> Dict[str, Any]:
        """Convert to a YAML-compatible entry.

        Returns:
            Dictionary with bookmark name as key and config as value.
        """
        return {self.name: self.config.to_dict()}


@dataclass
class BookmarkGroup:
    """A group containing multiple bookmarks."""

    name: str
    bookmarks: List[Bookmark] = field(default_factory=list)

    @classmethod
    def from_dict(cls, name: str, entries: List[Dict[str, Any]]) -> "BookmarkGroup":
        """Create a BookmarkGroup from a dictionary.

        Args:
            name: Group name.
            entries: List of bookmark entries.

        Returns:
            A new BookmarkGroup instance.
        """
        bookmarks: List[Bookmark] = []
        for entry in entries:
            if isinstance(entry, dict) and len(entry) == 1:
                bookmark_name, bookmark_config = next(iter(entry.items()))
                if isinstance(bookmark_name, str) and isinstance(bookmark_config, dict):
                    bookmarks.append(Bookmark.from_dict(bookmark_name, bookmark_config))
        return cls(name=name, bookmarks=bookmarks)

    def to_entry(self) -> Dict[str, Any]:
        """Convert to a YAML-compatible entry.

        Returns:
            Dictionary with group name as key and list of bookmarks as value.
        """
        return {self.name: [bookmark.to_entry() for bookmark in self.bookmarks]}


# Type alias for bookmark lookup
BookmarkEntry = Tuple[str, int, int]
"""Type alias for bookmark lookup: (group_name, group_index, bookmark_index)."""
