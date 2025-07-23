
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import UnitOfEnergy

from .const import CYCLES, CONF_SOURCE_SENSOR, DOMAIN
from .coordinator import EnergyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HouseIQ Energy cycle sensors for this config entry."""
    src_sensor = entry.data[CONF_SOURCE_SENSOR]

    # Make (or reuse) one coordinator per entry
    coordinator = hass.data.setdefault(DOMAIN, {}).get(entry.entry_id)
    if coordinator is None:
        coordinator = EnergyCoordinator(hass, src_sensor)
        hass.data[DOMAIN][entry.entry_id] = coordinator

    entities = [CycleEnergySensor(coordinator, cycle) for cycle in CYCLES]
    async_add_entities(entities, update_before_add=True)


class CycleEnergySensor(Entity):
    """Accumulated energy for a specific cycle (daily, weekly, etc.)."""

    _attr_device_class = "energy"
    _attr_state_class = "total"
    _attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_should_poll = True  # simple polling to refresh UI

    def __init__(self, coordinator: EnergyCoordinator, cycle: str) -> None:
        self.coordinator = coordinator
        self.cycle = cycle
        self._attr_name = f"HouseIQ {cycle.capitalize()} Energieproductie"
        self._attr_unique_id = f"houseiq_{cycle}_energieproductie"

    @property
    def state(self) -> str | None:
        """Return current accumulated kWh for this cycle."""
        return f"{self.coordinator.data.get(self.cycle, 0.0):.3f}"

    @property
    def extra_state_attributes(self) -> dict:
        """Expose the last reset timestamp."""
        return {"last_reset": self.coordinator.last_reset.get(self.cycle)}

    async def async_update(self) -> None:
        """No explicit update required; value pulled from coordinator."""
        # Coordinator updates its own data; sensor just reflects that.
        return
