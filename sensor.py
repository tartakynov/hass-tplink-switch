from typing import Optional

from homeassistant.components.sensor import (
    SensorDeviceClass, SensorEntityDescription, SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_IP
from .coordinator import TPLinkSwitchCoordinator

LINK_STATUS_MAP = {
    0: "linkdown",
    2: "10mh",
    3: "10mf",
    4: "100mh",
    5: "100mf",
    6: "1000mf"
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TP-Link switch sensor entities."""
    coord: TPLinkSwitchCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Get the device IP from config entry
    device_ip = config_entry.data[CONF_IP]

    # Create sensor entities for each port based on the data length
    if coord.data is not None:
        entities = [
            TPLinkSwitchPortSensor(
                coordinator=coord,
                port_number=port_num + 1,  # Port numbers are 1-indexed
                device_ip=device_ip,
                entry_id=config_entry.entry_id,
            )
            for port_num in range(len(coord.data))
        ]
        async_add_entities(entities)


class TPLinkSwitchPortSensor(CoordinatorEntity, SensorEntity):
    """Representation of a TP-Link switch port sensor."""

    def __init__(
        self,
        coordinator: TPLinkSwitchCoordinator,
        port_number: int,
        device_ip: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._port_number = port_number
        self._device_ip = device_ip
        self._attr_unique_id = f"{entry_id}_port_{port_number}"
        self._attr_has_entity_name = True
        self._attr_translation_key = "port"
        self._attr_translation_placeholders = {"port_number": port_number}
        self.entity_description = SensorEntityDescription(
            key=f"port_{port_number}",
            name=f"Port {port_number}",
            icon="mdi:ethernet",
            device_class=SensorDeviceClass.ENUM,
            options=list(LINK_STATUS_MAP.values()),
            translation_key="port",
        )

    @property
    def native_value(self) -> Optional[str]:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        # Port numbers are 1-indexed, but the array is 0-indexed
        port_index = self._port_number - 1

        if port_index >= len(self.coordinator.data):
            return None

        status_value = self.coordinator.data[port_index]
        return LINK_STATUS_MAP.get(status_value, f"UNKNOWN_{status_value}")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information to link sensors to the same device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_ip)},
            name=f"TP-Link Switch ({self._device_ip})",
            manufacturer="TP-Link",
            model="TP-Link Switch",
        )
