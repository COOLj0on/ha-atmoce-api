"""Data coordinator for Atmoce Cloud API."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .cloud_client import AtmoceCloudClient, AtmoceCloudError
from .const import (
    CONF_PASSWORD,
    CONF_SITE_ID,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SOURCE_CLOUD,
)

_LOGGER = logging.getLogger(__name__)


class AtmoceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the Atmoce Cloud Open API for gateway data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            config_entry: The config entry for this integration.
        """
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.serial_number = config_entry.data[CONF_SITE_ID]
        self.battery_model = "Cloud API"
        self.firmware_version = "unknown"
        self.hw_version = 0
        self._client = AtmoceCloudClient(
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
        )
        self._connection_errors = 0

    @property
    def active_source(self) -> str:
        """Return the active data source.

        Returns:
            Always returns SOURCE_CLOUD as only supported source.
        """
        return SOURCE_CLOUD

    @property
    def connection_errors(self) -> int:
        """Return the count of connection errors since startup.

        Returns:
            Number of connection errors.
        """
        return self._connection_errors

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest gateway data from Atmoce Cloud API.

        Returns:
            Dictionary with gateway status and energy data.

        Raises:
            UpdateFailed: If data fetch fails.
        """
        try:
            data = await self._client.async_fetch_site_data(self.serial_number)
        except (
            AtmoceCloudError,
            aiohttp.ClientError,
            ConnectionError,
            OSError,
            asyncio.TimeoutError,
        ) as err:
            self._connection_errors += 1
            raise UpdateFailed(f"Atmoce Cloud API unavailable: {err}") from err

        data["active_source"] = SOURCE_CLOUD
        data["connection_errors"] = self._connection_errors
        return data
