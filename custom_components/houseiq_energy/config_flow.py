import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_SOURCE_SENSOR

class HouseIQConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HouseIQ Energy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_create_entry(
                title=user_input[CONF_SOURCE_SENSOR],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SOURCE_SENSOR): selector.selector({
                    "entity": {"domain": ["sensor"]}
                })
            }),
        )
