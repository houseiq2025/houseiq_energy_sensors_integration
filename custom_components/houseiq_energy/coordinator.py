import logging
from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_utc_time_change
from .const import CYCLES

_LOGGER = logging.getLogger(__name__)

class EnergyCoordinator(DataUpdateCoordinator):
    """Coordinator to accumulate energy and handle resets."""

    def __init__(self, hass: HomeAssistant, source_entity: str):
        super().__init__(hass, _LOGGER, name="energy_coordinator", update_interval=None)
        self.source = source_entity
        self.data = {cycle: 0.0 for cycle in CYCLES}
        self.last_reset = {cycle: datetime.utcnow() for cycle in CYCLES}

        hass.bus.async_listen("state_changed", self._state_changed)

        async_track_utc_time_change(hass, self._reset_daily, hour=0, minute=0, second=0)
        async_track_utc_time_change(hass, self._reset_weekly, weekday=0, hour=0, minute=0, second=0)
        async_track_utc_time_change(hass, self._reset_monthly, day=1, hour=0, minute=0, second=0)
        async_track_utc_time_change(hass, self._reset_yearly, month=1, day=1, hour=0, minute=0, second=0)

    @callback
    def _state_changed(self, event):
        entity_id = event.data.get("entity_id")
        if entity_id != self.source:
            return
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        # Validate new state
        if not new or new.state in (None, "unknown", "unavailable"):
            return
        try:
            new_val = float(new.state)
        except (ValueError, TypeError):
            return

        # Validate old state; if it's invalid we skip integration this round
        if not old or old.state in (None, "unknown", "unavailable"):
            return
        try:
            old_val = float(old.state)
        except (ValueError, TypeError):
            old_val = new_val

        # Calculate time difference in hours
        dt_seconds = (new.last_updated - old.last_updated).total_seconds()
        if dt_seconds <= 0:
            return  # no forward time, skip
        dt = dt_seconds / 3600

        # Trapezoidal integration: average power * time, convert W→kWh
        energy = ((new_val + old_val) / 2) * dt / 1000.0

        if energy < 0:
            return  # skip negative deltas

        for cycle in CYCLES:
            self.data[cycle] += energy

        # Notify listeners
        self.async_set_updated_data(self.data)

    @callback
    def _reset_daily(self, now):
        self.data["daily"] = 0.0
        self.last_reset["daily"] = now
        self.async_set_updated_data(self.data)

    @callback
    def _reset_weekly(self, now):
        self.data["weekly"] = 0.0
        self.last_reset["weekly"] = now
        self.async_set_updated_data(self.data)

    @callback
    def _reset_monthly(self, now):
        self.data["monthly"] = 0.0
        self.last_reset["monthly"] = now
        self.async_set_updated_data(self.data)

    @callback
    def _reset_yearly(self, now):
        self.data["yearly"] = 0.0
        self.last_reset["yearly"] = now
        self.async_set_updated_data(self.data)
