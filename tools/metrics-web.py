#!/usr/bin/env python3
"""Unauthenticated web view of the cumulative repeater metrics.

Reads the CSV that `poll-repeater.py` appends to and serves a single page of
totals for the pilot: availability, traffic, battery, RF conditions and errors.
Standard library only — no Flask, no build step, nothing to install on the Pi.

    python3 tools/metrics-web.py --csv ~/minden-pilot/status.csv --port 8080

There is NO authentication, by design. Anyone who can reach the port sees the
page. That is fine for these numbers (uptime, packet counts, battery) but do not
add anything sensitive to the CSV on the assumption that the page is private.

Counter handling
----------------
The repeater's counters (nb_recv, sent_flood, airtime, ...) are cumulative since
*its* boot, and it has no battery-backed RTC, so a power cycle resets them to
zero. Naively taking the last row would silently under-report every total after
the first reboot, and naively summing rows would wildly over-report. So totals
are accumulated from per-poll deltas, and a drop in `uptime_s` is treated as a
reboot boundary: the counter restarted, so the new reading is itself the delta.
Reboots are counted and shown, because for this pilot an unexplained repeater
reboot is a finding, not noise.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import html
import ipaddress
import json
import os
import re
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Restart actions are performed by a small root-owned helper, invoked through a
# single NOPASSWD sudoers entry. The web process itself stays unprivileged.
HELPER = "/usr/local/sbin/meshbridge-restart"
BUSID_RE = re.compile(r"^\d+-\d+(\.\d+)*$")

# Counters that only ever climb while the repeater stays up.
COUNTERS = [
    "nb_recv", "nb_sent", "sent_flood", "sent_direct", "recv_flood", "recv_direct",
    "airtime_s", "rx_airtime_s", "full_evts", "direct_dups", "flood_dups", "recv_errors",
]
# Point-in-time gauges.
GAUGES = ["battery_mv", "tx_queue_len", "last_rssi", "last_snr", "noise_floor", "uptime_s"]


def _num(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f


def _parse_ts(v):
    try:
        return dt.datetime.fromisoformat(v)
    except (TypeError, ValueError):
        return None


def usb_busid(tty_path: str) -> str | None:
    """Walk from a tty up to the USB *device* that owns it, e.g. '1-1.2'.

    Unbinding needs the device, not the interface: the interface node is named
    '1-1.2:1.0' and the usb driver will not accept it. So climb until the name
    has no colon in it.
    """
    dev = os.path.realpath(f"/sys/class/tty/{os.path.basename(tty_path)}/device")
    while dev and dev != "/":
        name = os.path.basename(dev)
        if BUSID_RE.match(name) and os.path.exists(f"/sys/bus/usb/devices/{name}"):
            return name
        dev = os.path.dirname(dev)
    return None


def list_radios() -> list[dict]:
    """Serial radios currently attached, with the USB id needed to reset them."""
    out = []
    for link in sorted(glob.glob("/dev/serial/by-id/*")):
        target = os.path.realpath(link)
        try:
            busid = usb_busid(target)
        except OSError:
            busid = None
        out.append({"name": os.path.basename(link), "dev": target, "busid": busid})
    return out


def client_allowed(addr: str, cidrs: list) -> bool:
    """Restart controls are limited to the Pi's own AP subnet (and loopback).

    Enforced here rather than by hiding the buttons: hiding a control in HTML is
    not a restriction, it is a suggestion.
    """
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return False
    if ip.is_loopback:
        return True
    return any(ip in net for net in cidrs)


def run_helper(args: list[str]) -> tuple[bool, str]:
    try:
        p = subprocess.run(["sudo", "-n", HELPER, *args], capture_output=True,
                           text=True, timeout=25)
    except FileNotFoundError:
        return False, "sudo or helper not installed"
    except subprocess.TimeoutExpired:
        return False, "helper timed out"
    if p.returncode != 0:
        return False, (p.stderr or p.stdout or f"exit {p.returncode}").strip()
    return True, (p.stdout or "ok").strip()


def load(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: r.get("timestamp") or "")
    return rows


def summarize(rows: list[dict]) -> dict:
    """Fold the raw poll log into the numbers the pilot actually reports."""
    out = {
        "polls": len(rows),
        "reachable_polls": 0,
        "availability": None,
        "availability_24h": None,
        "first_seen": None,
        "last_poll": None,
        "last_ok": None,
        "current": None,
        "reboots": 0,
        "totals": {k: 0.0 for k in COUNTERS},
        "gauges": {},
        "battery_series": [],
        "reach_series": [],
        "outages": 0,
    }
    if not rows:
        return out

    out["first_seen"] = rows[0].get("timestamp")
    out["last_poll"] = rows[-1].get("timestamp")

    prev_uptime = None
    prev_counters: dict[str, float] = {}
    prev_reachable = None
    now = dt.datetime.now(dt.timezone.utc)

    recent_total = recent_ok = 0
    bat_vals, rssi_vals, snr_vals = [], [], []

    for r in rows:
        reachable = str(r.get("reachable", "0")).strip() in ("1", "true", "True")
        ts = _parse_ts(r.get("timestamp"))

        if ts is not None:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=dt.timezone.utc)
            if (now - ts).total_seconds() <= 86400:
                recent_total += 1
                recent_ok += 1 if reachable else 0
            out["reach_series"].append((ts.isoformat(), 1 if reachable else 0))

        # An outage is a transition into unreachable, not every failed poll —
        # otherwise one long outage reads as dozens of separate incidents.
        if prev_reachable is not None and prev_reachable and not reachable:
            out["outages"] += 1
        prev_reachable = reachable

        if not reachable:
            continue

        out["reachable_polls"] += 1
        out["last_ok"] = r.get("timestamp")
        out["current"] = r

        uptime = _num(r.get("uptime_s"))
        rebooted = uptime is not None and prev_uptime is not None and uptime < prev_uptime
        if rebooted:
            out["reboots"] += 1

        for k in COUNTERS:
            cur = _num(r.get(k))
            if cur is None:
                continue
            prev = prev_counters.get(k)
            if prev is None or rebooted or cur < prev:
                # First sighting, or the counter restarted: the reading IS the delta.
                out["totals"][k] += max(cur, 0.0)
            else:
                out["totals"][k] += cur - prev
            prev_counters[k] = cur

        if uptime is not None:
            prev_uptime = uptime

        bat = _num(r.get("battery_mv"))
        if bat:
            bat_vals.append(bat)
            if ts is not None:
                out["battery_series"].append((ts.isoformat(), bat))
        for src, dest in (("last_rssi", rssi_vals), ("last_snr", snr_vals)):
            v = _num(r.get(src))
            if v is not None:
                dest.append(v)

    if out["polls"]:
        out["availability"] = out["reachable_polls"] / out["polls"]
    if recent_total:
        out["availability_24h"] = recent_ok / recent_total
    if bat_vals:
        out["gauges"]["battery_min_mv"] = min(bat_vals)
        out["gauges"]["battery_max_mv"] = max(bat_vals)
        out["gauges"]["battery_last_mv"] = bat_vals[-1]
    if rssi_vals:
        out["gauges"]["rssi_avg"] = sum(rssi_vals) / len(rssi_vals)
    if snr_vals:
        out["gauges"]["snr_avg"] = sum(snr_vals) / len(snr_vals)
    return out


def fmt_dur(seconds) -> str:
    if seconds is None:
        return "—"
    s = int(seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, _ = divmod(s, 60)
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


def fmt_int(v) -> str:
    return "—" if v is None else f"{int(v):,}"


def sparkline(points, width=520, height=48, invert=False) -> str:
    """Tiny inline SVG. No JS, no external chart library — it has to render on a
    phone connected to the Pi's AP with no internet."""
    vals = [v for _, v in points]
    if len(vals) < 2:
        return '<div class="nodata">not enough readings yet</div>'
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    step = width / (len(vals) - 1)
    pts = []
    for i, v in enumerate(vals):
        y = height - ((v - lo) / span) * (height - 6) - 3
        if invert:
            y = height - y
        pts.append(f"{i * step:.1f},{y:.1f}")
    return (
        f'<svg viewBox="0 0 {width} {height}" preserveAspectRatio="none" role="img">'
        f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )


