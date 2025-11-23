import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .tlstats import TLStats

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)


class TPLinkSwitchCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching TP-Link switch data."""

    tracker: TLStats

    def __init__(self, hass: HomeAssistant, tracker: TLStats):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="TP-Link Switch",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.tracker = tracker

    async def _async_update_data(self):
        """Fetch data from the switch."""
        success = await self.tracker.update()
        if not success:
            raise UpdateFailed("Failed to fetch switch data")
        return self.tracker.link_statuses
