"""Device identity decoding."""

from __future__ import annotations

from sungrow_modbus import DeviceTypeCode, SungrowSHx


async def test_device_type_is_decoded(device: SungrowSHx) -> None:
    assert device.info.device_type_code_raw == 0x0E03
    assert device.info.device_type is DeviceTypeCode.SH10RT
    assert device.info.model == "SH10RT"


async def test_manufacturer_is_constant(device: SungrowSHx) -> None:
    assert device.info.manufacturer == "Sungrow"


async def test_unknown_device_type_falls_back_to_raw_code(
    loaded_unit, device_class=SungrowSHx
) -> None:
    loaded_unit.input[4999] = 0xFFFF  # not in DeviceTypeCode
    dev = device_class(loaded_unit)
    await dev.async_update()
    assert dev.info.device_type is None
    assert dev.info.model == "Sungrow SHx (type 0xFFFF)"
