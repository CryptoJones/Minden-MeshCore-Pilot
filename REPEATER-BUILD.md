# Solar repeater build — Seeed Wio Tracker L1 Pro

Build sheet for the pole-mounted, off-grid Meshtastic relay in the proposal. Built
around the **Seeed Wio Tracker L1 Pro** because its nRF52840 sips power, and it already
bundles the radio, battery, and solar input — so the whole node is one ~$47 device.

> **The siren comes first.** Everything here keeps the relay physically and electrically
> separate from the tornado siren and its control wiring — its own power, its own
> antenna, mounted clear of the siren head and its conduit. If anything ever conflicts,
> the relay yields. Do not tap the siren's power or run cable through its enclosure.

## Parts (~$180)

| Part | Est. | Notes |
| --- | --- | --- |
| Seeed Wio Tracker L1 Pro (Meshtastic, US 915 MHz) | $47 | radio + 2000 mAh battery + solar input in one unit |
| Solar panel ~10 W, weatherproof, with charge management | $40 | sized for 24/7 unattended through cloudy stretches — bigger than the unit's built-in trickle input |
| External gain antenna (915 MHz fiberglass, ~5–6 dBi) + low-loss coax + pole mount | $55 | **this is what gives the pole its range** — the unit's stock whip is for handheld use |
| Weatherproof enclosure + cable glands | $23 | for permanent outdoor mounting + sealed cable entries |
| Contingency | $15 | |

Get the **Meshtastic** edition (not Meshcore) and confirm **US 915 MHz** — see `HARDWARE.md`.

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

## Config (Meshtastic)

Flash at https://flasher.meshtastic.org (Chrome). Then, from the phone app or the
`meshtastic` CLI:

- **Region:** `US` (915 MHz). Must match every other node or it hears nothing.
- **Role:** `ROUTER`. This role is *specifically* for permanently-placed, elevated,
  good-coverage infrastructure nodes — exactly a pole repeater. It rebroadcasts for the
  mesh and stays awake to do so. (Do **not** set regular handhelds to ROUTER; it's for
  infrastructure only. If you want a pure relay that doesn't appear in the node list,
  `REPEATER` is the alternative — lower overhead, but you lose its telemetry.)
- **Fixed position:** since the pole never moves, set a **fixed GPS position** once and
  then disable the live GPS to save power. A repeater doesn't need to keep a live fix.
- **Channel:** default `LongFast`, or a shared AES key if the mesh should be private.

CLI equivalents:

```bash
meshtastic --set lora.region US
meshtastic --set device.role ROUTER
meshtastic --setlat <lat> --setlon <lon> --setalt <m>   # then disable GPS in the app
meshtastic --info      # confirm it's configured
```

## Commissioning checklist

- [ ] Joins the mesh from a handheld on the bench before install.
- [ ] Antenna attached before every power-on.
- [ ] After install, a handheld at a distant point in town can reach the mesh **through**
      the repeater (check hop count / that the repeater relayed).
- [ ] Battery holds voltage overnight and recovers through a cloudy day — watch it for a
      few days before trusting it unattended.
- [ ] Nothing on the relay touches or interferes with the siren or its activation.

## Where this goes next

One elevated repeater plus handhelds is hub-and-spoke — a mesh, but a shallow one. Adding
a second elevated node (another siren pole, a water tower, a hilltop) is what gives real
path redundancy and self-healing. That's the grant-funded Phase 2 in the proposal.
