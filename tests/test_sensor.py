"""Tests for Atmoce Cloud API sensor entities."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.components.sensor import SensorEntityDescription

from custom_components.atmoce import sensor as sensor_platform
from custom_components.atmoce.const import CONF_ENABLED_SENSORS, DOMAIN
from custom_components.atmoce.sensor import (
    SENSOR_DESCRIPTIONS,
    AtmoceSensor,
    _device_info,
)


def _make_coordinator(data):
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.serial_number = "123456"
    coordinator.battery_model = "Cloud API"
    coordinator.firmware_version = "unknown"
    coordinator.hw_version = 0
    return coordinator


class TestAtmoceSensor:
    def test_returns_cloud_value(self):
        description = next(d for d in SENSOR_DESCRIPTIONS if d.key == "grid_power")
        sensor = AtmoceSensor.__new__(AtmoceSensor)
        sensor.coordinator = _make_coordinator({"grid_power": 500})
        sensor.entity_description = description

        assert sensor.native_value == 500

    def test_missing_cloud_value_is_unavailable(self):
        description = next(d for d in SENSOR_DESCRIPTIONS if d.key == "battery_soc")
        sensor = AtmoceSensor.__new__(AtmoceSensor)
        sensor.coordinator = _make_coordinator({})
        sensor.entity_description = description

        assert sensor.native_value is None

    def test_cloud_source_is_a_supported_sensor(self):
        assert any(d.key == "active_source" for d in SENSOR_DESCRIPTIONS)

    def test_descriptions_are_unique(self):
        keys = [description.key for description in SENSOR_DESCRIPTIONS]
        assert len(keys) == len(set(keys))

    def test_descriptions_include_home_assistant_entity_defaults(self):
        assert all(
            isinstance(description, SensorEntityDescription)
            and description.entity_registry_enabled_default
            for description in SENSOR_DESCRIPTIONS
        )

    @pytest.mark.asyncio
    async def test_platform_setup_only_creates_selected_sensors(self):
        coordinator = _make_coordinator({})
        hass = MagicMock()
        hass.data = {DOMAIN: {"entry_id": coordinator}}
        entry = MagicMock()
        entry.entry_id = "entry_id"
        entry.options = {CONF_ENABLED_SENSORS: ["grid_power", "battery_soc"]}
        entities = []

        def add_entities_callback(new_entities):
            entities.extend(new_entities)

        with patch.object(sensor_platform, "AtmoceSensor", side_effect=lambda _, item: item):
            await sensor_platform.async_setup_entry(hass, entry, add_entities_callback)

        assert [entity.key for entity in entities] == ["grid_power", "battery_soc"]

    @pytest.mark.asyncio
    async def test_platform_setup_defaults_to_all_sensors(self):
        hass = MagicMock()
        hass.data = {DOMAIN: {"entry_id": _make_coordinator({})}}
        entry = MagicMock()
        entry.entry_id = "entry_id"
        entry.options = {}
        entities = []

        with patch.object(sensor_platform, "AtmoceSensor", side_effect=lambda _, item: item):
            await sensor_platform.async_setup_entry(
                hass, entry, lambda new_entities: entities.extend(new_entities)
            )

        assert [entity.key for entity in entities] == [
            description.key for description in SENSOR_DESCRIPTIONS
        ]


def test_device_info_uses_site_id():
    info = _device_info(_make_coordinator({}))

    assert (DOMAIN, "123456") in info["identifiers"]
    assert info["manufacturer"] == "Atmoce"
    assert info["model"] == "Cloud API"
