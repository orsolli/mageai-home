from mage_ai.streaming.sources.base_python import BasePythonSource
from typing import Callable

if 'streaming_source' not in globals():
    from mage_ai.data_preparation.decorators import streaming_source

import asyncio
from datetime import datetime

from threading import Thread

from flexit_bacnet import FlexitBACnet

async def get_flexit(device):

    await device.update()

    return {
        'device_name': device.device_name, # Device Name
        'serial_number': device.serial_number, # Serial Number
        'outside_air_temperature': device.outside_air_temperature, # Air Temperature Outside (°C)
        'extract_air_temperature': device.extract_air_temperature, # Air Temperature Extract (°C)
        'supply_air_temperature': device.supply_air_temperature, # Air Temperature Supply (°C)
        'exhaust_air_temperature': device.exhaust_air_temperature, # Air Temperature Exhaust (°C)
        'extract_air_humidity': device.extract_air_humidity, # Air Humidity Extract (%)
        'room_temperature': device.room_temperature, # Air Temperature Room (°C)
        'room_1_humidity': device.room_1_humidity, # Air Humidity Room (%)
        'room_2_humidity': device.room_2_humidity, # Air Humidity Room 2 (%)
        'room_3_humidity': device.room_3_humidity, # Air Humidity Room 3 (%)
        'comfort_button': device.comfort_button, # Comfort (Active)
        'operation_mode': device.operation_mode, # Operation (Mode)
        'ventilation_mode': device.ventilation_mode, # Ventilation (Mode)
        'air_temp_setpoint_away': device.air_temp_setpoint_away, # Air Temperature Setpoint Away (°C)
        'air_temp_setpoint_home': device.air_temp_setpoint_home, # Air Temperature Setpoint Home (°C)
        'fireplace_ventilation_remaining_duration': device.fireplace_ventilation_remaining_duration, # Fireplace Ventilation Remaining Duration (Minutes)
        'rapid_ventilation_remaining_duration': device.rapid_ventilation_remaining_duration, # Rapid Ventilation Remaining Duration (Minutes)

        'supply_air_fan_control_signal': device.supply_air_fan_control_signal, # Current supply air fan control signal (in %) (int)
        'supply_air_fan_rpm': device.supply_air_fan_rpm, # Current supply air fan RPM (int)
        'exhaust_air_fan_control_signal': device.exhaust_air_fan_control_signal, # Current exhaust air fan control signal (in %) (int)
        'exhaust_air_fan_rpm': device.exhaust_air_fan_rpm, # Current exhaust air fan RPM (int)
        'electric_heater': device.electric_heater, # True if electric heater is enabled (bool)
        'electric_heater_nominal_power': device.electric_heater_nominal_power, # Nominal heater power in kilowatts (float)
        'electric_heater_power': device.electric_heater_power, # Heater power consumption in kilowatts (float)
        'fan_setpoint_supply_air_home': device.fan_setpoint_supply_air_home, # Fan setpoint for supply air HOME in percent (int)
        'fan_setpoint_extract_air_home': device.fan_setpoint_extract_air_home, # Fan setpoint for extract air HOME in percent (int)
        'fan_setpoint_supply_air_high': device.fan_setpoint_supply_air_high, # Fan setpoint for supply air HIGH in percent (int)
        'fan_setpoint_extract_air_high': device.fan_setpoint_extract_air_high, # Fan setpoint for extract air HIGH in percent (int)
        'fan_setpoint_supply_air_away': device.fan_setpoint_supply_air_away, # Fan setpoint for supply air AWAY in percent (int)
        'fan_setpoint_extract_air_away': device.fan_setpoint_extract_air_away, # Fan setpoint for extract air AWAY in percent (int)
        'fan_setpoint_supply_air_cooker': device.fan_setpoint_supply_air_cooker, # Fan setpoint for supply air COOKER in percent (int)
        'fan_setpoint_extract_air_cooker': device.fan_setpoint_extract_air_cooker, # Fan setpoint for extract air COOKER in percent (int)
        'fan_setpoint_supply_air_fire': device.fan_setpoint_supply_air_fire, # Fan setpoint for supply air FIRE in percent (int)
        'fan_setpoint_extract_air_fire': device.fan_setpoint_extract_air_fire, # Fan setpoint for extract air FIRE in percent (int)
        'air_filter_operating_time': device.air_filter_operating_time, # Air filter operating time in hours (float)
        'air_filter_exchange_interval': device.air_filter_exchange_interval, # Air Filter Exchange Interval
        'heat_exchanger_efficiency': device.heat_exchanger_efficiency, # Heat exchanger efficiency in percent (int)
        'heat_exchanger_speed': device.heat_exchanger_speed, # Heat exchanger speed in percent (int)
        'air_filter_polluted': device.air_filter_polluted, # Polluted Filter (bool)
    }

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

def execute_async(coro) -> None:
    loop = asyncio.new_event_loop()
    t = Thread(target=start_background_loop, args=(loop,), daemon=True)
    t.start()

    task = asyncio.run_coroutine_threadsafe(coro, loop)
    res = task.result()

    loop.stop()
    return res



@streaming_source
class CustomSource(BasePythonSource):
    def init_client(self):
        """
        Implement the logic of initializing the client.
        """
        self.device = FlexitBACnet('10.0.0.2', 2)
        self.last_result = 0


    def batch_read(self, handler: Callable):
        """
        Batch read the messages from the source and use handler to process the messages.
        """
        res = execute_async(get_flexit(self.device))
        last_result = res
        if self.last_result != last_result:
            self.last_result = last_result
            res['timestamp'] = datetime.utcnow()
            handler([res])
        else:
            print(last_result)
