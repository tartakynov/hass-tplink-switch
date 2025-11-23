# TP-Link Network Switch Monitor for Home Assistant

This Home Assistant integration allows you to monitor the port link statuses from TL-SG1016PE network switch.

> [!CAUTION]
> Please be aware that Home Assistant exposes the configuration values of all integrations to every other installed
> integration. This means that if there is a malicious integration installed that sends back all configuration values
> from
> your Home Assistant, your network switch credentials could potentially be leaked. Use this integration at your own risk.

## Installation

To manually install this integration from GitHub, follow these instructions:

- Add `tplinkmonitor` folder with the contents of this repository into the `custom_components` directory of your Home
  Assistant installation. If the `custom_components` directory does not exist, create it at the same level as
  your `configuration.yaml` file.
- Restart Home Assistant to apply the changes.
- After restarting, configure the integration through the Home Assistant UI.

## Configuration

To configure this custom integration, follow these steps:

1. Navigate to your Home Assistant's `Settings` -> `Devices and Services`.
2. Click on the `Add Integration` button.
3. Search for the `TP-Link Network Switch Monitor` and select it.
4. Enter your credentials as required from the network switch to authenticate.

## Usage

Upon successful authentication, 16 new entities will be added to your Home Assistant:

- `sensor.#{entity ID}_port{N}`: Can have one of the following states - LINKDOWN, 10MH, 10MF, 100MH, 100MF, 1000MF

## Tracking Frequency

This integration queries the network switch for updated statistics every 5 minutes.
