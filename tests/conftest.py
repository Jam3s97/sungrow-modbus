"""Fixtures: a SungrowSHx over modbus-connection's in-memory mock backend.

The mock backend and its fixtures ship with ``modbus-connection``. They are
imported explicitly below so the test suite does not depend on pytest
entry-point autoloading. There is no real server, socket, or backend here --
just an address-keyed store loaded with Sungrow-shaped register values.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.pytest_plugin import (
    mock_modbus_connection as mock_modbus_connection,
    mock_modbus_unit as mock_modbus_unit,
)

from sungrow_modbus import SungrowSHx


def _split_word_swapped(value: int) -> tuple[int, int]:
    """Split a signed/unsigned 32-bit value into (low_word, high_word)."""
    raw = value & 0xFFFFFFFF
    return raw & 0xFFFF, (raw >> 16) & 0xFFFF


# Raw register words keyed by their (protocol) address; decoded view inline.
INPUT: dict[int, int] = {
    # --- identity ---
    4999: 0x0E03,  # device_type_code_raw -> SH10RT
    5000: 100,  # rated_output_power -> 10000 W (scale 100)
    # --- PV strings ---
    5010: 3500,  # mppt1_voltage -> 350.0 V
    5011: 82,  # mppt1_current -> 8.2 A
    5012: 3400,  # mppt2_voltage -> 340.0 V
    5013: 61,  # mppt2_current -> 6.1 A
    # 5016/5017: total_dc_power (uint32, word-swapped) -> 4500 W
    5016: _split_word_swapped(4500)[0],
    5017: _split_word_swapped(4500)[1],
    # --- inverter status ---
    5007: 385,  # temperature -> 38.5 degC
    5018: 2300,  # phase_a_voltage -> 230.0 V
    5019: 2310,  # phase_b_voltage -> 231.0 V
    5020: 2290,  # phase_c_voltage -> 229.0 V
    5034: 985,  # power_factor -> 0.985
    12999: 0x0000,  # running_state -> RUNNING
    13000: 0,  # power_flow_status_raw
    13030: 65,  # phase_a_current -> 6.5 A
    13031: 65,  # phase_b_current -> 6.5 A
    13032: 65,  # phase_c_current -> 6.5 A
    # 13033/13034: total_active_power (int32, word-swapped) -> 4400 W
    13033: _split_word_swapped(4400)[0],
    13034: _split_word_swapped(4400)[1],
    # --- battery telemetry ---
    # 5213/5214: power (int32, word-swapped) -> -1500 W (charging)
    5213: _split_word_swapped(-1500)[0],
    5214: _split_word_swapped(-1500)[1],
    5638: 1280,  # capacity_high_precision -> 12.80 kWh
    13019: 4850,  # voltage -> 485.0 V
    13022: 550,  # level -> 55.0 %
    13023: 993,  # state_of_health -> 99.3 %
    13024: 280,  # temperature -> 28.0 degC
    # --- grid meter ---
    5241: 5001,  # frequency -> 50.01 Hz
    # 13007/13008: load_power (int32, word-swapped) -> 900 W
    13007: _split_word_swapped(900)[0],
    13008: _split_word_swapped(900)[1],
    # 13009/13010: export_power_raw (int32, word-swapped) -> -300 W (importing)
    13009: _split_word_swapped(-300)[0],
    13010: _split_word_swapped(-300)[1],
    # --- backup ---
    5725: _split_word_swapped(0)[0],
    5726: _split_word_swapped(0)[1],
    # --- energy totals ---
    13001: 125,  # daily_pv_generation -> 12.5 kWh
    13004: 40,  # daily_exported_energy_from_pv -> 4.0 kWh
    13011: 30,  # daily_battery_charge_from_pv -> 3.0 kWh
    13016: 55,  # daily_direct_energy_consumption -> 5.5 kWh
    13025: 20,  # daily_battery_discharge -> 2.0 kWh
    13035: 10,  # daily_imported_energy -> 1.0 kWh
    13039: 35,  # daily_battery_charge -> 3.5 kWh
    13044: 45,  # daily_exported_energy -> 4.5 kWh
}

HOLDING: dict[int, int] = {
    13001: 3,  # load_adjustment_mode -> DISABLED
    13010: 0x55,  # load_adjustment_mode_enabled -> OFF
    13049: 0,  # ems_mode -> SELF_CONSUMPTION
    13050: 0xCC,  # forced_charge_discharge_command -> STOP
    13051: 0,  # forced_charge_discharge_power
    13057: 900,  # battery max_soc -> 90.0 %
    13058: 100,  # battery min_soc -> 10.0 %
    13073: 5000,  # export_power_limit -> 5000 W
    13074: 0x55,  # backup_mode_enabled -> OFF
    13086: 0x55,  # export_power_limit_enabled -> OFF
    13099: 10,  # reserved_soc_for_backup -> 10 %
    33046: 800,  # max_charge_power -> 8000 W (scale 10)
    33047: 800,  # max_discharge_power -> 8000 W (scale 10)
}


@pytest.fixture
def loaded_unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """A mock unit pre-loaded with a realistic Sungrow SHx register snapshot."""
    mock_modbus_unit.input.update(INPUT)
    mock_modbus_unit.holding.update(HOLDING)
    return mock_modbus_unit


@pytest.fixture
async def device(loaded_unit: MockModbusUnit) -> SungrowSHx:
    """A ``SungrowSHx`` that has already performed one ``async_update``."""
    dev = SungrowSHx(loaded_unit)
    await dev.async_update()
    return dev
