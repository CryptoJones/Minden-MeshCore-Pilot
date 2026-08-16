#!/usr/bin/env python3
"""Poll a MeshCore repeater over the air and log its status to CSV.

Runs on an always-on computer at home (a Raspberry Pi, a spare PC) with a
MeshCore *companion* node plugged in over USB. It periodically asks the rooftop
repeater for its status over the mesh — no climbing the pole, no second roof
node — and appends one row per reading to a CSV you can chart for the pilot
report: uptime, battery, packet counts, RF conditions, and (most importantly)
whether the repeater answered at all, which is your availability/uptime metric.

Requires the `meshcore` Python package:

    pipx install meshcore-cli      # provides the library
    # or:  pip install meshcore

Example:

    python3 tools/poll-repeater.py \
        --port /dev/ttyACM0 \
        --repeater MINDEN-3RD-HUBBARD \
        --password "$REPEATER_ADMIN_PW" \
        --csv ~/minden-pilot/status.csv \
        --interval 900            # every 15 minutes

Run it under systemd or `nohup ... &` so it keeps logging unattended. A row with
reachable=0 means the poll timed out — that is real data (an outage), so the
script records it rather than crashing.
"""
import argparse
import asyncio
import csv
import datetime
import os
import sys

try:
    from meshcore import MeshCore
except ImportError:
    sys.exit("The 'meshcore' package is required:  pipx install meshcore-cli  (or pip install meshcore)")

FIELDS = [
    "timestamp", "reachable",
    "uptime_s", "battery_mv", "tx_queue_len",
    "nb_recv", "nb_sent",
    "sent_flood", "sent_direct", "recv_flood", "recv_direct",
    "last_rssi", "last_snr", "noise_floor",
    "airtime_s", "rx_airtime_s",
    "full_evts", "direct_dups", "flood_dups", "recv_errors",
]


def append_row(path: str, row: dict) -> None:
    new = not os.path.exists(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in FIELDS})


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


async def poll_once(args) -> dict:
    """One reading. Returns a CSV row dict; reachable=0 on any failure."""
    row = {"timestamp": now_iso(), "reachable": 0}
    mc = None
    try:
        mc = await MeshCore.create_serial(args.port, args.baud)
        if mc is None:
            print(f"{row['timestamp']}  local node not responding on {args.port}", file=sys.stderr)
            return row

        await mc.ensure_contacts()
        repeater = mc.get_contact_by_name(args.repeater)
        if repeater is None:
            print(f"{row['timestamp']}  repeater '{args.repeater}' not in contacts yet "
                  f"(has it advertised? is it in range?)", file=sys.stderr)
            return row

        if args.password:
            login = await mc.commands.send_login_sync(repeater, args.password)
            if login is None:
                print(f"{row['timestamp']}  login to '{args.repeater}' failed/timed out", file=sys.stderr)
                return row

        status = await mc.commands.req_status_sync(repeater)
        if not status:
            print(f"{row['timestamp']}  no status reply from '{args.repeater}' (likely offline)", file=sys.stderr)
            return row

        row.update({
            "reachable": 1,
            "uptime_s": status.get("uptime"),
            "battery_mv": status.get("bat"),
            "tx_queue_len": status.get("tx_queue_len"),
            "nb_recv": status.get("nb_recv"),
            "nb_sent": status.get("nb_sent"),
            "sent_flood": status.get("sent_flood"),
            "sent_direct": status.get("sent_direct"),
            "recv_flood": status.get("recv_flood"),
            "recv_direct": status.get("recv_direct"),
            "last_rssi": status.get("last_rssi"),
            "last_snr": status.get("last_snr"),
            "noise_floor": status.get("noise_floor"),
            "airtime_s": status.get("airtime"),
            "rx_airtime_s": status.get("rx_airtime"),
            "full_evts": status.get("full_evts"),
            "direct_dups": status.get("direct_dups"),
            "flood_dups": status.get("flood_dups"),
            "recv_errors": status.get("recv_errors"),
        })
        return row
    except Exception as exc:  # never let one bad poll kill the loop
        print(f"{row['timestamp']}  poll error: {exc}", file=sys.stderr)
        return row
    finally:
        if mc is not None:
            try:
                await mc.disconnect()
            except Exception:
                pass


async def main_async(args) -> None:
    while True:
        row = await poll_once(args)
        append_row(args.csv, row)
        state = "OK" if row["reachable"] else "UNREACHABLE"
        bat = row.get("battery_mv")
        up = row.get("uptime_s")
        print(f"{row['timestamp']}  {state}"
              + (f"  battery={bat/1000:.2f}V  uptime={up}s" if row["reachable"] and bat else ""))
        if args.once:
            return
        await asyncio.sleep(args.interval)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True, help="serial port of the LOCAL companion node, e.g. /dev/ttyACM0")
    ap.add_argument("--repeater", required=True, help="repeater name as advertised, e.g. MINDEN-3RD-HUBBARD")
    ap.add_argument("--password", default=os.environ.get("REPEATER_ADMIN_PW", ""),
                    help="repeater admin password (or set REPEATER_ADMIN_PW). Omit if status needs no login.")
    ap.add_argument("--csv", default="status.csv", help="output CSV path (default: status.csv)")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--interval", type=int, default=900, help="seconds between polls (default: 900 = 15 min)")
    ap.add_argument("--once", action="store_true", help="poll a single time and exit")
    args = ap.parse_args()

    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
