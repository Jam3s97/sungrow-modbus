"""End-to-end read of every subsystem."""

from __future__ import annotations

from sungrow_modbus import SungrowSHx


async def test_async_update_populates_every_component(device: SungrowSHx) -> None:
    assert device.info.rated_output_power == 10000
    assert device.pv.mppt1_voltage == 350.0
    assert device.status.phase_a_voltage == 230.0
    assert device.battery.voltage == 485.0
    assert device.battery_settings.max_soc == 90.0
    assert device.grid.frequency == 50.01
    assert device.backup.total_power == 0
    assert device.energy.daily_pv_generation == 12.5
    assert device.controls.ems_mode is not None


async def test_components_are_polled_as_a_group(device: SungrowSHx) -> None:
    assert set(device.components) == {
        device.info,
        device.pv,
        device.status,
        device.battery,
        device.battery_settings,
        device.grid,
        device.backup,
        device.energy,
        device.controls,
    }
