"""Common methods used across tests for Ecobee."""

from unittest.mock import patch

from homeassistant.components.ecobee.const import CONF_REFRESH_TOKEN, DOMAIN
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def setup_platform(
    hass: HomeAssistant,
    platform: str,
) -> MockConfigEntry:
    """Set up the ecobee platform."""
    mock_entry = MockConfigEntry(
        title=DOMAIN,
        domain=DOMAIN,
        data={
            CONF_API_KEY: "ABC123",
            CONF_REFRESH_TOKEN: "EFG456",
        },
    )
    mock_entry.add_to_hass(hass)

    with patch("homeassistant.components.ecobee.PLATFORMS", [platform]):
        await hass.config_entries.async_setup(mock_entry.entry_id)
        await hass.async_block_till_done()
    return mock_entry
