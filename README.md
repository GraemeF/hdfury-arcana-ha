# HDFury Arcana for Home Assistant

A custom Home Assistant integration for the [HDFury Arcana](https://www.hdfury.com/product/arcana/) HDMI audio extractor, communicating over RS-232 serial.

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "HDFury Arcana" and install
3. Restart Home Assistant

### Manual

Copy the `custom_components/hdfury_arcana` directory into your Home Assistant `custom_components/` directory and restart.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "HDFury Arcana"
3. Enter the serial port path (e.g. `/dev/ttyUSB0`)
4. The integration will verify the connection and detect the device

## Entities

### Sensors (diagnostic)

| Entity | Description |
|--------|-------------|
| Firmware version | Device firmware version |
| Serial number | Device serial number |

### Switches

| Entity | Description |
|--------|-------------|
| eARC select | Enable/disable eARC output |
| ARC select | Enable/disable ARC output |
| eARC delay mode | Enable/disable eARC audio delay |

### Selects

| Entity | Options |
|--------|---------|
| Scale mode | auto, none, 4k60_420_10_hdr, 4k60_420_10_sdr, 4k60_420_8_hdr, 4k60_420_8_sdr, 4k30_444_8_hdr, 4k30_444_8_sdr, 1080p60_12_hdr, 1080p60_12_sdr, 1080p60_8_sdr |
| Audio mode | auto |
| HDR mode | auto, off, force1000 |
| LLDV to HDR mode | off, on |
| LLDV to HDR primaries | bt2020, dci-p3 |
| Audio source | hdmi, tv |

### Numbers

| Entity | Range | Description |
|--------|-------|-------------|
| HDR custom value | 0–10000 | Custom HDR nits value |
| HDR boost value | 0–100 | HDR boost percentage |
| eARC delay | 0–200 ms | Audio delay compensation |
| LLDV to HDR min luminance | 0–10000 | Minimum luminance for DV→HDR |
| LLDV to HDR max luminance | 0–10000 | Maximum luminance for DV→HDR |
| OSD colour | 0–63 | On-screen display colour value |

### Buttons

| Entity | Description |
|--------|-------------|
| Hotplug | Trigger HDMI hotplug signal |
| Reboot | Reboot the device |

## Requirements

- HDFury Arcana connected via USB-to-serial adapter (FTDI recommended)
- Home Assistant 2025.1.0 or later

## Serial Protocol

The integration communicates using the HDFury Arcana's RS-232 protocol at 19200 baud, 8N1. Commands use the format `#arcana get|set <param> [value]` with carriage return termination.
