# Solar repeater build — Seeed Wio Tracker L1 Pro

Build sheet for the pole-mounted, off-grid MeshCore relay in the proposal. Built
around the **Seeed Wio Tracker L1 Pro** because its nRF52840 sips power, and it already
bundles the radio, battery, and solar input — so the whole node is one ~$47 device.

> **The siren comes first.** Everything here keeps the relay physically and electrically
> separate from the tornado siren and its control wiring — its own power, its own
> antenna, mounted clear of the siren head and its conduit. If anything ever conflicts,
> the relay yields. Do not tap the siren's power or run cable through its enclosure.

## Parts (~$180)

| Part | Est. | Notes |
| --- | --- | --- |
| Seeed Wio Tracker L1 Pro (MeshCore edition, US 915 MHz) | $48 | radio + 2000 mAh battery + solar input in one unit |
| Solar panel ~10 W, weatherproof, with charge management | $40 | sized for 24/7 unattended through cloudy stretches — bigger than the unit's built-in trickle input |
| External gain antenna (915 MHz fiberglass, ~5–6 dBi) + low-loss coax + pole mount | $55 | **this is what gives the pole its range** — the unit's stock whip is for handheld use |
| Weatherproof enclosure + cable glands | $23 | for permanent outdoor mounting + sealed cable entries |
| Contingency | $15 | |

Get the **MeshCore** edition (not Meshtastic) and confirm **US 915 MHz** — see `HARDWARE.md`.

## Why the antenna is the real cost

The L1 Pro's included antenna is a small whip — fine in a pocket, useless for reaching
across town from a pole. Range from an elevated repeater comes almost entirely from
**height + a real gain antenna**. Put a proper 915 MHz fiberglass antenna at the top of
the mast, feed it with **low-loss coax** (LMR-240 or better; keep the run short — coax
loss at 915 MHz adds up fast), and keep the electronics in a shaded box lower down.

## Assembly

1. **Flash + configure first, on the bench** (see Config below) before it ever goes up
   the pole. Verify it joins the mesh from a second node indoors.
2. **Antenna:** disconnect the stock whip; connect the external gain antenna via coax to
   the unit's antenna connector. **Never power the radio with no antenna attached** — it
   can damage the transmitter.
3. **Enclosure:** mount the L1 Pro inside the weatherproof box. Bring the coax and the
   solar lead in through sealed cable glands. The unit's own case is rugged but is not a
   permanent all-weather mount on its own.
4. **Solar:** mount the panel facing due south, tilted roughly to your latitude, with a
   clear sky view. Wire it to the unit's solar/charge input.
5. **Mount:** fix the enclosure to the pole **below and clear of the siren**, antenna run
   up the mast to the highest clear point, well away from the siren head and its conduit.

## Config (MeshCore)

**Flash the Repeater build, not the Companion firmware it ships with.** MeshCore makes
the role a *firmware choice*, not a setting — a pole relay runs dedicated Repeater
firmware that has no phone pairing and no user interface, just a serial/mesh admin
console. Get it from <https://flasher.meshcore.io/seeed-studio-wio-tracker-l1-pro/>
(Chrome or Edge), or double-tap RST and drag the `.uf2` onto the `TRACKER L1` drive.

Then configure it over USB serial. `pipx install meshcore-cli`, and use `-r` for direct
repeater mode:

```bash
meshcore-cli -r -s /dev/ttyACM0            # interactive repeater console
```

Settings that matter:

- **Radio preset:** `set preset us` — the US 915 MHz band plan. Must match every other
  node in the state or it hears nothing. Confirm against what the Nebraska mesh is
  actually running before install; a wrong preset is the single most common reason a
  new node appears dead.
- **Name:** `set name MINDEN-3RD-HUBBARD` — this is what shows up on the statewide map.
- **Fixed position:** `set lat <lat>` / `set lon <lon>`. The pole never moves, so set it
  once. This is what puts the relay on the map for everyone else; it is not a live GPS
  fix and costs nothing to keep.
- **Admin password:** `password <something-not-the-default>` — this gates remote
  configuration over the mesh. Set it, and record it somewhere the city has it too.
  Leaving the default means anyone in radio range can reconfigure the relay.
- **TX power:** `set tx <dBm>` — leave at the default unless there's a reason.

A repeater periodically broadcasts an *advert* — its name, position, and public key — so
the rest of the mesh learns it exists and can route through it. That is automatic.

Once it's on the pole you can administer it **over the air** from a companion node
rather than climbing back up: `meshcore-cli` in client mode, then `to <repeater-name>`
and the same commands, authenticated with the admin password.

## Commissioning checklist

- [ ] Joins the mesh from a handheld on the bench before install.
- [ ] Antenna attached before every power-on.
- [ ] After install, a handheld at a distant point in town can reach the mesh **through**
      the repeater (check hop count / that the repeater relayed).
- [ ] Battery holds voltage overnight and recovers through a cloudy day — watch it for a
      few days before trusting it unattended.
- [ ] Nothing on the relay touches or interferes with the siren or its activation.
- [ ] Admin password changed off the default and recorded where the city has it.
- [ ] The relay's advert is visible to the wider Nebraska mesh, not just to local nodes —
      this is the whole point of choosing MeshCore, so confirm it rather than assume it.

## Where this goes next

One elevated repeater plus handhelds is hub-and-spoke — a mesh, but a shallow one. Adding
a second elevated node (another siren pole, a water tower, a hilltop) is what gives real
path redundancy and self-healing. That's the grant-funded Phase 2 in the proposal.

Worth doing early and for free: get the relay onto the **Nebraska mesh community's** map
and tell them it's coming up. Because the state has standardized on MeshCore, a correctly
configured Minden repeater joins the existing network rather than starting a private one —
and their operators are the fastest source of help on coverage, presets, and siting.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
