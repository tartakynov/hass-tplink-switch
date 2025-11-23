import logging
import hashlib

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow

from .tlstats import TLStats
from .const import DOMAIN, CONF_IP, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)


async def try_fetch_statuses(data):
    ip = data.get(CONF_IP)
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)

    tracker = TLStats(host=ip, username=username, password=password)
    try:
        success = await tracker.update()
        return success
    finally:
        tracker.close()


class TLTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                success = await try_fetch_statuses(user_input)
                if success:
                    # Generate a unique ID based on the IP address
                    # This allows users to configure multiple switches
                    ip = user_input[CONF_IP]
                    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:8]
                    unique_id = f"tplink_switch_{ip_hash}"

                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    # Use IP address in the title for easy identification
                    title = f"TP-Link Switch ({ip})"

                    return self.async_create_entry(title=title, data=user_input)
                else:
                    errors["base"] = "auth_error"
            except Exception as e:
                _LOGGER.exception("Unexpected error during config flow: %s", e)
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
