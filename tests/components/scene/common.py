"""Collection of helper methods.

All containing methods are legacy helpers that should not be used by new
components. Instead call the service directly.
"""

from homeassistant.components.scene import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, ENTITY_MATCH_ALL, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.loader import bind_hass


@bind_hass
def activate(hass: HomeAssistant, entity_id: str = ENTITY_MATCH_ALL) -> None:
    """Activate a scene."""
    data = {}

    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id

    hass.services.call(DOMAIN, SERVICE_TURN_ON, data)
