# Minden Meshtastic Pilot

Proposal and supporting material for a solar-powered, off-grid emergency-communications
relay (Meshtastic / LoRa) co-located on a City of Minden tornado-siren pole. Equipment
donated; installed by city crew; owned by the city. Includes a grant-funded expansion path.

## What's here

| File | What it is |
| --- | --- |
| `HARDWARE.md` | Recommended node hardware (Seeed Wio Tracker L1 Pro) + getting-started steps |
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

## Fields still to fill in

The proposal has four placeholders left, each wrapped in a `<mark>…</mark>` tag and
written in `[square brackets]` so they're easy to find (they render highlighted):

- `[Meeting Date]`
- `[siren location / cross-streets]`
- `[phone]`
- `[email]`

Search the file for `[` to jump to them. Everything else — name (Aaron K. Clark),
city, department, title, cost table — is already filled.

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
