import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import CYCLES, CONF_SOURCE_SENSOR
from .coordinator import EnergyCoordinator
from homeassistant.const import UnitOfEnergy

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback):
    src = entry.data[CONF_SOURCE_SENSOR]
    coordinator = EnergyCoordinator(hass, src)
    src_sensor = src
    base = src_sensor.split(".")[1] if "." in src_sensor else src_sensor
    entities = [CycleEnergySensor(coordinator, cycle, base) for cycle in CYCLES]
    async_add_entities(entities, update_before_add=True)

class CycleEnergySensor(RestoreEntity):
    """Sensor for a specific energy cycle."""
    def __init__(self, coordinator: EnergyCoordinator, cycle: str, base: str) -> None:
        self.coordinator = coordinator
        self.cycle = cycle
        self._base = base
        self._attr_name = f"HouseIQ {cycle.capitalize()} {base.replace('_', ' ')}"
        self._attr_unique_id = f"houseiq_{base}_{cycle}"
        self._attr_device_class = "energy"
        self._attr_state_class = "total"
        self._attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    async def async_added_to_hass(self):
        """Register callbacks."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Unregister callbacks."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    @property
    def available(self) -> bool:
        return self.cycle in self.coordinator.data

    @property
    def state(self):
        return f"{self.coordinator.data[self.cycle]:.3f}"

    @property
    def extra_state_attributes(self):
        return {"last_reset": self.coordinator.last_reset[self.cycle]}
