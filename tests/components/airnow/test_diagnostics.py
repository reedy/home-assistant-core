"""Test AirNow diagnostics."""

import pytest
from syrupy import SnapshotAssertion

from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator


@pytest.mark.usefixtures("setup_airnow")
async def test_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
    snapshot: SnapshotAssertion,
) -> None:
    """Test config entry diagnostics."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    assert (
        await get_diagnostics_for_config_entry(hass, hass_client, config_entry)
        == snapshot
    )
