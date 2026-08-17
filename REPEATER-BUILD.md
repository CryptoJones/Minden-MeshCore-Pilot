# Solar repeater build — SenseCAP Solar Node P1-Pro

Build sheet for the pole-mounted, off-grid MeshCore relay in the proposal. The pole
node is the sealed **SenseCAP Solar Node P1-Pro** (~$150), **not** a hand-built node.
This is the "hardened pole" tier — see DD-006 in the bridge project's `DESIGN.md`. The
cheap, many coverage nodes are a separate build (`COVERAGE-NODE.md`).

**Why a $150 sealed unit and not a $35 hand-build:**

- **The battery is the thing under test.** The pilot's evaluation *is* uptime and
  battery through the season. The P1-Pro's **13,400 mAh** pack (4× 18650) and integrated
  BMS mean a bad power system won't confound the data — a marginal hand-built pack fails
  for reasons that have nothing to do with whether community mesh works.
- **Cold-weather cell protection.** Lithium cannot be charged below 0 °C without
  permanent damage, and Minden sees −10 °C. The P1-Pro's BMS enforces a **0–50 °C charge
  window** — on a sub-freezing day it *stops charging to protect the cells* rather than
  destroying them, and rides the freeze on the big battery. A garden-light charger has no
  such cutoff. (This is protection, not sub-freezing charging — see the winter note below.)
- **Access cost and optics.** A siren pole means city coordination and maybe a bucket
  truck; one service visit costs more than the hardware saved. And off-the-shelf rated gear
  clears a city facilities review in a way a gutted garden light does not.

Worth knowing: the P1-Pro's **electronics are the same XIAO nRF52840 + Wio-SX1262** as the
coverage nodes. The $150 buys the 13.4 Ah battery, 5 W panel, BMS, and weatherproof
enclosure — ruggedization and capacity, not a better radio.

> **The siren comes first.** Everything here keeps the relay physically and electrically
> separate from the tornado siren and its control wiring — its own power, its own
> antenna, mounted clear of the siren head and its conduit. If anything ever conflicts,
> the relay yields. Do not tap the siren's power or run cable through its enclosure.

## Parts (~$210)

| Part | Est. | Notes |
| --- | --- | --- |
| SenseCAP Solar Node P1-Pro (US 915 MHz) — **buy direct from Seeed Studio** | $150 | all-in-one: 5 W panel, 13.4 Ah battery, BMS, GPS, weatherproof enclosure, 2 dBi RP-SMA whip |
| External gain antenna (915 MHz fiberglass, ~5–6 dBi) + low-loss coax + pole mount | $55 | *optional upgrade* — height + gain is what gives the pole its range. **Node connector is RP-SMA**, not SMA — match it or use an adapter |
| Pole mount / U-bolts / hose clamps | contingency | the unit mounts as one piece; panel faces the sky |

No separate panel, charge controller, enclosure, or panel-voltage wiring — the P1-Pro
integrates all of it. That is most of what the $150 buys over a hand-build.

**Vendor:** buy the P1-Pro **direct from Seeed Studio** (seeedstudio.com), not a reseller —
consistent with how the L1 Tracker nodes were sourced.

**Firmware:** the P1-Pro ships **pre-flashed with Meshtastic** on the standard SKU (a
MeshCore-preflashed SKU also exists); either **reflashes cleanly to MeshCore**. Confirm
you get / flash **MeshCore Repeater** and set **US 915 MHz** — see `HARDWARE.md` and Config
below.

## Why the antenna can still be the real cost

The included 2 dBi rubber whip works, but range from an elevated repeater comes almost
entirely from **height + a real gain antenna**. If the site needs the reach, put a proper
915 MHz fiberglass antenna at the top of the mast, feed it with **low-loss coax** (LMR-240
or better; keep the run short — coax loss at 915 MHz adds up fast), and mount the P1-Pro
lower with a clear sky view for its panel.

