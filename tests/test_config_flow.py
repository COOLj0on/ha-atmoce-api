"""Tests for the Atmoce Cloud API config flow."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.atmoce.config_flow import AtmoceConfigFlow
from custom_components.atmoce.cloud_client import AtmoceCloudAuthError
from custom_components.atmoce.const import (
    CONF_PASSWORD,
    CONF_SITE_ID,
    CONF_USERNAME,
)


USER_INPUT = {
    CONF_USERNAME: " user@example.com ",
    CONF_PASSWORD: "secret",
    CONF_SITE_ID: "123456",
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
