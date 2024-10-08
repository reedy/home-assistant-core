"""Diagnostics support for AirVisual."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import (
    CONF_API_KEY,
    CONF_COUNTRY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_STATE,
    CONF_UNIQUE_ID,
)
from homeassistant.core import HomeAssistant

from . import AirVisualConfigEntry
from .const import CONF_CITY

CONF_COORDINATES = "coordinates"
CONF_TITLE = "title"

TO_REDACT = {
    CONF_API_KEY,
    CONF_CITY,
    CONF_COORDINATES,
    CONF_COUNTRY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_STATE,
    # Config entry title and unique ID may contain sensitive data:
    CONF_TITLE,
    CONF_UNIQUE_ID,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AirVisualConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": async_redact_data(coordinator.data["data"], TO_REDACT),
    }