def bar_strip(points, width=520, height=28) -> str:
    """One bar per poll: reachable or not. The availability story at a glance."""
    if not points:
        return '<div class="nodata">no polls recorded yet</div>'
    n = len(points)
    w = width / n
    bars = []
    for i, (_, ok) in enumerate(points):
        cls = "ok" if ok else "down"
        bars.append(f'<rect class="{cls}" x="{i * w:.2f}" y="0" width="{max(w - 0.5, 0.5):.2f}" height="{height}"/>')
    return (f'<svg class="strip" viewBox="0 0 {width} {height}" preserveAspectRatio="none" '
            f'role="img">{"".join(bars)}</svg>')


def controls_html(radios: list[dict], can_restart: bool, ap_cidr: str) -> str:
    if not can_restart:
        return (f'<section><h2>Restart</h2><div class="nodata">Restart controls are '
                f'only available to clients on the Pi\'s own access point '
                f'(<code>{html.escape(ap_cidr)}</code>). You are viewing from another '
                f'network.</div></section>')

    if radios:
        buttons = "".join(
            f'<form method="post" action="/restart/radio">'
            f'<input type="hidden" name="busid" value="{html.escape(r["busid"] or "")}">'
            f'<button class="btn" {"disabled" if not r["busid"] else ""} '
            f'onclick="return confirm(\'Power-cycle {html.escape(r["name"])}?\\n\\n'
            f'This is the same as unplugging and replugging it. A MeshCore node will '
            f'lose its clock (it has no RTC).\')">Power-cycle</button>'
            f'<span class="dev"><b>{html.escape(r["name"])}</b><br>'
            f'<small>{html.escape(r["dev"])}'
            f'{" · usb " + html.escape(r["busid"]) if r["busid"] else " · no USB id — cannot reset"}'
            f'</small></span></form>'
            for r in radios)
    else:
        buttons = ('<div class="nodata">No serial radios attached. Plug one in and '
                   'reload — nothing to restart yet.</div>')

    return f"""<section><h2>Restart</h2>
{buttons}
<form method="post" action="/restart/pi">
  <button class="btn danger" onclick="return confirm('Reboot the Raspberry Pi?\\n\\nThe access point you are connected through will drop for about a minute.')">Reboot the Pi</button>
  <span class="dev"><b>Raspberry Pi</b><br><small>drops this AP for ~1 min while it comes back</small></span>
</form>
</section>"""


