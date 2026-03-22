# HDFury Arcana for Home Assistant

A custom Home Assistant integration for the [HDFury Arcana](https://www.hdfury.com/product/arcana/) eARC adapter, communicating over RS-232 serial.

The Arcana sits between your source (Apple TV, Shield, etc.) and your display/projector, adding eARC support, HDR tone mapping, Dolby Vision conversion, and output scaling. This integration gives you full control and monitoring from Home Assistant.

## Connection

The Arcana exposes an RS-232 serial interface via its 3.5mm jack. You need a USB-to-3.5mm RS-232 cable — the [DSD TECH SH-U35B](https://www.amazon.com/DSD-TECH-SH-U35B-Converter-Compatible/dp/B08ZS6M831) or any FTDI-based 3.5mm serial cable will work.

**Pinout:** Tip = TX, Ring = RX, Sleeve = GND

The integration communicates at 19200 baud, 8N1.

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots menu (top right) → **Custom repositories**
3. Paste `GraemeF/hdfury-arcana-ha` and select **Integration** as the category
4. Click **Add**, then find "HDFury Arcana" in the list and install it
5. Restart Home Assistant

### Manual

Copy the `custom_components/hdfury_arcana` directory into your Home Assistant `custom_components/` directory and restart.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "HDFury Arcana"
3. Select or enter the serial port path (e.g. `/dev/ttyUSB0`)
4. The integration will verify the connection and detect the device

### Options

After setup, go to the integration's options to configure:

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| Signal poll interval | 30s | 5–300s | How often signal status sensors are polled. Settings are polled every 5 minutes. |

## Entity Reference

### Select Entities (settings)

| Entity | Options | Description |
|--------|---------|-------------|
| Scale mode | auto, none, 4k60_420_10_hdr, 4k60_420_10_sdr, 4k60_420_8_hdr, 4k60_420_8_sdr, 4k30_444_8_hdr, 4k30_444_8_sdr, 1080p60_12_hdr, 1080p60_12_sdr, 1080p60_8_sdr | HDMI output scaling. **auto** optimises for sink capabilities, **none** passes through unchanged. |
| Audio mode | auto, display, earc, both | Audio output routing. **auto** depends on connection, **display** mutes eARC, **earc** mutes display, **both** always outputs from both. |
| HDR mode | auto, off, force4000, force2000, force1000, boost, custom, lldvsync | HDR metadata handling. **auto** passes through, **off** strips HDR (useful for JVC projectors), **force\*** sets MaxCLL/MaxFALL nits, **boost** offsets by HDR boost value, **custom** replaces with HDR custom value, **lldvsync** uses DV datablock nits. |
| LLDV to HDR primaries | bt2020, dci-p3 | Colour primaries for LLDV → HDR10 conversion. May require active LLDV content to change. |
| Audio source | hdmi, tv | Where audio is extracted from. **hdmi** from source device, **tv** via ARC/eARC (requires active ARC/eARC connection). |

### Number Entities (settings)

| Entity | Range | Description |
|--------|-------|-------------|
| HDR custom value | 0–10000 | Replacement MaxCLL/MaxFALL nit value when HDR mode is set to **custom**. |
| HDR boost value | -5000–5000 | Offset added to incoming HDR nits when HDR mode is set to **boost**. Negative values dim. |
| eARC delay | 0–255 | Audio delay in ms for lip-sync correction. Only active when eARC delay mode is on. |
| LLDV to HDR min luminance | 0–10000 | Min luminance for DV datablock in LLDV → HDR10 conversion. |
| LLDV to HDR max luminance | 0–10000 | Max luminance for DV datablock in LLDV → HDR10 conversion. |
| OSD colour | 0–31 | Text colour for on-screen display. |
| OSD timer | 0–255 | OSD auto-hide timer in seconds. |
| OSD fade | 0–255 | OSD fade timer in seconds. 0 = no fade. |

### Switch Entities (settings)

| Entity | Description |
|--------|-------------|
| eARC select | Enable/disable eARC audio output. Full audio up to Atmos over TrueHD. May be hardware-locked by physical connection state. |
| ARC select | Enable/disable ARC audio output. Up to DD+/Atmos over DD+. May be hardware-locked by physical connection state. |
| eARC delay mode | Enable/disable the eARC audio delay feature. |
| LLDV to HDR mode | Enable/disable Low Latency Dolby Vision to HDR10 conversion. |
| OSD | Enable/disable the on-screen display. |

### Button Entities

| Entity | Description |
|--------|-------------|
| Hotplug | Triggers HDMI hotplug event, causing source to re-negotiate. |
| Reboot | Restarts the Arcana unit. |
| Refresh | Triggers an immediate poll of all settings and signal status. |
| Factory reset | Resets the Arcana to factory defaults. |

### Sensor Entities (diagnostic)

| Entity | Description |
|--------|-------------|
| Firmware version | Current firmware version. |
| Serial number | Device serial number. |
| Input signal | Input video stream info (resolution, pixel clock, chroma, colourspace, bit depth). |
| Output signal | Output video stream info. |
| Display capabilities | Connected display name and max capabilities. |
| Audio output | Output audio format, sample rate, channels, bit depth. |
| eARC audio | eARC audio format info. |
| Source device | Source product description string. |
| Audio channels | Output audio channel count (LPCM mode only). |
| Audio encoding | Audio encoding mode (LPCM or bitstream). |

### Binary Sensor Entities (diagnostic)

| Entity | Description |
|--------|-------------|
| Input 5V | Whether a source device is connected and powered. |
| Output hotplug | Whether a display is connected. |
| Output TMDS | Whether video signal is actively being transmitted. |

## Notes

- **eARC/ARC select** may be hardware-locked depending on what is physically connected to the Arcana — the device rejects writes if the connection state doesn't support the mode.
- **Audio source** set to **tv** requires an active ARC/eARC connection from the TV.
- **LLDV to HDR primaries** may require active LLDV content playing to accept changes.
- **HDR mode** relationships: **boost** uses the HDR boost value, **custom** uses the HDR custom value, **lldvsync** uses the DV datablock luminance values.
- Signal status sensors (input/output signal, display capabilities, audio, etc.) are polled at a faster interval (default 30s) than settings (5 minutes) since they change with content.

## Requirements

- HDFury Arcana connected via USB-to-3.5mm RS-232 cable (FTDI chipset recommended)
- Home Assistant 2025.1.0 or later
