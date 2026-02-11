"""Sensor platform for CREG-tarief thuis laden."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import CregDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the CREG sensors."""
    coordinator: CregDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            CregSensor(coordinator, "flanders", "Flanders"),
            CregSensor(coordinator, "brussels", "Brussels"),
            CregSensor(coordinator, "wallonia", "Wallonia"),
        ]
    )


class CregSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CREG Sensor."""

    def __init__(
        self,
        coordinator: CregDataUpdateCoordinator,
        key: str,
        region_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._region_name = region_name
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_name = f"CREG Tarief Thuis Laden {region_name}"
        self._attr_native_unit_of_measurement = "c€/kWh" # Cent Euro per kWh as per CSV header
        self._attr_state_class = SensorStateClass.MEASUREMENT
        # device_class MONETARY requires currency unit, so we skip it for c€/kWh
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {}
        return {
            "source_year": self.coordinator.data.get("source_year"),
            "source_month": self.coordinator.data.get("source_month"),
        }
