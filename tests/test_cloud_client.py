"""Tests for the Atmoce Cloud API client."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.atmoce.cloud_client import (
    AtmoceCloudAuthError,
    AtmoceCloudClient,
    AtmoceCloudError,
)


def _response(payload, status=200):
    response = MagicMock()
    response.status = status
    response.json = AsyncMock(return_value=payload)
    return response


def _session(responses):
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.post = AsyncMock(side_effect=[_response(item) for item in responses])
    return session


AUTH = {"code": 200, "data": {"token": "token", "prefix": "Bearer "}}
SITE = {
    "code": 200,
    "success": True,
    "data": {
        "id": 123456,
        "sn": "SN123",
        "gridPower": 500,
        "generationPower": 2000,
        "storagePower": -800,
        "runStatusName": "Running",
        "dataValues": {"daily_generation": 8.5},
    },
}


class TestAuthentication:
    @pytest.mark.asyncio
    async def test_authenticate_stores_token(self):
        client = AtmoceCloudClient("user@example.com", "secret")
        with patch("custom_components.atmoce.cloud_client.aiohttp.ClientSession") as cls:
            cls.return_value = _session([AUTH])

            await client._async_authenticate()

        assert client._token == "token"

    @pytest.mark.asyncio
    async def test_authenticate_rejects_invalid_credentials(self):
        client = AtmoceCloudClient("user@example.com", "wrong")
        with patch("custom_components.atmoce.cloud_client.aiohttp.ClientSession") as cls:
            cls.return_value = _session(
                [{"code": 401, "msg": "invalid credentials"}]
            )

            with pytest.raises(AtmoceCloudAuthError):
                await client._async_authenticate()


class TestFetch:
    @pytest.mark.asyncio
    async def test_fetch_maps_cloud_fields(self):
        client = AtmoceCloudClient("user@example.com", "secret")
        with patch("custom_components.atmoce.cloud_client.aiohttp.ClientSession") as cls:
            cls.return_value = _session([AUTH, SITE])

            data = await client.async_fetch_site_data("123456")

        assert data["grid_power"] == 500
        assert data["pv_power"] == 2000
        assert data["battery_power"] == -800
        assert data["device_serial_number"] == "SN123"
        assert data["daily_demand"] is None

    @pytest.mark.asyncio
    async def test_fetch_rejects_unsuccessful_payload(self):
        client = AtmoceCloudClient("user@example.com", "secret")
        client._token = "token"
        with patch("custom_components.atmoce.cloud_client.aiohttp.ClientSession") as cls:
            cls.return_value = _session(
                [
                    {"code": 500, "success": False, "msg": "failed"},
                    AUTH,
                    {"code": 500, "success": False, "msg": "failed"},
                ]
            )

            with pytest.raises(AtmoceCloudError):
                await client.async_fetch_site_data("123456")
