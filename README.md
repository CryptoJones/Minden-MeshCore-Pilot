<p align="center"><em>Proudly Made in Nebraska. Go Big Red! 🌽 <a href="https://xkcd.com/2347/">https://xkcd.com/2347/</a></em></p>

# Minden MeshCore Pilot

Proposal and supporting material for a solar-powered, off-grid emergency-communications
relay (MeshCore / LoRa) co-located on a City of Minden tornado-siren pole. Equipment
donated; installed by city crew; owned by the city. Includes a grant-funded expansion path.

**Why MeshCore:** Nebraska's mesh community has standardized on it, so a Minden relay
joins an existing statewide network instead of starting an island. That interoperability
is the reason for the platform choice — see Section 3 of the proposal.

## What's here

| File | What it is |
| --- | --- |
| `HARDWARE.md` | Recommended node hardware (Seeed Wio Tracker L1 Pro, MeshCore edition) + getting-started steps |
| `REPEATER-BUILD.md` | Build sheet for the pole-mounted solar repeater (parts, assembly, MeshCore config) |
| `proposal.html` | The full council proposal — one self-contained HTML page. Open it in any browser to read or print. |

## Editing the proposal on another machine

The proposal is a single HTML file with **no dependencies** — no build step, no server,
nothing to install. To work on it from another computer:

```bash
git clone https://github.com/CryptoJones/Minden-MeshCore-Pilot.git
cd Minden-MeshCore-Pilot
```

- **Read / preview / print:** double-click `proposal.html`, or open it in any browser.
  It has a print stylesheet, so `Ctrl/Cmd-P` gives a clean printout (the yellow
  "before you present" banner is hidden in print).
- **Edit the words:** open `proposal.html` in any text editor. The content is plain
  HTML near the bottom of the file, after the `<style>` block. You do not need to touch
  the CSS.

## Getting started with your first node

Works for any MeshCore device (Wio Tracker L1 Pro, Heltec, etc.), whether you're
bringing it up as a handheld or tethering it to a PC / Raspberry Pi.

1. **Check the firmware.** The MeshCore edition ships pre-flashed with BLE Companion
   firmware, so a handheld needs nothing. To reflash — different role, different
   display, or a unit bought with Meshtastic on it — use
   <https://flasher.meshcore.io/seeed-studio-wio-tracker-l1-pro/> (Chrome/Edge, needs
   WebSerial), or double-tap RST and drag the `.uf2` onto the `TRACKER L1` drive.
   **MeshCore ships separate firmware per role** — Companion, Repeater, Room Server —
   and separate OLED vs e-ink builds. Pick the pair that matches.
2. **Set the region to US 915 MHz.** This is the one setting that must be right or the
   node hears nothing. Confirm the exact preset against what the Nebraska mesh runs.
3. **Talk to it.** Either pair the **MeshCore phone app** over Bluetooth (iOS/Android),
   or plug it into a computer over USB and drive it from the CLI:
   ```bash
   pipx install meshcore-cli              # or: pip install meshcore-cli
   meshcore-cli -s /dev/ttyACM0 infos     # see the node
   meshcore-cli -s /dev/ttyACM0 contacts  # who's out there
   meshcore-cli -s /dev/ttyACM0 msg <name> "hello mesh"
   ```
   On a PC/Pi the node shows up as `/dev/ttyUSB0` or `/dev/ttyACM0`. There's also a
   browser client at <https://app.meshcore.nz>.
4. **Attach the antenna before powering on** — transmitting with no antenna can damage
   the radio.
5. **Two nodes = a link; three = a real mesh.** Set two nodes ~15 ft apart (not
   touching — too close overloads them), confirm each appears in the other's contact
   list, text both ways, then walk one off to find your real range.

For the pole repeater specifically (parts, assembly, Repeater-firmware config), see
`REPEATER-BUILD.md`. For hardware choice and ordering gotchas, see `HARDWARE.md`.

## Fields still to fill in

**None — the proposal is fully filled in.** Name (Aaron K. Clark), city, department,
title, siren location (3rd & Hubbard), contact email, and the cost table are all set.
The date fills itself in with today's date whenever the file is opened or printed, so a
printed copy always carries the date it was actually run.

Worth checking before you present, even though nothing is blank:

- The cost table still reads $53 / ~$186 total. Both the MeshCore and Meshtastic
  editions of the L1 Pro list at the same price, so the switch didn't change it — but
  re-check current pricing before quoting figures to the Council.
- Confirm the radio preset the Nebraska mesh actually runs, since Section 3 now rests
  on interoperability with it.

## Notes for the pilot itself

- **Region:** US hardware must be the **915 MHz** variant. An 868 MHz (EU) board won't
  talk to a US network and isn't legal to transmit on here.
- **Interoperability is the point.** Match whatever radio preset the Nebraska mesh is
  actually running, not just "US" in the abstract. A node on the wrong preset is
  invisible to the state network and looks simply broken.
- **The siren comes first.** Any install must keep the relay physically and
  electrically clear of the siren and its control wiring — see Section 5 of the proposal.
- **Talk to whoever services the sirens before the council meeting.** Being able to
  say "maintenance sees no conflict" disarms the main objection. Confirm, too, whether
  the siren system is city-controlled or run through the county/regional EMA — that
  changes who else has to sign off.

---

Not affiliated with or endorsed by the City of Minden; this is a citizen proposal
prepared for submission to the council.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
