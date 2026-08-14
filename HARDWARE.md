# Hardware notes

## Recommended node: Seeed Wio Tracker L1 Pro

For both **field units** and, potentially, the **solar repeater**, the recommended
device is the **Seeed Studio Wio Tracker L1 Pro, MeshCore edition** — $47.90 list,
ready to use out of the box (it ships pre-flashed with MeshCore companion firmware).

Product page: https://www.seeedstudio.com/Wio-Tracker-L1-Pro-for-Meshcore-p-6717.html

Why it's the pick:

- **nRF52840** — a very low-power chip. Battery lasts *days*, not hours, which matters
  for a carried unit and is essential for a solar node. (This is the same low-power
  chip class you want on the repeater pole.)
- **Built-in GPS** — position sharing on the mesh, useful for field crews.
- **1.3" OLED + 4-way joystick** — read and send messages standalone, no phone needed.
- **2000 mAh battery, USB-C fast charge, and solar input** — three ways to power it.
- **Rugged 3D-printed case**, assembled and ready. No parts to source or build.

### Two things to get right when ordering

1. **Buy the MeshCore edition, NOT the Meshtastic one.** They are the same hardware
   with different firmware, and Meshtastic is a *separate, incompatible* mesh protocol —
   a Meshtastic unit will not talk to a MeshCore network, which means it will not talk
   to the rest of Nebraska.
   - MeshCore (correct): https://www.seeedstudio.com/Wio-Tracker-L1-Pro-for-Meshcore-p-6717.html
   - Meshtastic (avoid): https://www.seeedstudio.com/Wio-Tracker-L1-Pro-p-6454.html

   If you end up with the wrong one, it is not wasted — the firmware is
   interchangeable, see "Switching a unit you already own" below.
2. **Confirm US 915 MHz.** The radio covers 862–930 MHz; make sure it's set to the US
   band. An 868 MHz (EU) configuration is both illegal to transmit on in the US and
   won't talk to a US 915 network.

There's also a cheaper bare **Wio Tracker L1** (no case/screen) — the **Pro** is the
one worth buying.

## One tradeoff to know

The nRF52840 has **no WiFi** (Bluetooth only). This does not affect using the node as
a USB-attached base station on a PC or Raspberry Pi — it still exposes USB serial and
is driven by `meshcore-cli` the same way. It only means you can't later run the node as
a WiFi-connected device.

## Alternative: Heltec LoRa 32 V3 build (~$49)

If you specifically want an **ESP32 with WiFi**, the DIY option is a Heltec LoRa 32 V3
(US 915 MHz) + an 18650 holder + battery, about $49 assembled. MeshCore has builds for
it. More power-hungry (hours, not days), no GPS, and you assemble it — but WiFi-capable.
Fine as a PC/Pi-tethered base station; not the choice for a battery/solar field or pole
unit.

## Switching a unit you already own

MeshCore and Meshtastic run on the same L1 Pro hardware, so a unit bought with the
wrong firmware is a five-minute fix, not a wasted $53. The nRF52840 has an Adafruit
UF2 bootloader that neither firmware can overwrite, so this is not a brick risk:

1. Double-tap the **RST** button. Wait 10–15 s for a USB drive named `TRACKER L1`.
2. Drag the `.uf2` onto it. It reboots itself.

Get the file from <https://flasher.meshcore.io/seeed-studio-wio-tracker-l1-pro/>, which
will also do the whole thing over WebSerial in Chrome or Edge (not Firefox or Safari).
**Pick the build that matches the role AND the display** — MeshCore ships separate
firmware per role (Companion / Repeater / Room Server), and separate OLED vs e-ink
builds. Wrong display build gives you a blank screen on an otherwise working node.

Switching wipes the node's config and identity, so it rejoins the mesh as a new node.

## Getting started as a PC / Raspberry Pi node

1. The MeshCore edition arrives pre-flashed with **BLE Companion** firmware. To drive it
   from a computer over USB instead, flash the **USB Serial Companion** build from
   <https://flasher.meshcore.io/seeed-studio-wio-tracker-l1-pro/>.
2. Plug the node into the PC/Pi over USB (`/dev/ttyUSB0` or `/dev/ttyACM0`).
3. `pipx install meshcore-cli` (or `pip install meshcore-cli`).
4. `meshcore-cli -s /dev/ttyACM0 infos`, then `contacts`, `msg <name> "hello"`.
   Channel broadcast is `chan <number> "hello"`. `meshcore-cli --help` lists the rest.

Set the region to the **US 915 MHz** preset before transmitting — see `REPEATER-BUILD.md`
for the exact commands.

Always attach the antenna **before** powering on — transmitting with no antenna can
damage the radio. On a Raspberry Pi, use a solid 5 V / 3 A supply; a marginal supply
plus the radio's transmit-current spikes causes undervoltage and a flaky node.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
