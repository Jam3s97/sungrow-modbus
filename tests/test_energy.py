"""Derived household consumption from the daily energy counters."""

from __future__ import annotations

from sungrow_modbus import SungrowSHx


async def test_daily_consumed_energy_is_derived(device: SungrowSHx) -> None:
    # pv(12.5) - exported(4.5) + imported(1.0)
    # - battery_charge(3.5) + battery_discharge(2.0)
    assert device.energy.daily_pv_generation == 12.5
    assert device.energy.daily_exported_energy == 4.5
    assert device.energy.daily_imported_energy == 1.0
    assert device.energy.daily_battery_charge == 3.5
    assert device.energy.daily_battery_discharge == 2.0
    assert device.energy.daily_consumed_energy == round(12.5 - 4.5 + 1.0 - 3.5 + 2.0, 2)


async def test_missing_counter_yields_none(loaded_unit) -> None:
    from sungrow_modbus import SungrowSHx as _SungrowSHx

    loaded_unit.input[13044] = 65535  # daily_exported_energy's configured NaN sentinel
    dev = _SungrowSHx(loaded_unit)
    await dev.async_update()
    assert dev.energy.daily_exported_energy is None
    assert dev.energy.daily_consumed_energy is None
