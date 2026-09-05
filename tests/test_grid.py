"""Grid import/export power split."""

from __future__ import annotations

from sungrow_modbus import SungrowSHx


async def test_negative_export_power_means_importing(device: SungrowSHx) -> None:
    assert device.grid.export_power_raw == -300
    assert device.grid.is_importing is True
    assert device.grid.is_exporting is False
    assert device.grid.import_power == 300
    assert device.grid.export_power == 0


async def test_frequency_is_scaled(device: SungrowSHx) -> None:
    assert device.grid.frequency == 50.01
