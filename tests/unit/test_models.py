"""Unit tests for Homepage Services CLI models."""

from __future__ import annotations

import pytest

from homepage_services.models import Group, Service, ServiceConfig


class TestServiceConfig:
    """Tests for the ServiceConfig dataclass."""

    def test_service_config_basic(self) -> None:
        """Test creating a basic service config."""
        config = ServiceConfig(href="http://example.com")
        assert config.href == "http://example.com"
        assert config.icon is None
        assert config.description is None
        assert config.widget is None

    def test_service_config_full(self) -> None:
        """Test creating a full service config."""
        config = ServiceConfig(
            href="http://example.com",
            icon="mdi:test",
            description="Test service",
            widget={"type": "custom"},
        )
        assert config.href == "http://example.com"
        assert config.icon == "mdi:test"
        assert config.description == "Test service"
        assert config.widget == {"type": "custom"}

    def test_to_dict_basic(self) -> None:
        """Test converting basic config to dict."""
        config = ServiceConfig(href="http://example.com")
        result = config.to_dict()
        assert result == {"href": "http://example.com"}

    def test_to_dict_full(self) -> None:
        """Test converting full config to dict."""
        config = ServiceConfig(
            href="http://example.com",
            icon="mdi:test",
            description="Test",
            widget={"type": "custom"},
        )
        result = config.to_dict()
        assert result == {
            "href": "http://example.com",
            "icon": "mdi:test",
            "description": "Test",
            "widget": {"type": "custom"},
        }

    def test_to_dict_with_extra(self) -> None:
        """Test converting config with extra fields to dict."""
        config = ServiceConfig(
            href="http://example.com",
            extra={"server": "example.com", "port": "8080"},
        )
        result = config.to_dict()
        assert result == {
            "href": "http://example.com",
            "server": "example.com",
            "port": "8080",
        }


class TestService:
    """Tests for the Service dataclass."""

    def test_service_basic(self) -> None:
        """Test creating a basic service."""
        config = ServiceConfig(href="http://example.com")
        service = Service(name="Test", config=config)
        assert service.name == "Test"
        assert service.config.href == "http://example.com"

    def test_from_dict_basic(self) -> None:
        """Test creating a service from a dict."""
        config_dict = {"href": "http://example.com"}
        service = Service.from_dict("Test", config_dict)
        assert service.name == "Test"
        assert service.config.href == "http://example.com"
        assert service.config.icon is None

    def test_from_dict_full(self) -> None:
        """Test creating a service from a full dict."""
        config_dict = {
            "href": "http://example.com",
            "icon": "mdi:test",
            "description": "Test",
            "widget": {"type": "custom"},
        }
        service = Service.from_dict("Test", config_dict)
        assert service.name == "Test"
        assert service.config.href == "http://example.com"
        assert service.config.icon == "mdi:test"
        assert service.config.description == "Test"
        assert service.config.widget == {"type": "custom"}

    def test_from_dict_with_extra(self) -> None:
        """Test creating a service from a dict with extra fields."""
        config_dict = {
            "href": "http://example.com",
            "server": "example.com",
            "custom_field": "value",
        }
        service = Service.from_dict("Test", config_dict)
        assert service.config.extra is not None
        assert service.config.extra["server"] == "example.com"
        assert service.config.extra["custom_field"] == "value"

    def test_to_entry(self) -> None:
        """Test converting service to YAML entry."""
        config = ServiceConfig(href="http://example.com", icon="mdi:test")
        service = Service(name="Test", config=config)
        entry = service.to_entry()
        assert entry == {
            "Test": {"href": "http://example.com", "icon": "mdi:test"}
        }

    def test_from_dict_invalid_name(self) -> None:
        """Test creating a service with invalid name type."""
        config_dict = {"href": "http://example.com"}
        # This should not raise an error but result in a different service
        service = Service.from_dict("123", config_dict)
        assert service.name == "123"


class TestGroup:
    """Tests for the Group dataclass."""

    def test_group_basic(self) -> None:
        """Test creating a basic group."""
        group = Group(name="Test Group", services=[])
        assert group.name == "Test Group"
        assert group.services == []

    def test_group_with_services(self) -> None:
        """Test creating a group with services."""
        services = [
            Service(
                name="Service1",
                config=ServiceConfig(href="http://example1.com"),
            ),
            Service(
                name="Service2",
                config=ServiceConfig(href="http://example2.com"),
            ),
        ]
        group = Group(name="Test Group", services=services)
        assert group.name == "Test Group"
        assert len(group.services) == 2
        assert group.services[0].name == "Service1"
        assert group.services[1].name == "Service2"

    def test_from_dict_empty(self) -> None:
        """Test creating a group from an empty dict."""
        group = Group.from_dict("Test Group", [])
        assert group.name == "Test Group"
        assert group.services == []

    def test_from_dict_with_services(self) -> None:
        """Test creating a group from a dict with services."""
        entries = [
            {"Service1": {"href": "http://example1.com"}},
            {"Service2": {"href": "http://example2.com", "icon": "mdi:test"}},
        ]
        group = Group.from_dict("Test Group", entries)
        assert group.name == "Test Group"
        assert len(group.services) == 2
        assert group.services[0].name == "Service1"
        assert group.services[1].name == "Service2"
        assert group.services[1].config.icon == "mdi:test"

    def test_from_dict_invalid_entries(self) -> None:
        """Test creating a group from a dict with invalid entries."""
        entries = [
            {"Service1": {"href": "http://example1.com"}},
            "invalid entry",  # Should be skipped
            {"Service2": {"href": "http://example2.com"}},
        ]
        group = Group.from_dict("Test Group", entries)
        assert len(group.services) == 2  # Invalid entries skipped

    def test_to_entry(self) -> None:
        """Test converting group to YAML entry."""
        services = [
            Service(
                name="Service1",
                config=ServiceConfig(href="http://example1.com"),
            ),
        ]
        group = Group(name="Test Group", services=services)
        entry = group.to_entry()
        assert entry == {
            "Test Group": [{"Service1": {"href": "http://example1.com"}}]
        }
