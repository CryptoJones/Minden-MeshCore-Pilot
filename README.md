# Minden Meshtastic Pilot

Proposal and supporting material for a solar-powered, off-grid emergency-communications
relay (Meshtastic / LoRa) co-located on a City of Minden tornado-siren pole. Equipment
donated; installed by city crew; owned by the city. Includes a grant-funded expansion path.

## What's here

| File | What it is |
| --- | --- |
| `HARDWARE.md` | Recommended node hardware (Seeed Wio Tracker L1 Pro) + getting-started steps |
| `REPEATER-BUILD.md` | Build sheet for the pole-mounted solar repeater (parts, assembly, Meshtastic config) |
| `proposal.html` | The full council proposal — one self-contained HTML page. Open it in any browser to read or print. |

## Editing the proposal on another machine

The proposal is a single HTML file with **no dependencies** — no build step, no server,
nothing to install. To work on it from another computer:

```bash
git clone https://github.com/CryptoJones/Minden-Meshtastic-Pilot.git
cd Minden-Meshtastic-Pilot
```

- **Read / preview / print:** double-click `proposal.html`, or open it in any browser.
  It has a print stylesheet, so `Ctrl/Cmd-P` gives a clean printout (the yellow
  "before you present" banner is hidden in print).
- **Edit the words:** open `proposal.html` in any text editor. The content is plain
  HTML near the bottom of the file, after the `<style>` block. You do not need to touch
  the CSS.

## Getting started with your first node

Works for any Meshtastic device (Wio Tracker L1 Pro, Heltec, etc.), whether you're
bringing it up as a handheld or tethering it to a PC / Raspberry Pi.

1. **Flash Meshtastic** at <https://flasher.meshtastic.org> (Chrome/Edge — needs
   WebSerial). Choose region **US (915 MHz)**. This is the one setting that must be
   right or the node hears nothing.
2. **Talk to it.** Either pair the **Meshtastic phone app** over Bluetooth, or plug it
   into a computer over USB and drive it from the CLI:
   ```bash
   pipx install meshtastic          # or: pip install meshtastic
   meshtastic --info                # see the node
   meshtastic --set lora.region US  # if not already set
   meshtastic --sendtext "hello mesh"
   meshtastic --nodes               # who's out there
   ```
   On a PC/Pi the node shows up as `/dev/ttyUSB0` or `/dev/ttyACM0`.
3. **Attach the antenna before powering on** — transmitting with no antenna can damage
   the radio.
4. **Two nodes = a link; three = a real mesh.** Set two nodes ~15 ft apart (not
   touching — too close overloads them), confirm each appears in the other's node list,
   text both ways, then walk one off to find your real range.

For the pole repeater specifically (parts, assembly, ROUTER-role config), see
`REPEATER-BUILD.md`. For hardware choice and ordering gotchas, see `HARDWARE.md`.

## Fields still to fill in

The proposal has three placeholders left, each wrapped in a `<mark>…</mark>` tag and
written in `[square brackets]` so they're easy to find (they render highlighted):

- `[Meeting Date]`
- `[phone]`
- `[email]`

Search the file for `[` to jump to them. Everything else — name (Aaron K. Clark),
city, department, title, siren location (3rd & Hubbard), cost table — is already filled.

## Notes for the pilot itself

- **Region:** US Meshtastic hardware must be the **915 MHz** variant. An 868 MHz
  (EU) board won't talk to a US network and isn't legal to transmit on here.
- **The siren comes first.** Any install must keep the relay physically and
  electrically clear of the siren and its control wiring — see Section 5 of the proposal.
- **Talk to whoever services the sirens before the council meeting.** Being able to
  say "maintenance sees no conflict" disarms the main objection. Confirm, too, whether
  the siren system is city-controlled or run through the county/regional EMA — that
  changes who else has to sign off.

---

Not affiliated with or endorsed by the City of Minden; this is a citizen proposal
prepared for submission to the council.
