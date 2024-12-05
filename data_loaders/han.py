from mage_ai.streaming.sources.base_python import BasePythonSource
from typing import Callable
import serial
from datetime import datetime

if 'streaming_source' not in globals():
    from mage_ai.data_preparation.decorators import streaming_source


@streaming_source
class CustomSource(BasePythonSource):
    def init_client(self):
        """
        Implement the logic of initializing the client.
        """
        self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=2400, timeout=10, parity='N')

    def batch_read(self, handler: Callable):
        """
        Batch read the messages from the source and use handler to process the messages.
        """
        data = parse_stream(self.ser.read(512))
        if data:
            handler([data])
        self.ser.close()

def parse_stream(stream):
    data = dict()
    for part in stream.split(b'\x09\x06'):
        match list(part):
            case [1, 1, 0, 2, 129, 255, *rest]:
                data['OBIS List version'] = bytes(rest)
            case [1, 1, 0, 0, 5, 255, *rest]:
                data['METER_ID'] = bytes(rest)
            case [1, 1, 96, 1, 1, 255, *rest]:
                data['METER_TYPE'] = bytes(rest)
            case [1, 1, 1, 7, 0, 255, *rest]:
                data['ACTIVE_POWER_PLUS'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 2, 7, 0, 255, *rest]:
                data['ACTIVE_POWER_MINUS'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 3, 7, 0, 255, *rest]:
                data['REACTIVE_POWER_PLUS'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 4, 7, 0, 255, *rest]:
                data['REACTIVE_POWER_MINUS'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 31, 7, 0, 255, *rest]:
                data['CURRENT_PHASE_L1'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 51, 7, 0, 255, *rest]:
                data['CURRENT_PHASE_L2'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 71, 7, 0, 255, *rest]:
                data['CURRENT_PHASE_L3'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 32, 7, 0, 255, *rest]:
                data['VOLTAGE_PHASE_L1'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 52, 7, 0, 255, *rest]:
                data['VOLTAGE_PHASE_L2'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [1, 1, 72, 7, 0, 255, *rest]:
                data['VOLTAGE_PHASE_L3'] = int.from_bytes(bytes(rest[-2:]), 'big')
            case [0, 1, 1, 0, 0, 255, *rest]:
                data['Clock_and_date'] = bytes(rest)
            case [1, 1, 1, 8, 0, 255, *rest]:
                data['Cumulative_hourly_active_import_kWh'] = bytes(rest)
            case [1, 1, 2, 8, 0, 255, *rest]:
                data['Cumulative_hourly_active_export_kWh'] = bytes(rest)
            case [1, 1, 3, 8, 0, 255, *rest]:
                data['Cumulative_hourly_reactive_import_kVArh'] = bytes(rest)
            case [1, 1, 4, 8, 0, 255, *rest]:
                data['Cumulative_hourly_active_export_kVArh'] = bytes(rest)
    if len(data):
        data['timestamp'] = datetime.utcnow()
        return data