⚠ **The P1-Pro's antenna jack is RP-SMA (reverse polarity).** It looks like SMA and will
not mate with a standard SMA-male antenna. Buy an **RP-SMA** gain antenna, or an
SMA↔RP-SMA adapter. (Note this is the *opposite* connector convention from the coverage
nodes, whose Wio-SX1262 pigtails are plain SMA — don't cross the parts between builds.)

## Assembly

1. **Reflash + configure first, on the bench** (see Config below) before it ever goes up
   the pole. Verify it joins the mesh from a second node indoors. Use **firmware v1.14.1
   or newer** — older builds cannot do the 2-byte path hashes the state runs.
2. **Antenna:** use the included 2 dBi whip, or connect an external gain antenna via coax
   to the RP-SMA jack. **Never power the radio with no antenna attached** — it can damage
   the transmitter.
3. **Mount:** fix the unit to the pole **below and clear of the siren**, panel facing the
   open sky (roughly south, tilted toward latitude if the mount allows). If using an
   external antenna, run it up the mast to the highest clear point, well away from the
   siren head and its conduit.

The P1-Pro is already the weatherproof enclosure, its own charge controller, and its own
battery — there is no box to seal, no panel to wire, and no 5 V input to protect. That is
the point of choosing it.

## Config (MeshCore)

**Flash the Repeater build.** MeshCore makes the role a *firmware choice*, not a setting —
a pole relay runs dedicated Repeater firmware with no phone pairing, just a serial/mesh
admin console. The P1-Pro's XIAO nRF52840 flashes over **USB-C**: use
<https://flasher.meshcore.io/> (Chrome or Edge), or double-tap RST and drag the `.uf2`
onto the drive that appears.

Then configure it over USB serial. `pipx install meshcore-cli`, and use `-r` for direct
repeater mode:

```bash
meshcore-cli -r -s /dev/ttyACM0            # interactive repeater console
```

Settings that matter:

- **Radio preset:** `set preset us` — the stock US/Canada band plan. A wrong preset is
  the single most common reason a new node appears dead.
- **Coding rate 8.** Nebraska runs the stock US preset with CR bumped to 8. Note that CR
  does **not** have to match between nodes — it travels in each packet's header and the
  receiver adapts, so a CR 8 node and a CR 5 node hear each other perfectly. CR 8 buys
  extra reliability on your own marginal links. It is **frequency, bandwidth and
  spreading factor** that must match the state or the node is deaf.
- **2-byte path hashes:** `set path.hash.mode 1`. **Watch the off-by-one — mode 1 means
  2 bytes**, mode 2 means 3 bytes. Requires **firmware v1.14.1 or newer**, on companion
  nodes as well as repeaters.

  Each hop a packet takes is tagged with a hash of the repeater that relayed it. At
  1 byte there are only 256 possible values, so in a growing region two repeaters
  eventually collide and the mesh cannot distinguish their paths. 2 bytes gives 65,536.
  Nebraska has standardized on 2-byte, which is a sign the state network has outgrown
  the 1-byte space — exactly the network this pilot wants to be part of.

  This degrades gracefully rather than failing hard: a 2-byte repeater still relays for
  1-byte nodes. But the region is meant to be uniform, so match it.
- **Name:** `set name MINDEN-3RD-HUBBARD` — this is what shows up on the statewide map.
- **Fixed position:** `set lat <lat>` / `set lon <lon>`. The pole never moves, so set it
  once. This is what puts the relay on the map for everyone else; it is not a live GPS
  fix and costs nothing to keep. (The P1-Pro has GPS, but a repeater does not need a live
  fix — a fixed position is lighter and never drifts.)
- **Admin password:** `password <something-not-the-default>` — this gates remote
  configuration over the mesh. Set it, and record it somewhere the city has it too.
  Leaving the default means anyone in radio range can reconfigure the relay.
- **TX power:** `set tx <dBm>` — leave at the default unless there's a reason.

A repeater periodically broadcasts an *advert* — its name, position, and public key — so
the rest of the mesh learns it exists and can route through it. That is automatic.

Once it's on the pole you can administer it **over the air** from a companion node
rather than climbing back up: `meshcore-cli` in client mode, then `to <repeater-name>`
and the same commands, authenticated with the admin password.

## Winter note — the one real seasonal limitation

The P1-Pro protects its cells (0–50 °C charge window) but that means it **cannot recharge
while the panel is below freezing**. On a normal cold-but-sunny day it discharges through
the morning and tops back up once things warm; the 13.4 Ah pack easily covers that. The
genuine risk is an **extended sub-freezing overcast stretch** — several days where it can
neither warm enough to charge nor see sun. Then it runs down the battery with no
replenishment until conditions break.

For the pilot this is a thing to **watch in the data, not engineer around** — the big pack
is sized to ride typical Nebraska cold snaps, and a rare multi-day deep-freeze brownout is
itself a useful pilot finding. Flag it if the battery telemetry trends toward empty during
a cold overcast run.

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
- [ ] Antenna attached before every power-on. (RP-SMA — confirm the right connector.)
- [ ] Battery near full and the panel charging before it goes up — confirm the solar
      input is working on the bench in sun.
- [ ] After install, a handheld at a distant point in town can reach the mesh **through**
      the repeater (check hop count / that the repeater relayed).
- [ ] Battery holds voltage overnight and recovers through a cloudy day — watch it for a
      few days before trusting it unattended.
- [ ] Nothing on the relay touches or interferes with the siren or its activation.
- [ ] Admin password changed off the default and recorded where the city has it.
- [ ] The relay's advert is visible to the wider Nebraska mesh, not just to local nodes —
      this is the whole point of choosing MeshCore, so confirm it rather than assume it.

## Lightning & grounding — a permanence upgrade, not a pilot part

The pilot node is intentionally not lightning-grounded for the pilot term, and that is a
deliberate, bounded choice. An antenna on a mast is a raised conductor, so it does build
static charge in wind and can pick up a surge from a nearby strike. But adding a coax surge
arrestor and a bonded ground rod is a permanence step that belongs with the permanence
decision and its funding — not with a time-boxed proof. If the pilot node is lost to
weather during the term, it is replaced.

**What does *not* change for the pilot:** the relay stays electrically separate from the
siren — its own antenna, its own power, nothing tapped from or bonded to the siren's
wiring or its ground. The siren's protection is never touched.

**If the pilot succeeds and the node becomes permanent, proper lightning and surge
protection gets added then — by the city, as part of making it permanent.** That means an
inline coax surge arrestor and the mast bonded to a dedicated ground rod, installed to NEC
by the city's electrician or crew and kept separate from the siren's own grounding system.
This is a modest, standard hardening step for any permanent pole-mounted antenna, and it
belongs with the permanence decision. The proposal states this plainly in its Risks &
limitations section and commits to it as Phase 2 hardening.

## Automated data collection (for the pilot report)

The evaluation the proposal promises — uptime, battery through the season,
packet counts, and above all *was the relay reachable* — does not need anyone to
climb the pole or babysit a laptop. A repeater is administrable **over the air**:
any MeshCore companion node in radio range can log in with the admin password and
ask it for status. So the hands-off way to gather the pilot data is a small
always-on collector at home:

1. **A home base node.** A spare MeshCore **companion** node (a Seeed XIAO nRF52840 +
   Wio-SX1262, or similar) plugged by USB into an always-on computer — a Raspberry Pi is
   ideal. It only has to be within radio range of the rooftop repeater, which a rooftop
   relay covering the town almost certainly reaches. This node lives indoors on a desk;
   it is **not** a second roof install. (This is the window historian — see DD-005.)
2. **The polling script.** `tools/poll-repeater.py` in this repo connects to that
   local node, logs in to the repeater over the mesh, requests its status on a
   fixed interval, and appends one row per reading to a CSV:

   ```bash
   pipx install meshcore-cli        # provides the meshcore library
   python3 tools/poll-repeater.py \
       --port /dev/ttyACM0 \
       --repeater MINDEN-3RD-HUBBARD \
       --password "$REPEATER_ADMIN_PW" \
       --csv ~/minden-pilot/status.csv \
       --interval 900               # every 15 minutes
   ```

   Every row carries `reachable` (1/0), uptime, battery millivolts, RX/TX and
   flood/direct packet counts, RSSI/SNR, noise floor, airtime, and error counts.
   A `reachable=0` row is not a crash — it is a recorded outage, which is exactly
   the availability data the report needs. The battery-millivolts column is also
   what surfaces the winter brownout risk above.
3. **Keep it running** under a service manager so it survives reboots. A minimal
   systemd unit (`/etc/systemd/system/minden-pilot-logger.service`):

   ```ini
   [Unit]
   Description=MeshCore pilot repeater logger
   After=network.target

   [Service]
   Environment=REPEATER_ADMIN_PW=change-me
   ExecStart=/usr/bin/python3 /home/pi/Minden-MeshCore-Pilot/tools/poll-repeater.py \
       --port /dev/ttyACM0 --repeater MINDEN-3RD-HUBBARD \
       --csv /home/pi/minden-pilot/status.csv --interval 900
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

   Enable it with `systemctl enable --now minden-pilot-logger` (as root). The CSV
   then charts straight into the interim (~3 month) and final (6 month) reports —
   uptime %, battery vs. time across the season, and traffic — with no ongoing
   effort.

Coverage is the one metric this cannot capture: where the relay reaches is
measured by walking/driving town with a handheld, not polled from a desk.

## Where this goes next

One elevated repeater plus handhelds is hub-and-spoke — a mesh, but a shallow one. Adding
a second elevated node (another siren pole, a water tower, a hilltop) is what gives real
path redundancy and self-healing. That's the grant-funded Phase 2 in the proposal.

Two lessons worth carrying in from operators who have already done this:

- **Siting beats spending.** One operator moved a repeater ~1,200 ft to a spot only
  **30 ft higher** with better sightlines and went from roughly −8 dB to about 0 dB. That
  same person saw no improvement at all from a better antenna and no improvement from a
  purpose-built repeater over a bare node sitting in the yard. Height and geometry are the
  levers; hardware spend is not. (This is *why* the P1-Pro is chosen for ruggedness and
  battery, not for radio performance — the radio is the same as a bare node.)
- **Solar is the easy part.** An 8 W panel held a 2× 18650 bank at 94–95% through a full
  week of rain — lying unmounted on the ground. The P1-Pro's 5 W panel and 4× 18650 pack
  is a bigger buffer than that, so warm-season power is a non-issue; winter is the only
  season to watch (above).

Worth doing early and for free: get the relay onto the **Nebraska mesh community's** map
and tell them it's coming up. Because the state has standardized on MeshCore, a correctly
configured Minden repeater joins the existing network rather than starting a private one —
and their operators are the fastest source of help on coverage, presets, and siting.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
