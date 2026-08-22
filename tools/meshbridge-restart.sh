#!/usr/bin/env bash
# Privileged helper for the metrics page's restart controls.
#
# Installed as /usr/local/sbin/meshbridge-restart (root:root 0755) and reachable
# from the unprivileged web process through exactly one NOPASSWD sudoers entry.
# The web process never gets general root — it can run this and nothing else.
#
#   meshbridge-restart pi
#   meshbridge-restart usb 1-1.2
#
# Every argument is validated here rather than trusted from the caller: this is
# the security boundary, and the caller is an unauthenticated web page.
set -euo pipefail

usage() { echo "usage: meshbridge-restart {pi|usb <busid>}" >&2; exit 64; }

case "${1:-}" in
  pi)
    logger -t meshbridge-restart "reboot requested via metrics page"
    # Deferred so the HTTP response reaches the browser before the box goes down;
    # otherwise the user sees a connection error and cannot tell whether it worked.
    systemd-run --on-active=3 --unit=meshbridge-reboot-once /usr/sbin/reboot >/dev/null 2>&1
    echo "reboot scheduled"
    ;;

  usb)
    id="${2:-}"
    # Strict allow-list. Anything with a slash, colon or '..' is rejected before
    # it can reach a sysfs path.
    [[ "$id" =~ ^[0-9]+-[0-9]+(\.[0-9]+)*$ ]] || { echo "invalid usb id" >&2; exit 2; }
    [[ -e "/sys/bus/usb/devices/$id" ]] || { echo "no such usb device: $id" >&2; exit 3; }

    logger -t meshbridge-restart "power-cycling USB $id"
    printf '%s' "$id" > /sys/bus/usb/drivers/usb/unbind
    sleep 2
    printf '%s' "$id" > /sys/bus/usb/drivers/usb/bind

    # Give the device a moment to re-enumerate so the page can report honestly.
    for _ in $(seq 1 10); do
      [[ -e "/sys/bus/usb/devices/$id" ]] && { echo "power-cycled $id"; exit 0; }
      sleep 1
    done
    echo "power-cycled $id, but it has not re-enumerated yet" >&2
    exit 4
    ;;

  *) usage ;;
esac
