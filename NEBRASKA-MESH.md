# Nebraska Mesh — the network this pilot joins

[Nebraska Mesh](https://www.nebraskamesh.net/) is the volunteer-run, statewide MeshCore
network. **Interoperating with it is the entire reason this pilot chose MeshCore**, so
their published standards govern our configuration, not the other way around.

Their materials are linked here rather than copied into this repo. They maintain them;
we should read the current version rather than a snapshot that silently goes stale.

## Directly useful to this proposal

| Resource | Why it matters here |
| --- | --- |
| [Host a Node](https://www.nebraskamesh.net/property-owner-faq.html) | A property-owner FAQ for people being asked to host a repeater. This is the same conversation we are having with the city, from the host's side. Read it before the council meeting — it anticipates the objections. |
| [Repeater do's and don'ts (PDF)](https://www.nebraskamesh.net/resources/nebraska-mesh-repeater-dos-and-donts.pdf) | Siting guidance from people who have already placed nodes across the state. Feeds the site survey. |
| [One-pager (PDF)](https://www.nebraskamesh.net/resources/nebraska-mesh-onepager.pdf) | Plain-language explanation of the network. Useful as a leave-behind for council members. |
| [Convention flyer (PDF)](https://www.nebraskamesh.net/resources/nebraska-mesh-convention-flyer.pdf) | Outreach material covering gear and settings for newcomers. |
| [Help & setup](https://www.nebraskamesh.net/help.html) | **Canonical radio settings**, firmware guide, and the repeater naming scheme. |
| [Etiquette](https://www.nebraskamesh.net/mesh-etiquette.html) | Norms for operating on a shared volunteer network. |
| [Resources index](https://www.nebraskamesh.net/resources.html) | Everything above, plus presentation templates. |

They also run a Discord, a network map, and an analyzer, all linked from their home page.

## Settings that govern our build

Recorded in full in `REPEATER-BUILD.md`. Summarised here because getting them wrong is
the single most likely way this pilot quietly fails:

| Setting | Value |
| --- | --- |
| Frequency | 910.525 MHz |
| Bandwidth | 62.5 kHz |
| Spreading factor | 7 |
| Coding rate | 8 |
| Path hash | 2-byte (`set path.hash.mode 1`) |
| Firmware | v1.14 minimum, v1.15.0 current |

**These are not MeshCore's stock US defaults.** The default region preset uses a much
wider bandwidth and a higher spreading factor. A node left on the stock preset is deaf to
the state network while appearing to work perfectly on the bench.

They have changed twice in the past year (bandwidth narrowed Oct 2025, spreading factor
updated 31 May 2026), so **verify against their help page before install** rather than
trusting this file.

## Credit

This pilot is possible because a volunteer group already did the hard part: agreeing on
standards, publishing them clearly, and building a backbone across the state one node at
a time. Minden's relay is a node on their network, not a network of its own.

---

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
