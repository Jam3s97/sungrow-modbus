"""A device/meter that doesn't answer every declared register block."""

from __future__ import annotations

import pytest
from modbus_connection import IllegalDataAddressError, ServerDeviceBusyError
from modbus_connection.mock import MockModbusUnit

from sungrow_modbus import SungrowSHx


async def test_unsupported_block_is_dropped_and_update_still_succeeds(
    loaded_unit: MockModbusUnit,
) -> None:
    loaded_unit.fail_read(5740, IllegalDataAddressError(), register_type="input")

    device = SungrowSHx(loaded_unit)
    await device.async_update()

    assert device.grid.meter_phase_a_voltage is None
    assert device.grid.meter_phase_b_voltage is None
    assert device.grid.meter_phase_c_voltage is None
    assert device.grid.meter_phase_a_current is None
    assert device.grid.meter_phase_b_current is None
    assert device.grid.meter_phase_c_current is None
    # Other fields on the same component, and other components, still read.
    assert device.grid.frequency == 50.01
    assert device.pv.mppt1_voltage == 350.0


async def test_dropped_block_is_not_read_again(loaded_unit: MockModbusUnit) -> None:
    loaded_unit.fail_read(5740, IllegalDataAddressError(), register_type="input")

    device = SungrowSHx(loaded_unit)
    await device.async_update()
    loaded_unit.fail_read(5740, None, register_type="input")
    loaded_unit.read_events.clear()

    await device.async_update()

    assert not any(5740 <= event.address <= 5745 for event in loaded_unit.read_events)


async def test_transient_error_is_not_treated_as_unsupported(
    loaded_unit: MockModbusUnit,
) -> None:
    loaded_unit.fail_read(5740, ServerDeviceBusyError(), register_type="input")

    device = SungrowSHx(loaded_unit)
    with pytest.raises(ServerDeviceBusyError):
        await device.async_update()