def render(s: dict, csv_path: str, refresh: int,
           radios: list[dict] | None = None, can_restart: bool = False,
           ap_cidr: str = "10.13.37.0/24", notice: str = "") -> str:
    cur = s["current"] or {}
    up = _num(cur.get("uptime_s"))
    bat = s["gauges"].get("battery_last_mv")
    avail = s["availability"]
    avail24 = s["availability_24h"]

    live = bool(s["last_ok"] and s["last_ok"] == s["last_poll"])
    state_cls = "up" if live else ("down" if s["polls"] else "idle")
    state_txt = "REACHABLE" if live else ("UNREACHABLE" if s["polls"] else "NO DATA")

    def pct(v):
        return "—" if v is None else f"{v * 100:.1f}%"

    t = s["totals"]
    cards = [
        ("Availability", pct(avail), f'{s["reachable_polls"]:,} of {s["polls"]:,} polls answered'),
        ("Last 24 h", pct(avail24), "rolling window"),
        ("Outages", f'{s["outages"]:,}', "transitions into unreachable"),
        ("Repeater reboots", f'{s["reboots"]:,}', "detected by uptime resetting"),
        ("Current uptime", fmt_dur(up), "since its last boot"),
        ("Battery", f"{bat / 1000:.2f} V" if bat else "—",
         (f'min {s["gauges"]["battery_min_mv"] / 1000:.2f} V · '
          f'max {s["gauges"]["battery_max_mv"] / 1000:.2f} V') if "battery_min_mv" in s["gauges"] else "no readings"),
    ]

    traffic = [
        ("Packets received", fmt_int(t["nb_recv"])),
        ("Packets sent", fmt_int(t["nb_sent"])),
        ("Flood recv / sent", f'{fmt_int(t["recv_flood"])} / {fmt_int(t["sent_flood"])}'),
        ("Direct recv / sent", f'{fmt_int(t["recv_direct"])} / {fmt_int(t["sent_direct"])}'),
        ("Airtime TX", fmt_dur(t["airtime_s"])),
        ("Airtime RX", fmt_dur(t["rx_airtime_s"])),
        ("Duplicate flood / direct", f'{fmt_int(t["flood_dups"])} / {fmt_int(t["direct_dups"])}'),
        ("Receive errors", fmt_int(t["recv_errors"])),
        ("Queue-full events", fmt_int(t["full_evts"])),
    ]

    rf = [
        ("Last RSSI", f'{cur.get("last_rssi") or "—"} dBm'),
        ("Last SNR", f'{cur.get("last_snr") or "—"} dB'),
        ("Noise floor", f'{cur.get("noise_floor") or "—"}'),
        ("Avg RSSI", f'{s["gauges"]["rssi_avg"]:.1f} dBm' if "rssi_avg" in s["gauges"] else "—"),
        ("Avg SNR", f'{s["gauges"]["snr_avg"]:.1f} dB' if "snr_avg" in s["gauges"] else "—"),
        ("TX queue", cur.get("tx_queue_len") or "—"),
    ]

    def rows(pairs):
        return "".join(
            f'<div class="row"><span>{html.escape(str(k))}</span><b>{html.escape(str(v))}</b></div>'
            for k, v in pairs)

    empty_note = ""
    if not s["polls"]:
        empty_note = (
            '<div class="warn"><b>No readings yet.</b> This page is live, but '
            f'<code>{html.escape(csv_path)}</code> is empty or missing. It fills in once '
            '<code>poll-repeater.py</code> is running against the repeater with a MeshCore '
            'companion node attached to this Pi.</div>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="{refresh}">
<title>Repeater Metrics</title>
<style>
:root{{--bg:#f4f5f1;--card:#fff;--edge:#dcdfd6;--ink:#1e2227;--mut:#5d636b;--ok:#2e7d5b;--down:#c13b2f;--idle:#8a9099;--accent:#31567a}}
@media (prefers-color-scheme:dark){{:root{{--bg:#12151a;--card:#181c22;--edge:#2a3038;--ink:#e6e9ed;--mut:#a0a7b0;--ok:#4fa37d;--down:#e8695c;--idle:#6d747d;--accent:#6e9fd0}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:860px;margin:0 auto;padding:26px 16px 48px}}
h1{{font-size:23px;margin:0 0 2px}}
.sub{{color:var(--mut);font-size:13px;margin:0 0 18px}}
.state{{display:inline-block;padding:3px 11px;border-radius:99px;font-size:12px;font-weight:700;letter-spacing:.08em;color:#fff}}
.state.up{{background:var(--ok)}} .state.down{{background:var(--down)}} .state.idle{{background:var(--idle)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:11px;margin:16px 0}}
.card{{background:var(--card);border:1px solid var(--edge);border-radius:11px;padding:13px 15px}}
.card .k{{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--mut);font-weight:700}}
.card .v{{font-size:25px;font-weight:680;margin:3px 0 1px;font-variant-numeric:tabular-nums}}
.card .n{{font-size:12px;color:var(--mut)}}
section{{background:var(--card);border:1px solid var(--edge);border-radius:11px;padding:15px 17px;margin:14px 0}}
section h2{{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--mut);margin:0 0 9px}}
.row{{display:flex;justify-content:space-between;gap:12px;padding:5px 0;border-bottom:1px solid var(--edge)}}
.row:last-child{{border-bottom:0}}
.row b{{font-variant-numeric:tabular-nums}}
svg{{width:100%;height:auto;display:block;color:var(--accent)}}
.strip rect.ok{{fill:var(--ok)}} .strip rect.down{{fill:var(--down)}}
.nodata{{color:var(--mut);font-size:13px;padding:6px 0}}
.warn{{background:var(--card);border:1px solid var(--edge);border-left:4px solid var(--accent);border-radius:9px;padding:13px 15px;margin:14px 0;font-size:14px}}
code{{background:rgba(128,128,128,.16);padding:1px 5px;border-radius:4px;font-size:12.5px}}
footer{{color:var(--mut);font-size:12px;margin-top:20px;line-height:1.7}}
form{{display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid var(--edge)}}
form:last-child{{border-bottom:0}}
.btn{{flex:none;background:var(--accent);color:#fff;border:0;border-radius:8px;
  padding:9px 15px;font-size:14px;font-weight:640;cursor:pointer;min-width:132px}}
.btn:hover{{filter:brightness(1.08)}}
.btn:disabled{{background:var(--idle);cursor:not-allowed}}
.btn.danger{{background:var(--down)}}
.dev small{{color:var(--mut);font-size:12px;word-break:break-all}}
.notice{{background:var(--card);border:1px solid var(--edge);border-left:4px solid var(--ok);
  border-radius:9px;padding:11px 14px;margin:12px 0;font-size:14px}}
.notice.bad{{border-left-color:var(--down)}}
</style></head><body><div class="wrap">
<h1>MeshCore Repeater — Cumulative Metrics</h1>
<p class="sub"><span class="state {state_cls}">{state_txt}</span>
&nbsp;last poll {html.escape(str(s["last_poll"] or "never"))} · first {html.escape(str(s["first_seen"] or "—"))}</p>
{notice}
{empty_note}
<div class="grid">{"".join(
    f'<div class="card"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}</div>'
    f'<div class="n">{html.escape(n)}</div></div>' for k, v, n in cards)}</div>
<section><h2>Reachability — one bar per poll</h2>{bar_strip(s["reach_series"])}</section>
<section><h2>Battery</h2>{sparkline(s["battery_series"])}</section>
<section><h2>Traffic totals (reboot-adjusted)</h2>{rows(traffic)}</section>
<section><h2>RF conditions</h2>{rows(rf)}</section>
{controls_html(radios or [], can_restart, ap_cidr)}
<footer>
Totals are accumulated from per-poll deltas. The repeater's counters reset when it
loses power, so a drop in uptime is treated as a reboot boundary — without that,
every total would under-report after the first power cycle.<br>
Source <code>{html.escape(csv_path)}</code> · refreshes every {refresh}s · JSON at <code>/data.json</code> ·
no authentication.
</footer>
</div></body></html>"""


def make_handler(csv_path: str, refresh: int, cidrs: list, ap_cidr: str):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _allowed(self) -> bool:
            return client_allowed(self.client_address[0], cidrs)

        def _page(self, notice: str = "", code: int = 200):
            s = summarize(load(csv_path))
            body = render(s, csv_path, refresh, list_radios(), self._allowed(),
                          ap_cidr, notice).encode()
            self._send(code, body, "text/html; charset=utf-8")

        def _same_origin(self) -> bool:
            """Reject cross-site form posts.

            The controls are unauthenticated and reachable from the AP, so without
            this a page in any other tab could submit the reboot form on the
            viewer's behalf. Browsers always send Origin on a form POST; a missing
            Origin means it did not come from a browser form (curl, etc.), which
            is already limited by the subnet check.
            """
            origin = self.headers.get("Origin")
            if not origin:
                return True
            try:
                return urllib.parse.urlparse(origin).netloc == self.headers.get("Host")
            except ValueError:
                return False

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            try:
                if path in ("/", "/index.html"):
                    self._page()
                elif path == "/data.json":
                    s = summarize(load(csv_path))
                    s.pop("current", None)
                    self._send(200, json.dumps(s, indent=2, default=str).encode(),
                               "application/json; charset=utf-8")
                elif path == "/healthz":
                    self._send(200, b"ok\n", "text/plain; charset=utf-8")
                else:
                    self._send(404, b"not found\n", "text/plain; charset=utf-8")
            except Exception as exc:  # a bad CSV row must not take the page down
                self._send(500, f"error: {exc}\n".encode(), "text/plain; charset=utf-8")

        def do_POST(self):
            path = self.path.split("?", 1)[0]
            if not path.startswith("/restart/"):
                self._send(404, b"not found\n", "text/plain; charset=utf-8")
                return
            # Subnet check first: never even parse a body from a client that is
            # not permitted to act.
            if not self._allowed():
                self._send(403, b"restart is limited to the Pi's own AP subnet\n",
                           "text/plain; charset=utf-8")
                return
            if not self._same_origin():
                self._send(403, b"cross-origin request rejected\n",
                           "text/plain; charset=utf-8")
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
                form = urllib.parse.parse_qs(self.rfile.read(min(length, 4096)).decode())

                if path == "/restart/pi":
                    ok, msg = run_helper(["pi"])
                    note = ("The Pi is rebooting. This access point drops for about a "
                            "minute, then reconnect and reload.") if ok else f"Reboot failed: {msg}"
                elif path == "/restart/radio":
                    busid = (form.get("busid") or [""])[0]
                    if not BUSID_RE.match(busid):
                        self._page('<div class="notice bad">Invalid USB id.</div>', 400)
                        return
                    ok, msg = run_helper(["usb", busid])
                    note = (f"Power-cycled USB {html.escape(busid)}. It re-enumerates in a "
                            f"few seconds; a MeshCore node comes back with its clock reset."
                            ) if ok else f"Power-cycle failed: {html.escape(msg)}"
                else:
                    self._send(404, b"not found\n", "text/plain; charset=utf-8")
                    return

                cls = "notice" if ok else "notice bad"
                self._page(f'<div class="{cls}">{note}</div>')
            except Exception as exc:
                self._page(f'<div class="notice bad">Error: {html.escape(str(exc))}</div>', 500)

        def log_message(self, *a):  # keep the journal readable
            pass

    return Handler


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=os.path.expanduser("~/minden-pilot/status.csv"),
                    help="CSV written by poll-repeater.py")
    ap.add_argument("--host", default="0.0.0.0", help="bind address (default: all interfaces)")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--refresh", type=int, default=60, help="page auto-refresh seconds")
    ap.add_argument("--restart-from", default="10.13.37.0/24",
                    help="comma-separated CIDRs allowed to use the restart controls "
                         "(loopback is always allowed). Metrics stay readable to all.")
    args = ap.parse_args()

    cidrs = [ipaddress.ip_network(c.strip()) for c in args.restart_from.split(",") if c.strip()]
    srv = ThreadingHTTPServer((args.host, args.port),
                              make_handler(args.csv, args.refresh, cidrs, args.restart_from))
    print(f"serving {args.csv} on http://{args.host}:{args.port}/  (no authentication)", flush=True)
    print(f"restart controls limited to: {args.restart_from} (+loopback)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
