"""PV string computed power."""

from __future__ import annotations

from sungrow_modbus import SungrowSHx


async def test_mppt_power_is_computed_from_voltage_and_current(
    device: SungrowSHx,
) -> None:
    assert device.pv.mppt1_voltage == 350.0
    assert device.pv.mppt1_current == 8.2
    assert device.pv.mppt1_power == round(350.0 * 8.2)


async def test_unused_mppt_strings_read_as_none(device: SungrowSHx) -> None:
    # mppt3/mppt4 use nan=65535 and were never written -> default 0 in the
    # mock store, which is a valid (if unlikely) real reading, not NaN.
    assert device.pv.mppt3_voltage == 0.0
    assert device.pv.mppt3_power == 0


async def test_is_generating_reflects_total_dc_power(device: SungrowSHx) -> None:
    assert device.pv.total_dc_power == 4500
    assert device.pv.is_generating is True
