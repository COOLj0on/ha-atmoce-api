"""Tests for the Atmoce Cloud API coordinator."""
import asyncio
from unittest.mock import AsyncMock

import aiohttp
import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.atmoce.cloud_client import AtmoceCloudError
from custom_components.atmoce.const import SOURCE_CLOUD


class TestCloudPolling:
    """Cloud data is enriched with integration health values."""

    @pytest.mark.asyncio
    async def test_update_adds_source_and_error_count(self, coordinator):
        coordinator._client.async_fetch_site_data = AsyncMock(
            return_value={"grid_power": 500}
        )

        result = await coordinator._async_update_data()

        assert result == {
            "grid_power": 500,
            "active_source": SOURCE_CLOUD,
            "connection_errors": 0,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "error",
        [
            AtmoceCloudError("API rejected request"),
            aiohttp.ClientError("connection reset"),
            ConnectionError("offline"),
            OSError("network down"),
            asyncio.TimeoutError(),
        ],
    )
    async def test_network_failure_becomes_update_failed(self, coordinator, error):
        coordinator._client.async_fetch_site_data = AsyncMock(side_effect=error)

        with pytest.raises(UpdateFailed, match="Atmoce Cloud API unavailable"):
            await coordinator._async_update_data()

        assert coordinator.connection_errors == 1

    def test_active_source_is_cloud(self, coordinator):
        assert coordinator.active_source == SOURCE_CLOUD
