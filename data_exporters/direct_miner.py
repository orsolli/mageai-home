import json
import requests
import pandas as pd
from pandas import json_normalize
from mage_ai.orchestration.triggers.api import trigger_pipeline
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
from mage_ai.data_preparation.shared.secrets import get_secret_value
from datetime import timezone, datetime


@data_exporter
def export_data(energy_prices, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    execution_date = kwargs.get('execution_date', datetime.utcnow())
    from_time = pd.Timestamp(execution_date).replace(tzinfo=timezone.utc)
    future = energy_prices['timestamp'] > from_time - pd.Timedelta(hours=1)

    compare_time_window = from_time - pd.Timedelta(days=1)
    threshold = energy_prices['EUR/XMR'].loc[energy_prices['timestamp'] > compare_time_window].median() * 1.5
    energy_prices['cheap'] = energy_prices['EUR/XMR'] < threshold
    is_profitable = energy_prices['profitable'].loc[future].iloc[0]
    is_cheap = energy_prices['cheap'].loc[future].iloc[0]
    is_cold = False
    on = is_profitable or is_cold and is_cheap

    next_change = energy_prices.loc[future & (energy_prices['profitable'] ^ on)]
    next_change_time = from_time.ceil('24h')
    if next_change.size:
        next_change_time = next_change['timestamp'].loc[future].iloc[0]

    api_key = get_secret_value('xmrig_api_key')
    host = kwargs.get('xmrig_api', 'http://localhost')

    body = {"method":"resume" if on else "pause"}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    response = requests.post(f"{host}/json_rpc", data=json.dumps(body), headers=headers)
    content = response.content

    return json_normalize({"next_change": next_change_time, "is_on": on})
