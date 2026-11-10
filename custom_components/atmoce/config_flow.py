"""Config flow for the Atmoce Cloud API integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers import selector

from .cloud_client import AtmoceCloudAuthError, AtmoceCloudClient, AtmoceCloudError
from .const import (
    CONF_PASSWORD,
    CONF_SITE_ID,
    CONF_USERNAME,
    DOMAIN,
)

_PASSWORD_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type="password")  # type: ignore[typeddict-item]
)
_LOGGER = logging.getLogger(__name__)


class AtmoceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup using the Atmoce Cloud Open API only."""

    VERSION = 1

    @staticmethod
    def _get_schema(username: str = "", password: str = "", site_id: str = "") -> vol.Schema:
        """Build the configuration schema with optional defaults.

        Args:
            username: Default username value.
            password: Default password value.
            site_id: Default site ID value.

        Returns:
            Voluptuous schema for the configuration form.
        """
        return vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=username): str,
                vol.Required(CONF_PASSWORD, default=password): _PASSWORD_SELECTOR,
                vol.Required(CONF_SITE_ID, default=site_id): str,
            }
        )

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Handle the initial user setup step.

        Args:
            user_input: User input from the form.

        Returns:
            Configuration flow result.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]
            site_id = user_input[CONF_SITE_ID].strip()

            validation_error = await self._validate_credentials(username, password, site_id)
            if validation_error:
                errors["base"] = validation_error
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(username, password, site_id),
                    errors=errors,
                )

            await self.async_set_unique_id(site_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"ATMOCE {site_id}",
                data={
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                    CONF_SITE_ID: site_id,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
            errors=errors,
        )

    @staticmethod
    async def _validate_credentials(username: str, password: str, site_id: str) -> str | None:
        """Validate device ID format and cloud API credentials.

        Args:
            username: API username.
            password: API password.
            site_id: Gateway device ID.

        Returns:
            Error key if validation fails, None otherwise.
        """
        try:
            int(site_id)
        except ValueError:
            return "invalid_device_id"

        return await _validate_api_credentials(username, password, site_id)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AtmoceOptionsFlow:
        """Return an options flow for this integration.

        Args:
            config_entry: The config entry.

        Returns:
            Options flow instance.
        """
        return AtmoceOptionsFlow()


async def _validate_api_credentials(username: str, password: str, site_id: str) -> str | None:
    """Validate cloud API credentials by attempting to fetch data.

    Args:
        username: API username.
        password: API password.
        site_id: Gateway device ID.

    Returns:
        Error key if validation fails, None otherwise.
    """
    client = AtmoceCloudClient(username, password)
    try:
        await client.async_fetch_site_data(site_id)
    except AtmoceCloudAuthError as err:
        _LOGGER.warning("Atmoce Cloud authentication failed: %s", err)
        return "invalid_auth"
    except (AtmoceCloudError, aiohttp.ClientError, OSError, asyncio.TimeoutError) as err:
        _LOGGER.warning("Atmoce Cloud connection failed: %s", err)
        return "cannot_connect"
    return None


class AtmoceOptionsFlow(config_entries.OptionsFlow):
    """Allow API credentials and site ID to be changed."""

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Handle the options flow.

        Args:
            user_input: User input from the form.

        Returns:
            Configuration flow result.
        """
        if user_input is not None:
            error = await _validate_api_credentials(
                user_input[CONF_USERNAME].strip(),
                user_input[CONF_PASSWORD],
                user_input[CONF_SITE_ID].strip(),
            )
            if error:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._get_schema_for_edit(),
                    errors={"base": error},
                )

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_SITE_ID: user_input[CONF_SITE_ID].strip(),
                },
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(step_id="init", data_schema=self._get_schema_for_edit())

    def _get_schema_for_edit(self) -> vol.Schema:
        """Build the options schema with current config values.

        Returns:
            Voluptuous schema for the options form.
        """
        current: dict[str, Any] = dict(self.config_entry.data)
        return vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=current.get(CONF_USERNAME, ""),
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=current.get(CONF_PASSWORD, ""),
                ): _PASSWORD_SELECTOR,
                vol.Required(
                    CONF_SITE_ID,
                    default=current.get(CONF_SITE_ID, ""),
                ): str,
            }
        )
