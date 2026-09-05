# `sungrow-modbus` Python library

[![CI](https://github.com/Jam3s97/sungrow-modbus/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/Jam3s97/sungrow-modbus/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sungrow-modbus.svg)](https://pypi.org/project/sungrow-modbus/)
[![Python](https://img.shields.io/pypi/pyversions/sungrow-modbus.svg)](https://pypi.org/project/sungrow-modbus/)
[![License](https://img.shields.io/github/license/Jam3s97/sungrow-modbus.svg)](LICENSE)

`sungrow-modbus` is an asynchronous, transport-independent Python library for reading and controlling **Sungrow SHx** hybrid inverters (and compatible battery systems) over Modbus.

The library was developed as the backend for a Home Assistant integration. As it is kept independent of Home Assistant, it can also be used by other Python applications and projects.

## Purpose and scope

`sungrow-modbus` is intended for operational monitoring and day-to-day control of an already commissioned Sungrow SHx inverter: PV generation, battery state and charge/discharge control, grid import/export, backup output, and the site-level EMS/export/load-management settings. It is not a commissioning tool and does not attempt to reproduce every OEM parameter available through iSolarCloud or the installer app.

The library:

* contains the inverter-specific data model, including register addresses, data types, scaling, and the neutral metadata (unit, min/max, step, enum options, writable state) needed to build a UI or automation on top of it,

* groups related registers into subsystems (`info`, `pv`, `status`, `battery`, `battery_settings`, `grid`, `backup`, `energy`, `controls`) and pools their reads into as few Modbus round trips as the register layout allows,

* adds a small number of computed properties for values Sungrow does not expose directly but that are simple, well-defined functions of raw registers (per-string/per-phase power, charge/discharge power split, import/export power split, SoC rescaled into the configured min/max band, usable and health-rated battery capacity),

* does **not** create or own the Modbus transport. Applications using the library provide a [`modbus_connection.ModbusUnit`](https://pypi.org/project/modbus-connection/) and may use any backend supported by `modbus-connection` (pymodbus, tmodbus, ...).

An example script `script/query.py` shows how to build an application that queries a real inverter over Modbus/TCP or a serial/RS485 gateway.

## Supported devices

Built from the Sungrow SHx register map (residential hybrid inverters with an SBR-series or compatible battery attached). The register set matches the SH3.0RS through SH25T range; older/other Sungrow families (single-phase string-only inverters, SGxxxRT, SGxxxHX) are not covered.

## Data provided by the library

* controller identity: model (decoded from the device type code), serial number, rated output, firmware/protocol versions,

* PV string voltage, current, and computed power per MPPT (up to 4 strings), plus total DC power,

* inverter AC output: per-phase voltage/current/power, reactive power, power factor, temperature, running-state code, and start/stop control,

* battery telemetry: power (with charging/discharging split), voltage, current, level, state of health, temperature, rated capacity; plus derived nominal SoC and usable/health-rated stored energy once the configured min/max SoC band is known,

* battery settings and control: min/max SoC, reserved backup SoC, forced charge/discharge command and power, max charge/discharge power, charge/discharge start-power thresholds,

* grid meter: signed active power (with import/export split), per-phase voltage/current/power, frequency, accepted export-limit range,

* backup (EPS) output power, per phase and total,

* daily and lifetime energy counters for PV generation, grid import/export, battery charge/discharge, and direct PV consumption, plus a derived daily/lifetime household-consumption figure,

* site controls: EMS mode, load adjustment mode (+ enable), export power limit (+ enable), backup mode enable, active power limitation,

* neutral datapoint metadata (register number, unit, scale-adjusted limits, enum options, writable state) attached to every field for building integrations without hard-coding the register map twice.

## Testing and validation

The test suite runs entirely against the in-memory mock backend that ships with `modbus-connection` -- there is no dependency on a real inverter, network, or server to run CI. Every subsystem has read coverage, and every writable field has a corresponding write test asserting the correct scaled/encoded value lands on the wire.

```bash
script/run_checks.sh   # install deps, lint, type/format check, test, build
script/format_code.sh  # apply Ruff formatting and safe fixes
```

## Quick start

```python
import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.pymodbus import PymodbusConnection
from sungrow_modbus import SungrowSHx


async def main() -> None:
    connection = PymodbusConnection(ModbusTcpParams(host="192.168.1.50", port=502))
    await connection.connect()
    try:
        inverter = SungrowSHx(connection.for_unit(1))
        await inverter.async_update()
        print(inverter.info.model, inverter.pv.mppt1_power, "W")
        print("Battery:", inverter.battery.level, "%", "charging" if inverter.is_battery_charging else "idle")
    finally:
        await connection.close()


asyncio.run(main())
```

## Documentation, development and contribution guidelines

Detailed architecture, usage examples, datapoint behavior, and development setup are documented in the project wiki. Branching follows the same `develop`-first workflow enforced by `.github/workflows/enforce-develop.yml`: feature branches and pull requests target `develop`; `main` only receives merges from `develop` for tagged releases.

Support and documentation specific to the Home Assistant integration are maintained separately, alongside the `custom_components/sungrow_shx` HACS package and the Home Assistant core integration built on top of this library.
