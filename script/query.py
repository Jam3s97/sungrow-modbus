#!/usr/bin/env python3

"""Query a Sungrow SHx hybrid inverter over Modbus and print every value.

Connects over Modbus TCP (the LAN/Wi-Fi dongle, or a serial gateway) or a
serial/USB port, reads the whole device once, and dumps every subsystem's
values to the terminal. Handy for checking a real inverter without Home
Assistant.

The library only needs the connection protocol; this script selects the
pymodbus backend, so install the ``cli`` extra first::

    pip install "sungrow-modbus[cli]"
    python script/query.py tcp 192.168.1.50
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from modbus_connection import (
    ModbusConnection,
    ModbusError,
    ModbusSerialParams,
    ModbusTcpParams,
)
from modbus_connection.cli_helper import CountingUnit, print_component

from sungrow_modbus import SungrowSHx

# (label, attribute name on SungrowSHx) — the order in which sections are printed.
SECTIONS: list[tuple[str, str]] = [
    ("Device", "info"),
    ("PV strings", "pv"),
    ("Inverter", "status"),
    ("Battery", "battery"),
    ("Battery settings", "battery_settings"),
    ("Grid", "grid"),
    ("Backup output", "backup"),
    ("Energy totals", "energy"),
    ("Controls", "controls"),
]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="transport", required=True)

    # Shared options available on each transport (so --unit can follow the host).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--unit",
        type=int,
        default=1,
        help="Modbus unit/station address (default: 1)",
    )
    tcp = sub.add_parser(
        "tcp",
        parents=[common],
        help="connect over Modbus TCP (the inverter's LAN/Wi-Fi dongle)",
    )
    tcp.add_argument("host", help="hostname or IP of the inverter/dongle")
    tcp.add_argument("--port", type=int, default=502, help="TCP port (default: 502)")
    tcp.add_argument(
        "--framer",
        choices=("rtu", "socket"),
        default="socket",
        help="wire framing (default: socket, i.e. native Modbus TCP)",
    )
    serial = sub.add_parser(
        "serial",
        parents=[common],
        help="connect over a serial/USB port (RS485 gateway)",
    )
    serial.add_argument("device", help="serial device, e.g. /dev/ttyUSB0")
    serial.add_argument("--baudrate", type=int, default=9600, help="default: 9600")
    serial.add_argument("--parity", choices=("N", "E", "O"), default="N")
    serial.add_argument("--stopbits", type=int, choices=(1, 2), default=1)
    serial.add_argument("--bytesize", type=int, choices=(7, 8), default=8)
    return parser.parse_args(argv)


def _connection(args: argparse.Namespace) -> ModbusConnection:
    """Build the connection described by the arguments. Performs no I/O."""
    # Imported here so the module loads (and --help works) without a backend.
    from modbus_connection.pymodbus import PymodbusConnection

    if args.transport == "serial":
        return PymodbusConnection(
            ModbusSerialParams(
                device=args.device,
                baudrate=args.baudrate,
                parity=args.parity,
                stopbits=args.stopbits,
                bytesize=args.bytesize,
            )
        )
    return PymodbusConnection(
        ModbusTcpParams(host=args.host, port=args.port, framer=args.framer)
    )


def _print(device: SungrowSHx) -> None:
    for label, attr in SECTIONS:
        print()
        print_component(getattr(device, attr), title=label)
    print()
    print("Derived values")
    print(f"  is_pv_generating: {device.is_pv_generating}")
    print(f"  is_battery_charging: {device.is_battery_charging}")
    print(f"  is_battery_discharging: {device.is_battery_discharging}")
    print(f"  is_importing_from_grid: {device.is_importing_from_grid}")
    print(f"  is_exporting_to_grid: {device.is_exporting_to_grid}")
    print(f"  battery_level_nominal: {device.battery_level_nominal}")
    print(f"  battery_usable_charge_kwh: {device.battery_usable_charge_kwh}")
    print(
        f"  battery_health_rated_charge_kwh: {device.battery_health_rated_charge_kwh}"
    )


async def _run(args: argparse.Namespace) -> int:
    connection = _connection(args)
    try:
        await connection.connect()
    except ModbusError as err:
        print(f"Could not connect: {err}", file=sys.stderr)
        return 1
    counting = CountingUnit(connection.for_unit(args.unit))
    try:
        device = SungrowSHx(counting)
        start = time.monotonic()
        await device.async_update()
        elapsed = time.monotonic() - start
    except ModbusError as err:
        print(f"Error reading device: {err}", file=sys.stderr)
        return 1
    finally:
        await connection.close()
    _print(device)
    print(f"\nQueried in {elapsed * 1000:.0f} ms ({counting.reads} Modbus reads)")
    return 0


def main() -> int:
    return asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
