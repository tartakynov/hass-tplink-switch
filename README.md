# TP-Link Network Switch Monitor for Home Assistant

This Home Assistant integration allows you to monitor the port link statuses from TL-SG1016PE network switch.

> [!NOTE]
> This is not an official integration and is not affiliated with or endorsed by TP-Link.

> [!CAUTION]
> This integration stores your network switch credentials in Home Assistant. Be aware that other malicious integrations could potentially access and steal these credentials.

## Installation

To manually install this integration from GitHub, follow these instructions:

- Clone this repository into the `custom_components` folder of your Home Assistant installation, so you have `custom_components/hass-tplink-switch` with the contents of this repository. If the `custom_components` directory does not exist, create it at the same level as your `configuration.yaml` file.
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

- `sensor.#{entity ID}_port{N}`: Can have one of the following states - LINKDOWN, 10MH, 10MF, 100MH, 100MF, 1000MF, UNKNOWN

## Tracking Frequency

This integration queries the network switch for updated statistics every 15 minutes.

## Example Automation

Here's an example automation that sends a notification whenever any port link status changes:

```yaml
alias: TP-Link Switch - Port Status Changed
description: Send notification when any switch port status changes
triggers:
  - trigger: state
    entity_id:
      - sensor.tp_link_switch_192_168_1_2_port_1
      - sensor.tp_link_switch_192_168_1_2_port_2
      - sensor.tp_link_switch_192_168_1_2_port_3
      - sensor.tp_link_switch_192_168_1_2_port_4
      - sensor.tp_link_switch_192_168_1_2_port_5
      - sensor.tp_link_switch_192_168_1_2_port_6
      - sensor.tp_link_switch_192_168_1_2_port_7
      - sensor.tp_link_switch_192_168_1_2_port_8
      - sensor.tp_link_switch_192_168_1_2_port_9
      - sensor.tp_link_switch_192_168_1_2_port_10
      - sensor.tp_link_switch_192_168_1_2_port_11
      - sensor.tp_link_switch_192_168_1_2_port_12
      - sensor.tp_link_switch_192_168_1_2_port_13
      - sensor.tp_link_switch_192_168_1_2_port_14
      - sensor.tp_link_switch_192_168_1_2_port_15
      - sensor.tp_link_switch_192_168_1_2_port_16
conditions:
  - condition: template
    value_template: "{{ trigger.from_state.state not in ['unknown', 'unavailable'] }}"
actions:
  - action: notify.send_message
    metadata: {}
    data:
      message: >-
        {{ state_attr(trigger.entity_id, 'friendly_name') }} changed from {{
        trigger.from_state.state }} to {{ trigger.to_state.state }}
      title: Switch Port Status Change
    target:
      device_id: target_device_id
mode: single
```

