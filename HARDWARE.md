# Hardware notes

## Recommended node: Seeed Wio Tracker L1 Pro

For both **field units** and, potentially, the **solar repeater**, the recommended
device is the **Seeed Studio Wio Tracker L1 Pro** — ~$47, ready to use out of the box.

Product page: https://www.seeedstudio.com/Wio-Tracker-L1-Pro-p-6454.html

Why it's the pick:

- **nRF52840** — a very low-power chip. Battery lasts *days*, not hours, which matters
  for a carried unit and is essential for a solar node. (This is the same low-power
  chip class you want on the repeater pole.)
- **Built-in GPS** — position sharing on the mesh, useful for field crews.
- **1.3" OLED + 4-way joystick** — read and send messages standalone, no phone needed.
- **2000 mAh battery, USB-C fast charge, and solar input** — three ways to power it.
- **Rugged 3D-printed case**, assembled and ready. No parts to source or build.

### Two things to get right when ordering

1. **Buy the Meshtastic edition, NOT the Meshcore one.** They are the same hardware
   with different firmware, and Meshcore is a *separate, incompatible* mesh protocol —
   a Meshcore unit will not talk to a Meshtastic network.
   - Meshtastic (correct): https://www.seeedstudio.com/Wio-Tracker-L1-Pro-p-6454.html
   - Meshcore (avoid, unless you specifically want Meshcore): https://www.seeedstudio.com/Wio-Tracker-L1-Pro-for-Meshcore-p-6717.html
2. **Confirm US 915 MHz.** The radio covers 862–930 MHz; make sure it's set to the US
   band. An 868 MHz (EU) configuration is both illegal to transmit on in the US and
   won't talk to a US 915 network.

There's also a cheaper bare **Wio Tracker L1** (no case/screen) — the **Pro** is the
one worth buying.

## One tradeoff to know

The nRF52840 has **no WiFi** (Bluetooth only). This does not affect using the node as
a USB-attached base station on a PC or Raspberry Pi — it still exposes USB serial and
is driven by the `meshtastic` CLI the same way. It only means you can't later run the
node as a WiFi-connected device.

## Alternative: Heltec LoRa 32 V3 build (~$49)

If you specifically want an **ESP32 with WiFi** (e.g. to run a node as a WiFi/MQTT
gateway), the DIY option is a Heltec LoRa 32 V3 (US 915 MHz) + an 18650 holder +
battery, about $49 assembled. More power-hungry (hours, not days), no GPS, and you
assemble it — but WiFi-capable. Fine as a PC/Pi-tethered base station; not the choice
for a battery/solar field or pole unit.

## Getting started as a PC / Raspberry Pi node

1. Flash Meshtastic at https://flasher.meshtastic.org (Chrome). Region: **US (915 MHz)**.
2. Plug the node into the PC/Pi over USB (`/dev/ttyUSB0` or `/dev/ttyACM0`).
3. `pipx install meshtastic` (or `pip install meshtastic`).
4. `meshtastic --info`, `meshtastic --sendtext "hello"`, `meshtastic --nodes`.

Always attach the antenna **before** powering on — transmitting with no antenna can
damage the radio. On a Raspberry Pi, use a solid 5 V / 3 A supply; a marginal supply
plus the radio's transmit-current spikes causes undervoltage and a flaky node.
