# Coverage node build — the $35 "People's Repeater"

Build sheet for the **cheap, many** tier of the mesh (DD-006): a solar MeshCore
repeater built around a gutted solar garden light. These are **not** the pole
node — the siren pole gets the sealed, weather-rated SenseCAP P1-Pro. These are
the accessible coverage nodes that give the mesh its density: neighbours' roofs,
fence posts, sheds. Cheap enough to scatter, replaceable when one dies.

Design and STL by **Black Flag Civilian** —
["A $35 Solar Mesh Node Anyone Can Build"](https://www.youtube.com/watch?v=yAmINEghCOc),
[STL on Printables](https://www.printables.com/model/1768397-the-peoples-repeater-affordable-solar-mesh-repeate)
(free). We are building **two** as the first coverage pair / bench units.

> **Not the pole, and not winter-unattended.** The garden-light donor and the
> CN3065 charger have no low-temperature charge cutoff. Lithium cannot be charged
> below 0 °C without permanent damage, and Minden sees −10 °C. These nodes are
> warm-season coverage and bench-validation hardware. The node that must survive a
> Nebraska winter on a pole is the SenseCAP (see DD-006 and `REPEATER-BUILD.md`).

## Bill of materials (per node × 2)

| Part | Source | Status |
| --- | --- | --- |
| Radio: **Seeed XIAO nRF52840 + Wio-SX1262** kit | Seeed | ✅ ordered (2 kits) |
| Solar charge controller: **HiLetgo CN3065** (2-pack, ~$6.49) | Amazon wishlist | ✅ listed |
| **JST PH2.0** connector kit (smseace, 30-pc, ~$7.99) | Amazon wishlist | ✅ listed |
| Donor: **Harbor Breeze 60-lumen 1 W solar spot light** ×2 (~$15 ea) | Lowe's, Lincoln (pickup) | ✅ in cart — donates panel + housing + 18650 bay |
| Enclosure: **ASA print** of the People's Repeater hub ×2 | Al B, Lincoln | ✅ printing |
| Antenna + **SMA bulkhead pigtail**: DIYmall 6-pc 915 MHz U.FL→SMA-female (`B084KVYBH5`) | Amazon | ⬜ to add to wishlist |
| **Button-top 18650** ×2 (real-brand cell) | Check Zhiyun Crane gimbal first; Amazon as fallback | 🔍 possibly on hand |

The radio is the low-power nRF52840 — the right chip for solar, unlike an ESP32
class part. One of the two ordered kits per node.

## Lincoln trip — do the fit check here

Lowe's pickup and Al B are both in Lincoln, so the one trip collects the two
garden lights **and** the two ASA hubs. Use it to verify fit **before Al prints
the second hub**:

- [ ] **Housing check.** The STL pocket is cut for the Harbor Breeze donor. Ours
      is the **spot light** variant — confirm its panel housing actually seats in
      the ASA print. If the spotlight housing differs from the model's donor, this
      is the moment to catch it, together, with a real light in hand — not after
      two prints and two gutted lights.

## Pre-gut check

- [ ] **Meter the donor panel** in sun before cutting both lights open. It should
      read roughly **5–6 V** — the input range the CN3065 wants. A ~1 W Harbor
      Breeze should be fine; a path-light-class ~1.2 V panel would not charge an
      18650 through this charger. Check the first before gutting the second.

## Battery notes

- **Button top, not flat top** — flat-tops won't seat in the donor bay (per the
  build video).
- **Real-brand cell** (Samsung/LG/Sony-Murata or a reputable rewrap). Ignore any
  "9900 mAh" listing — genuine 18650s top out near 3500 mAh. The node sips power,
  so capacity is a fake-detector here, not a runtime concern.
- **Protected vs unprotected length.** Protected button-tops run ~69 mm;
  unprotected ~65 mm. The CN3065 gives no low-voltage cutoff, so protected is
  electrically nicer — **but only if it fits the bay.** Measure the Harbor Breeze
  bay before committing to protected cells.
- **Possible free source: the Zhiyun Crane gimbal.** Two 18650s may already be sitting
  in the unused handheld camera stabiliser. Before buying, verify: (1) the label
  actually reads `18650` (not a 26650 or a sealed proprietary pack); (2) they're
  **button-top**, not flat-top — flat-tops won't seat in the donor bay; (3) they
  still hold voltage after sitting unused (a cell that won't come up off a slow
  charge gets recycled, not deployed). Pass all three and the battery line is
  sourced for free.

## Antenna notes

- The Wio-SX1262 has a **U.FL / IPEX** socket. The chain is
  `U.FL (radio) → coax → SMA-female bulkhead (enclosure wall) → SMA-male antenna`.
- **SMA, not RP-SMA.** They look identical and don't mate. Standard LoRa antennas
  are SMA male, so you want an **SMA-female** bulkhead. The DIYmall kit above ships
  antenna + pigtail with genders pre-matched, which sidesteps the mistake.
- **Attach the antenna before applying power.** Powering a LoRa PA into no load
  can damage the transmitter.

## Firmware

Flash **MeshCore repeater** — the `xiao_nrf52_repeater` target from
<https://flasher.meshcore.io/>. On the nRF52840 it's drag-and-drop: double-tap
reset, a drive appears, drop the `.uf2` on it. No toolchain.

- Set the region to **US 915 MHz** and confirm the exact preset against what the
  Nebraska mesh runs (see `HARDWARE.md`).
- Bring it up on the bench and confirm it joins the mesh from a second node before
  it goes outside.

## Assembly (summary — full walk-through in the build video)

1. Gut the Harbor Breeze: keep the panel, its housing, and the 18650 bay; discard
   the LED/driver board.
2. Solder the PH2.0 pigtails between panel, CN3065, battery, and the radio's power
   input.
3. Mount the radio, charger, and battery in the ASA hub; run the U.FL→SMA pigtail
   out through the bulkhead hole.
4. Attach the external antenna, **then** power on.
5. Seat the panel housing into the hub; mount to a fence, post, or mast (the STL
   has slots for screws and zip ties).

## How these fit the pilot

- **Tier:** coverage / density (DD-006), not the pole.
- **Also the bench units:** build one first to validate MeshCore firmware and the
  window historian's polling loop end-to-end before anything goes up a pole.
- **Chip reuse note:** the nRF52840's microamp sleep is the reason these work on a
  tiny salvaged panel. That same low-power trait is wasted on the mains-powered
  window radios — so if radios ever get reshuffled, these two belong on solar, not
  in the window.
