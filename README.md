# HouseIQ Energy Custom Integration

This custom integration implements your own energy integration and cycle sensors,
avoiding reliance on the built-in helpers to ensure compatibility.

## Features

- DataUpdateCoordinator for energy accumulation and resets
- Daily, weekly, monthly, yearly energy sensors
- Configurable source sensor via UI

## Installation

1. Unzip the `houseiq_energy.zip` into your Home Assistant `/config/` folder.
2. Restart Home Assistant.
3. Go to Settings → Integrations → Add Integration → HouseIQ Energy.
4. Select your source power sensor (e.g., `sensor.electricity_meter_energieproductie`).
5. The integration will create:
   - Four sensors: daily, weekly, monthly, yearly energy production
