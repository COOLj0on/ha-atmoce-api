"""Sensor entities for Atmoce Battery integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AtmoceCoordinator


@dataclass(frozen=True, kw_only=True)
class AtmoceeSensorDescription:
    """Sensor description for Atmoce sensors.

    This dataclass holds the configuration for each sensor entity, providing
    a centralized definition that drives both the entity creation in async_setup_entry
    and the data retrieval in AtmoceSensor.native_value.

    Attributes:
        key: Unique identifier for the sensor (becomes entity ID suffix).
        name: Human-readable display name.
        data_key: Key to retrieve data from coordinator.
        device_class: HA device class for the sensor entity.
        entity_category: HA entity category for filtering in the UI.
        state_class: HA state class (measurement, total, total_increasing).
        native_unit_of_measurement: Unit display string.
        suggested_display_precision: Decimal precision for UI display.
        icon: MDI icon identifier.
        value_map: Optional mapping for status enums to string values.
    """

    key: str
    name: str
    data_key: str
    device_class: str | None = None
    entity_category: str | None = None
    state_class: str | None = None
    native_unit_of_measurement: str | None = None
    suggested_display_precision: int | None = None
    icon: str | None = None
    value_map: dict[int, str] | None = None


SENSOR_DESCRIPTIONS: tuple[AtmoceeSensorDescription, ...] = (
    # ── Grid ──────────────────────────────────────────────────────────────────
    AtmoceeSensorDescription(
        key="grid_voltage",
        data_key="grid_voltage",
        name="Grid Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    AtmoceeSensorDescription(
        key="daily_demand",
        data_key="daily_demand",
        name="Daily Demand",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="total_demand",
        data_key="total_demand",
        name="Total Demand",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="grid_current",
        data_key="grid_current",
        name="Grid Current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="grid_power",
        data_key="grid_power",
        name="Grid Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    AtmoceeSensorDescription(
        key="grid_energy_daily",
        data_key="grid_energy_daily",
        name="Grid Energy Daily",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="grid_energy_total",
        data_key="grid_energy_total",
        name="Grid Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="elec_sales_daily",
        data_key="elec_sales_daily",
        name="Electricity Sold Daily",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="elec_sales_total",
        data_key="elec_sales_total",
        name="Electricity Sold Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    # ── PV ────────────────────────────────────────────────────────────────────
    AtmoceeSensorDescription(
        key="pv_power",
        data_key="pv_power",
        name="PV Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    AtmoceeSensorDescription(
        key="pv_energy_daily",
        data_key="pv_energy_daily",
        name="PV Energy Daily",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="pv_energy_total",
        data_key="pv_energy_total",
        name="PV Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="pv_self_consumption_rate",
        data_key="pv_self_consumption_rate",
        name="PV Self Consumption Rate",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        icon="mdi:solar-power",
    ),
    # ── Battery ───────────────────────────────────────────────────────────────
    AtmoceeSensorDescription(
        key="battery_soc",
        data_key="battery_soc",
        name="Battery SOC",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    AtmoceeSensorDescription(
        key="battery_power",
        data_key="battery_power",
        name="Battery Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    AtmoceeSensorDescription(
        key="battery_status",
        data_key="battery_status",
        name="Battery Status",
        icon="mdi:battery-charging",
        value_map={1: "charging", 2: "discharging", 99: "idle"},
    ),
    AtmoceeSensorDescription(
        key="battery_mode",
        data_key="battery_mode",
        name="Battery Operating Mode",
        icon="mdi:battery-sync",
        value_map={1: "self_consumption", 2: "tou", 10: "remote_control"},
    ),
    AtmoceeSensorDescription(
        key="battery_dispatch_power",
        data_key="battery_dispatch_power",
        name="Battery Dispatch Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    AtmoceeSensorDescription(
        key="battery_charged_daily",
        data_key="battery_charged_daily",
        name="Battery Charged Daily",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="battery_discharged_daily",
        data_key="battery_discharged_daily",
        name="Battery Discharged Daily",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="battery_charged_total",
        data_key="battery_charged_total",
        name="Battery Charged Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="battery_discharged_total",
        data_key="battery_discharged_total",
        name="Battery Discharged Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    AtmoceeSensorDescription(
        key="autonomy_hours",
        data_key="autonomy_hours",
        name="Battery Autonomy",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=1,
        icon="mdi:battery-clock",
    ),
    # ── System ────────────────────────────────────────────────────────────────
    AtmoceeSensorDescription(
        key="station_status",
        data_key="station_status",
        name="Station Status",
        icon="mdi:solar-power-variant",
        value_map={0: "normal", 1: "fault"},
    ),
    AtmoceeSensorDescription(
        key="active_source",
        data_key="active_source",
        name="Active Data Source",
        icon="mdi:connection",
        # About the integration's health, not the energy system's behaviour.
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AtmoceeSensorDescription(
        key="connection_errors",
        data_key="connection_errors",
        name="Connection Errors",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:alert-network",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities for the Atmoce Cloud API.

    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: AtmoceCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AtmoceSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class AtmoceSensor(CoordinatorEntity[AtmoceCoordinator], SensorEntity):
    """A single Atmoce sensor entity."""

    entity_description: AtmoceeSensorDescription  # type: ignore[assignment]
    _attr_has_entity_name = True
    _attr_device_class: SensorDeviceClass | None
    _attr_entity_category: EntityCategory | None
    _attr_state_class: SensorStateClass | None
    _attr_native_unit_of_measurement: str | None
    _attr_suggested_display_precision: int | None
    _attr_icon: str | None

    def __init__(
        self,
        coordinator: AtmoceCoordinator,
        description: AtmoceeSensorDescription,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data coordinator instance.
            description: Sensor entity description.
        """
        super().__init__(coordinator)
        self.entity_description = description
        # Map description fields to entity attributes
        self._attr_device_class = description.device_class  # type: ignore[assignment]
        self._attr_entity_category = description.entity_category  # type: ignore[assignment]
        self._attr_state_class = description.state_class  # type: ignore[assignment]
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_suggested_display_precision = description.suggested_display_precision
        self._attr_icon = description.icon
        # Every sensor key has a matching entry under `entity.sensor` in the
        # translation files, so the name comes from there. The `name` on the
        # description stays as the fallback for a key without a translation.
        self._attr_translation_key = description.key
        self._attr_unique_id = f"{coordinator.serial_number}_{description.key}"
        self._attr_device_info = _device_info(coordinator)

    @property
    def native_value(self) -> Any:
        """Get the current sensor value.

        Returns:
            The native value or None if not available. Maps enum values if
            a value_map is configured for this sensor.
        """
        raw = self.coordinator.data.get(self.entity_description.data_key)
        if raw is None:
            return None
        value_map = self.entity_description.value_map
        if value_map and isinstance(raw, int):
            return value_map.get(raw, str(raw))
        return raw


def _device_info(coordinator: AtmoceCoordinator) -> DeviceInfo:
    """Create device info from coordinator data.

    Args:
        coordinator: Data coordinator instance.

    Returns:
        Device info for the Atmoce battery system.
    """
    return DeviceInfo(
        identifiers={(DOMAIN, coordinator.serial_number)},
        name=f"Atmoce {coordinator.battery_model}",
        manufacturer="Atmoce",
        model=coordinator.battery_model,
        sw_version=coordinator.firmware_version,
        hw_version=str(coordinator.hw_version),
    )
