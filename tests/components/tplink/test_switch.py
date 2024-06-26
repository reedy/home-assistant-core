"""Tests for switch platform."""

from datetime import timedelta
from unittest.mock import AsyncMock

from kasa import AuthenticationException, SmartDeviceException, TimeoutException
import pytest

from homeassistant.components import tplink
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.tplink.const import DOMAIN
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util, slugify

from . import (
    MAC_ADDRESS,
    _mocked_dimmer,
    _mocked_plug,
    _mocked_strip,
    _patch_connect,
    _patch_discovery,
)

from tests.common import MockConfigEntry, async_fire_time_changed


async def test_plug(hass: HomeAssistant) -> None:
    """Test a smart plug."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    plug = _mocked_plug()
    with _patch_discovery(device=plug), _patch_connect(device=plug):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    entity_id = "switch.my_plug"
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_off", {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    plug.turn_off.assert_called_once()
    plug.turn_off.reset_mock()

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_on", {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    plug.turn_on.assert_called_once()
    plug.turn_on.reset_mock()


@pytest.mark.parametrize(
    ("dev", "domain"),
    [
        (_mocked_plug(), "switch"),
        (_mocked_strip(), "switch"),
        (_mocked_dimmer(), "light"),
    ],
)
async def test_led_switch(hass: HomeAssistant, dev, domain: str) -> None:
    """Test LED setting for plugs, strips and dimmers."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    with _patch_discovery(device=dev), _patch_connect(device=dev):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    entity_name = slugify(dev.alias)

    led_entity_id = f"switch.{entity_name}_led"
    led_state = hass.states.get(led_entity_id)
    assert led_state.state == STATE_ON
    assert led_state.name == f"{dev.alias} LED"

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_off", {ATTR_ENTITY_ID: led_entity_id}, blocking=True
    )
    dev.set_led.assert_called_once_with(False)
    dev.set_led.reset_mock()

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_on", {ATTR_ENTITY_ID: led_entity_id}, blocking=True
    )
    dev.set_led.assert_called_once_with(True)
    dev.set_led.reset_mock()


async def test_plug_unique_id(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Test a plug unique id."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    plug = _mocked_plug()
    with _patch_discovery(device=plug), _patch_connect(device=plug):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    entity_id = "switch.my_plug"
    assert entity_registry.async_get(entity_id).unique_id == "aa:bb:cc:dd:ee:ff"


async def test_plug_update_fails(hass: HomeAssistant) -> None:
    """Test a smart plug update failure."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    plug = _mocked_plug()
    with _patch_discovery(device=plug), _patch_connect(device=plug):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    entity_id = "switch.my_plug"
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON
    plug.update = AsyncMock(side_effect=SmartDeviceException)

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=30))
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state.state == STATE_UNAVAILABLE


async def test_strip(hass: HomeAssistant) -> None:
    """Test a smart strip."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    strip = _mocked_strip()
    with _patch_discovery(device=strip), _patch_connect(device=strip):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    # Verify we only create entities for the children
    # since this is what the previous version did
    assert hass.states.get("switch.my_strip") is None

    entity_id = "switch.my_strip_plug0"
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_off", {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    strip.children[0].turn_off.assert_called_once()
    strip.children[0].turn_off.reset_mock()

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_on", {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    strip.children[0].turn_on.assert_called_once()
    strip.children[0].turn_on.reset_mock()

    entity_id = "switch.my_strip_plug1"
    state = hass.states.get(entity_id)
    assert state.state == STATE_OFF

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_off", {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    strip.children[1].turn_off.assert_called_once()
    strip.children[1].turn_off.reset_mock()

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_on", {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    strip.children[1].turn_on.assert_called_once()
    strip.children[1].turn_on.reset_mock()


async def test_strip_unique_ids(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Test a strip unique id."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    strip = _mocked_strip()
    with _patch_discovery(device=strip), _patch_connect(device=strip):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    for plug_id in range(2):
        entity_id = f"switch.my_strip_plug{plug_id}"
        assert (
            entity_registry.async_get(entity_id).unique_id == f"PLUG{plug_id}DEVICEID"
        )


@pytest.mark.parametrize(
    ("exception_type", "msg", "reauth_expected"),
    [
        (
            AuthenticationException,
            "Device authentication error async_turn_on: test error",
            True,
        ),
        (
            TimeoutException,
            "Timeout communicating with the device async_turn_on: test error",
            False,
        ),
        (
            SmartDeviceException,
            "Unable to communicate with the device async_turn_on: test error",
            False,
        ),
    ],
    ids=["Authentication", "Timeout", "Other"],
)
async def test_plug_errors_when_turned_on(
    hass: HomeAssistant,
    exception_type,
    msg,
    reauth_expected,
) -> None:
    """Tests the plug wraps errors correctly."""
    already_migrated_config_entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1"}, unique_id=MAC_ADDRESS
    )
    already_migrated_config_entry.add_to_hass(hass)
    plug = _mocked_plug()
    plug.turn_on.side_effect = exception_type("test error")

    with _patch_discovery(device=plug), _patch_connect(device=plug):
        await async_setup_component(hass, tplink.DOMAIN, {tplink.DOMAIN: {}})
        await hass.async_block_till_done()

    entity_id = "switch.my_plug"

    assert not any(
        already_migrated_config_entry.async_get_active_flows(hass, {SOURCE_REAUTH})
    )

    with pytest.raises(HomeAssistantError, match=msg):
        await hass.services.async_call(
            SWITCH_DOMAIN, "turn_on", {ATTR_ENTITY_ID: entity_id}, blocking=True
        )
    await hass.async_block_till_done()
    assert plug.turn_on.call_count == 1
    assert (
        any(
            flow
            for flow in already_migrated_config_entry.async_get_active_flows(
                hass, {SOURCE_REAUTH}
            )
            if flow["handler"] == tplink.DOMAIN
        )
        == reauth_expected
    )
