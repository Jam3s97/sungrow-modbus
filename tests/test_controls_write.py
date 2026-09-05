"""Writing to holding-register control fields."""

from __future__ import annotations

from sungrow_modbus import EmsMode, ForcedChargeDischargeCommand, SungrowSHx


async def test_write_ems_mode(device: SungrowSHx, loaded_unit) -> None:
    await device.controls.write("ems_mode", EmsMode.FORCED_MODE)
    assert loaded_unit.holding[13049] == int(EmsMode.FORCED_MODE)


async def test_write_forced_charge_discharge_command(
    device: SungrowSHx, loaded_unit
) -> None:
    await device.battery_settings.write(
        "forced_charge_discharge_command",
        ForcedChargeDischargeCommand.FORCED_CHARGE,
    )
    assert loaded_unit.holding[13050] == int(ForcedChargeDischargeCommand.FORCED_CHARGE)


async def test_write_max_soc_applies_scale(device: SungrowSHx, loaded_unit) -> None:
    await device.battery_settings.write("max_soc", 95.0)
    assert loaded_unit.holding[13057] == 950


async def test_start_and_stop_write_the_control_register(
    device: SungrowSHx, loaded_unit
) -> None:
    await device.async_start()
    assert loaded_unit.holding[12999] == 0xCF

    await device.async_stop()
    assert loaded_unit.holding[12999] == 0xCE
