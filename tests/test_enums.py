"""Enum decoding, including undocumented codes."""

from __future__ import annotations

from sungrow_modbus import RunningStateCode, SungrowSHx


async def test_known_running_state_decodes(device: SungrowSHx) -> None:
    assert device.status.running_state is RunningStateCode.RUNNING


async def test_unknown_running_state_decodes_to_none(loaded_unit) -> None:
    loaded_unit.input[12999] = 0x1111 + 1  # not present in the sourced code table

    dev = SungrowSHx(loaded_unit)
    await dev.async_update()
    assert dev.status.running_state is None
    assert dev.status.is_running is None
