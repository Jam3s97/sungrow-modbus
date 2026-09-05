"""Battery telemetry, charge/discharge split and SoC-band computations."""

from __future__ import annotations

from sungrow_modbus import SungrowSHx


async def test_negative_power_means_charging(device: SungrowSHx) -> None:
    assert device.battery.power == -1500
    assert device.battery.is_charging is True
    assert device.battery.is_discharging is False
    assert device.battery.charging_power == 1500
    assert device.battery.discharging_power == 0


async def test_nominal_level_rescales_into_soc_band(device: SungrowSHx) -> None:
    # level=55%, band 10%..90% -> 10 + (90-10) * 0.55 = 54
    assert device.battery.level == 55.0
    assert device.battery_settings.min_soc == 10.0
    assert device.battery_settings.max_soc == 90.0
    assert device.battery_level_nominal == 54.0


async def test_usable_charge_scales_capacity_by_band_and_level(
    device: SungrowSHx,
) -> None:
    # 12.80 kWh * (90-10)/100 * 55/100 = 5.632 -> 5.63
    assert device.battery.capacity_high_precision == 12.8
    assert device.battery_usable_charge_kwh == 5.63


async def test_health_rated_charge_further_scales_by_state_of_health(
    device: SungrowSHx,
) -> None:
    # 5.63 kWh * 99.3% = 5.5906 -> 5.59
    assert device.battery.state_of_health == 99.3
    assert device.battery_health_rated_charge_kwh == 5.59


async def test_forced_charge_discharge_command_defaults_to_stop(
    device: SungrowSHx,
) -> None:
    from sungrow_modbus import ForcedChargeDischargeCommand

    assert (
        device.battery_settings.forced_charge_discharge_command
        is ForcedChargeDischargeCommand.STOP
    )
