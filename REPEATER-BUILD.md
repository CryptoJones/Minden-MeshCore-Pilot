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
| Solar panel, **5–6 V** nominal, ~5–10 W, rigid & weatherproof | $40 | sized for 24/7 unattended through cloudy stretches. **Must be a 5 V panel, not the usual 12/18 V** — see the voltage warning under Assembly |
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
   the pole. Verify it joins the mesh from a second node indoors. Use **firmware v1.14.1
   or newer** — older builds cannot do the 2-byte path hashes the state runs.
2. **Antenna:** disconnect the stock whip; connect the external gain antenna via coax to
   the unit's antenna connector. **Never power the radio with no antenna attached** — it
   can damage the transmitter.
3. **Enclosure:** mount the L1 Pro inside the weatherproof box. Bring the coax and the
   solar lead in through sealed cable glands. The unit's own case is rugged but is not a
   permanent all-weather mount on its own.
4. **Solar:** mount the panel facing due south, tilted roughly to your latitude, with a
   clear sky view. Wire it to the unit's solar/charge input — **but read the voltage
   warning below first.**

> ### ⚠ The L1 Pro's solar input is 5 V. Do not exceed it.
>
> Seeed's spec is **5 V / 1 A max, "do not exceed 5V"**, on a 2-pin 2.0 mm JST
> connector. Almost every solar panel sold for outdoor use is **12 V or 18 V nominal**
> and will read ~22 V open-circuit in cold sun. Connecting one directly to this input
> destroys the node instantly.
>
> Two safe options:
>
> - **Buy a 5–6 V panel** sized around 5–10 W and feed the solar input directly. Simplest,
>   fewest parts, nothing extra to fail inside a sealed box. This is what the $40 budget
>   line assumes.
> - **Use a higher-voltage panel with a buck converter** rated for 24 V+ input, stepping
>   down to 5 V, then into the **USB-C port** rather than the JST solar input. Fine on the
>   bench; adds a permanent failure point on a pole.
>
> The node cannot accept more than **5 W** (5 V × 1 A) no matter what you connect, so a
> large panel buys nothing. Oversize for cloudy weeks, not for watts the node can't take.
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

> ### ⚠ Do NOT use the stock `us` preset
>
> Nebraska Mesh does **not** run MeshCore's default US region settings. The stock preset
> uses a far wider bandwidth and a higher spreading factor. A node left on it is
> **deaf to the entire state network** while looking perfectly healthy on the bench.
> Set the four values below explicitly.

**Canonical Nebraska Mesh radio settings**, published by the group at
<https://www.nebraskamesh.net/help.html>. Re-check that page before install — these have
changed twice in the past year:

| Setting | Value | Note |
| --- | --- | --- |
| Frequency | **910.525 MHz** | inside the US 915 MHz band |
| Bandwidth | **62.5 kHz** | the "narrow" setting, adopted Oct 2025 |
| Spreading factor | **7** | updated 31 May 2026 |
| Coding rate | **8** | raise for longer or weaker links |

**Frequency, bandwidth and spreading factor must match exactly** or the node cannot hear
the state. Coding rate is the exception: it rides in each packet's header and the
receiver adapts, so a CR 8 node and a CR 5 node still hear each other. CR 8 buys margin
on your own weak links.

Set these over USB with the config tool at <https://config.meshcore.io>, or choose them
in the web flasher.

- **2-byte path hashes:** `set path.hash.mode 1`. **Mind the off-by-one — mode 1 means
  2 bytes**, mode 2 means 3 bytes. Needs **firmware v1.14 or newer**; Nebraska Mesh's
  current firmware is **v1.15.0**. Applies to companion nodes as well as repeaters.

  Each hop is tagged with a hash of the repeater that relayed it. At 1 byte there are
  only 256 possible values, so in a growing region two repeaters eventually collide and
  the mesh cannot tell their paths apart. 2 bytes gives 65,536. Nebraska Mesh required
  2-byte prefixes as part of a June 2026 upgrade, which tells you the state network had
  outgrown the 1-byte space — exactly the network this pilot wants to join.

  It degrades gracefully rather than failing hard: a 2-byte repeater still relays for
  1-byte nodes. The region is meant to be uniform, so match it.

- **Check the prefix for collisions** before install, using the prefix tool Nebraska Mesh
  publishes. The prefix is unique per node, so it is never part of a copy-paste block.

### Repeater tuning recommended by Nebraska Mesh

```
set agc.reset.interval 120
set txdelay 0.5
set loop.detect minimal
```

**`txdelay` depends on install height**, and ours is a pole:

| Install | txdelay |
| --- | --- |
| Tower / high elevation | 0.3 or below |
| Building top, 50–100 ft | 0.5 |
| Rooftop / low elevation | 0.5 or above |
| Mobile repeater | 2.0 |

A siren pole sits in the low-to-middle band, so **start at 0.5** and check their TX-delay
table once the exact mounting height is known.

They also publish a **voluntary repeater naming scheme** so node owners are identifiable
on the map. Follow it rather than inventing a name.
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

## Site survey — do this BEFORE anything goes up a pole

Free, done from a desk, and it is the step that prevents wasting a city crew's morning.

- [ ] Run the pole location through the MeshCore map's **line-of-sight and propagation
      tools**. Confirm usable sightlines before requesting a bucket truck.
- [ ] If the modeling looks poor, propose a different site rather than installing and hoping.

Field reports from operators in hilly terrain show these tools correctly predicting a
blocked path before it was confirmed on the ground. Minden's flat ground is the favorable
case — but flat also means no natural high points, which is exactly why the pole matters.

## Commissioning checklist

- [ ] **Verify the radio actually transmits at full power — not just that it boots.**
      A node can power up, join a mesh, and receive perfectly while transmitting badly.
      One documented field case had a defective unit that worked only within ~500 ft and
      passed every "does it turn on" check. **Walk-test the range before install**, and
      if you have two units, compare them against each other — a weak radio is only
      obvious next to a good one.
- [ ] Joins the mesh from a handheld on the bench before install.
- [ ] Antenna attached before every power-on.
- [ ] Solar input measured at **under 5 V** before it is ever connected to the node.
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

Two lessons worth carrying in from operators who have already done this:

- **Siting beats spending.** One operator moved a repeater ~1,200 ft to a spot only
  **30 ft higher** with better sightlines and went from roughly −8 dB to about 0 dB. That
  same person saw no improvement at all from a better antenna and no improvement from a
  purpose-built repeater over a bare node sitting in the yard. Height and geometry are the
  levers; hardware spend is not.
- **Solar is the easy part.** An 8 W panel held a 2× 18650 bank at 94–95% through a full
  week of rain — lying unmounted on the ground. Our budget is generous by comparison.

Worth doing early and for free: get the relay onto the **Nebraska mesh community's** map
and tell them it's coming up. Because the state has standardized on MeshCore, a correctly
configured Minden repeater joins the existing network rather than starting a private one —
and their operators are the fastest source of help on coverage, presets, and siting.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
