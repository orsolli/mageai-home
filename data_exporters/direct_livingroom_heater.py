if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

from mage_ai.data_preparation.shared.secrets import get_secret_value
from plugp100.common.credentials import AuthCredential
from plugp100.new.device_factory import connect, DeviceConnectConfiguration
from plugp100.new.components.on_off_component import OnOffComponent
import pandas as pd
from pandas import json_normalize
from datetime import timezone, datetime
import aiohttp

import asyncio

from threading import Thread


async def toggle(host: str, on: bool):
    device_configuration = DeviceConnectConfiguration(
        host=host,
        credentials=AuthCredential(get_secret_value("tapo_username"), get_secret_value('tapo_password')),
        device_type='SMART.TAPOPLUG'
    )
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True, quote_cookie=False)) as session:
        device = await connect(device_configuration, session)
        await device.update()
        component = device.get_component(OnOffComponent)
        if on:
            result = await component.turn_on()
        elif on == False:
            result = await component.turn_off()
        return str(result)


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


@data_exporter
def export_data(df, *args, **kwargs):
    on = None
    extract_temperature = df['BAC/extract_air_temperature'].iloc[-1]
    supply_temperature = df['BAC/supply_air_temperature'].iloc[-1]
    power = df['Wh'].sum()
    power_limit = kwargs.get('power_limit', 1800)

    if extract_temperature < 22.4 and power < power_limit:
        on = True
    elif extract_temperature > 22.5 or power > power_limit:
        on = False

    base = {
        'power': power,
        'on': on,
        'extract_temperature': extract_temperature,
        'supply_temperature': supply_temperature,
        'power_limit': power_limit,
        'exe_result': None,
        'timestamp': df['timestamp'].iloc[-1],
    }
    if on is not None:
        base['exe_result'] = execute_async(toggle(kwargs['plug'], on))
    print(base)
    return json_normalize(base)
