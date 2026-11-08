"""Atmoce Cloud API client."""

from __future__ import annotations

import base64
import logging
from typing import Any

import aiohttp

from .const import WEB_BASE_URL

_LOGGER = logging.getLogger(__name__)
_DEVICE_DETAIL_URL = f"{WEB_BASE_URL}/energy-manage/webDeviceMonitor/getWebSingleDeviceDetailData"
_LOGIN_URL = f"{WEB_BASE_URL}/permission-auth/api/login"


class AtmoceCloudError(Exception):
    """The Cloud Open API rejected the request or returned no usable data."""


class AtmoceCloudAuthError(AtmoceCloudError):
    """Authentication against the Cloud Open API failed."""


class AtmoceCloudClient:
    """Minimal asynchronous client for the Atmoce Cloud API."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the Cloud API client.

        Args:
            username: API username or email.
            password: API password (will be base64-encoded).
        """
        self._username = username
        self._password = password
        self._token: str | None = None
        self._prefix = "Bearer "

    async def _async_authenticate(self) -> None:
        """Authenticate with the Cloud API endpoint.

        Raises:
            AtmoceCloudAuthError: If authentication fails.
        """
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                _LOGIN_URL,
                json={
                    "username": self._username,
                    "encrypted": True,
                    "password": base64.b64encode(self._password.encode("utf-8")).decode("ascii"),
                    "appType": "web",
                },
            )
            status = response.status
            data = await response.json()
        login_data = data.get("data") or {}
        token = login_data.get("token") or login_data.get("access_token")
        if status >= 400 or data.get("code") != 200 or not token:
            raise AtmoceCloudAuthError(
                f"Cloud auth failed (HTTP {status}): {data.get('msg') or data.get('code')}"
            )
        self._token = token
        self._prefix = login_data.get("prefix") or "Bearer "

    async def async_fetch_site_data(self, device_id: int | str) -> dict[str, Any]:
        """Fetch the latest detail data for an ATMOCE gateway.

        Automatically refreshes the token if the request fails.

        Args:
            device_id: The gateway device ID (integer or string).

        Returns:
            Dictionary containing gateway status and energy data.

        Raises:
            AtmoceCloudError: If fetching data fails after retry.
        """
        try:
            return await self._async_fetch_once(device_id)
        except AtmoceCloudError:
            if self._token is None:
                raise
            _LOGGER.debug("Cloud request rejected; refreshing the API token")
            self._token = None
            return await self._async_fetch_once(device_id)

    async def _async_fetch_once(self, device_id: int | str) -> dict[str, Any]:
        """Fetch data from the Cloud API once.

        Args:
            device_id: The gateway device ID.

        Returns:
            Dictionary of gateway status and energy data.

        Raises:
            AtmoceCloudError: If the API request fails.
        """
        if not self._token:
            await self._async_authenticate()

        headers = {"Authorization": f"{self._prefix}{self._token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            response = await session.post(
                _DEVICE_DETAIL_URL,
                json={
                    "typeCode": "gateway",
                    "deviceId": int(device_id),
                    "refreshRealtime": False,
                },
            )
            status = response.status
            payload = await response.json()

        if status >= 400 or payload.get("code") != 200 or not payload.get("success"):
            raise AtmoceCloudError(
                f"Cloud data fetch failed (HTTP {status}): "
                f"{payload.get('msg') or payload.get('code')}"
            )

        device = payload.get("data") or {}
        values = device.get("dataValues") or {}
        return {
            "grid_power": device.get("gridPower", values.get("grid_power")),
            "pv_power": device.get("generationPower", values.get("generation_power")),
            "pv_energy_daily": device.get("dailyGeneration", values.get("daily_generation")),
            "pv_energy_total": device.get("totalGeneration", values.get("total_generation")),
            "grid_energy_daily": values.get("daily_consumption"),
            "grid_energy_total": values.get("total_consumption"),
            "elec_sales_daily": device.get("dailySupply", values.get("daily_supply")),
            "elec_sales_total": device.get("totalSupply", values.get("total_supply")),
            "battery_soc": None,
            "battery_power": device.get("storagePower"),
            "battery_status": None,
            "grid_voltage": device.get("gridVoltage", device.get("gridU")),
            "grid_current": device.get("gridCurrent"),
            "battery_dispatch_power": None,
            "comm_control_mode": None,
            "forced_cmd": None,
            "forced_mode": None,
            "forced_target_soc": None,
            "forced_duration": None,
            "forced_power": None,
            "station_status": device.get("runStatusName"),
            "device_id": device.get("id"),
            "device_serial_number": device.get("sn"),
            "device_model": device.get("model"),
            "data_time": device.get("dataTime"),
            "daily_demand": device.get("dailyDemand", values.get("daily_demand")),
            "total_demand": device.get("totalDemand", values.get("total_demand")),
        }
