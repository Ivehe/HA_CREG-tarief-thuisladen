from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import CregDataUpdateCoordinator

SENSORS: list[SensorEntityDescription] = [
    SensorEntityDescription(key="flanders", name="Flanders"),
    SensorEntityDescription(key="brussels", name="Brussels"),
    SensorEntityDescription(key="wallonia", name="Wallonia"),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: CregDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        CregSensor(coordinator, entry, description)
        for description in SENSORS
    )

class CregSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CREG tariff sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:ev-station"
    _attr_native_unit_of_measurement = "c€/kWh"

    def __init__(self, coordinator: CregDataUpdateCoordinator, entry: ConfigEntry, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = f"CREG Tarief {description.name}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="CREG Tarief Thuis Laden",
            manufacturer="CREG",
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "source_year": self.coordinator.data.get("source_year"),
            "source_month": self.coordinator.data.get("source_month"),
        }
