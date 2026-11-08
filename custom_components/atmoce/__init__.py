"""Atmoce Cloud API integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import AtmoceCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]  # type: ignore[list-item]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Atmoce from a Cloud API config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry for the integration.

    Returns:
        True if setup is successful, False otherwise.
    """
    coordinator = AtmoceCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Atmoce config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry to unload.

    Returns:
        True if unload is successful, False otherwise.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options change.

    Args:
        hass: Home Assistant instance.
        entry: Config entry with updated options.
    """
    await hass.config_entries.async_reload(entry.entry_id)
