"""Tests for Atmoce Cloud API sensor entities."""
from unittest.mock import MagicMock

from custom_components.atmoce.sensor import (
    SENSOR_DESCRIPTIONS,
    AtmoceSensor,
    _device_info,
)
from custom_components.atmoce.const import DOMAIN


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


def test_device_info_uses_site_id():
    info = _device_info(_make_coordinator({}))

    assert (DOMAIN, "123456") in info["identifiers"]
    assert info["manufacturer"] == "Atmoce"
    assert info["model"] == "Cloud API"
