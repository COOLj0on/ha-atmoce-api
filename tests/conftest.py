"""Shared fixtures for Atmoce Cloud API tests."""

from unittest.mock import MagicMock

import pytest

from custom_components.atmoce.coordinator import AtmoceCoordinator


@pytest.fixture
def mock_config_entry():
    """Minimal Cloud API config entry."""
    entry = MagicMock()
    entry.entry_id = "entry_id"
    entry.data = {
        "username": "user@example.com",
        "password": "secret",
        "site_id": "123456",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_hass():
    """Minimal Home Assistant instance mock."""
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def coordinator(mock_hass, mock_config_entry):
    """Coordinator with a mocked Cloud client."""
    coord = AtmoceCoordinator(mock_hass, mock_config_entry)
    coord._client = MagicMock()
    return coord
