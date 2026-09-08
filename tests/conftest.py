"""Independent, deterministic register fixture; no real backend is required."""

import json
from pathlib import Path

import pytest
from modbus_connection.mock import MockModbusUnit


@pytest.fixture
def unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    data = json.loads((Path(__file__).parent / "fixtures" / "airpack4.json").read_text())
    mock_modbus_unit.load_raw(
        {space: {int(k): v for k, v in values.items()} for space, values in data.items()}
    )
    return mock_modbus_unit
