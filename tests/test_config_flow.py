"""Tests for the Atmoce Cloud API config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.atmoce.cloud_client import AtmoceCloudAuthError
from custom_components.atmoce.config_flow import AtmoceConfigFlow, AtmoceOptionsFlow
from custom_components.atmoce.const import (
    CONF_ENABLED_SENSORS,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_SITE_ID,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
)
from custom_components.atmoce.sensor import SENSOR_DESCRIPTIONS

USER_INPUT = {
    CONF_USERNAME: " user@example.com ",
    CONF_PASSWORD: "secret",
    CONF_SITE_ID: "123456",
    CONF_ENABLED_SENSORS: [description.key for description in SENSOR_DESCRIPTIONS],
    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL // 60,
}


def _make_flow():
    flow = AtmoceConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    return flow


class TestUserStep:
    """Validate the Cloud API credentials and site ID."""

    @pytest.mark.asyncio
    async def test_success_creates_entry(self):
        flow = _make_flow()
        with patch("custom_components.atmoce.config_flow.AtmoceCloudClient") as cls:
            cls.return_value.async_fetch_site_data = AsyncMock(return_value={})

            await flow.async_step_user(USER_INPUT)

        flow.async_set_unique_id.assert_awaited_once_with("123456")
        flow.async_create_entry.assert_called_once_with(
            title="ATMOCE 123456",
            data={
                CONF_USERNAME: "user@example.com",
                CONF_PASSWORD: "secret",
                CONF_SITE_ID: "123456",
            },
            options={
                CONF_ENABLED_SENSORS: USER_INPUT[CONF_ENABLED_SENSORS],
                CONF_SCAN_INTERVAL: USER_INPUT[CONF_SCAN_INTERVAL],
            },
        )

    @pytest.mark.asyncio
    async def test_invalid_site_id_shows_form(self):
        flow = _make_flow()

        await flow.async_step_user({**USER_INPUT, CONF_SITE_ID: "not-a-number"})

        _, kwargs = flow.async_show_form.call_args
        assert kwargs["errors"]["base"] == "invalid_device_id"

    @pytest.mark.asyncio
    async def test_auth_failure_shows_auth_error(self):
        flow = _make_flow()
        with patch("custom_components.atmoce.config_flow.AtmoceCloudClient") as cls:
            cls.return_value.async_fetch_site_data = AsyncMock(
                side_effect=AtmoceCloudAuthError("invalid credentials")
            )

            await flow.async_step_user(USER_INPUT)

        _, kwargs = flow.async_show_form.call_args
        assert kwargs["errors"]["base"] == "invalid_auth"

    @pytest.mark.asyncio
    async def test_empty_form_shows_form(self):
        flow = _make_flow()

        await flow.async_step_user(None)

        flow.async_show_form.assert_called_once()


class TestOptionsStep:
    """Update credentials and polling settings."""

    @pytest.mark.asyncio
    async def test_updates_credentials_and_sensor_options(self):
        flow = AtmoceOptionsFlow()
        flow.hass = MagicMock()
        flow.handler = "entry_id"
        config_entry = MagicMock()
        config_entry.options = {}
        flow.hass.config_entries.async_get_known_entry.return_value = config_entry
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        user_input = {
            **USER_INPUT,
            CONF_USERNAME: "updated@example.com",
            CONF_ENABLED_SENSORS: ["grid_power"],
            CONF_SCAN_INTERVAL: 5,
        }

        with patch(
            "custom_components.atmoce.config_flow._validate_api_credentials",
            return_value=None,
        ):
            await flow.async_step_init(user_input)

        flow.hass.config_entries.async_update_entry.assert_called_once_with(
            config_entry,
            data={
                CONF_USERNAME: "updated@example.com",
                CONF_PASSWORD: "secret",
                CONF_SITE_ID: "123456",
            },
            options={
                CONF_ENABLED_SENSORS: ["grid_power"],
                CONF_SCAN_INTERVAL: 5,
            },
        )
