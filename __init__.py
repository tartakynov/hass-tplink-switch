import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_IP, CONF_USERNAME, CONF_PASSWORD, DOMAIN
from .coordinator import TPLinkSwitchCoordinator
from .tlstats import TLStats

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    ip = config_entry.data[CONF_IP]
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    tracker = TLStats(host=ip, username=username, password=password)
    coord = TPLinkSwitchCoordinator(hass, tracker)

    await coord.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coord

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    # Cleanup the tracker session
    if unload_ok and config_entry.entry_id in hass.data[DOMAIN]:
        coord = hass.data[DOMAIN].pop(config_entry.entry_id)
        coord.tracker.close()

    return unload_ok
