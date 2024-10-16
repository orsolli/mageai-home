import io
import pandas as pd
import requests
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo


@transformer
def transform(data, *args, **kwargs):
    """
    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    root = ET.fromstring(data['response_text'].iloc[0])
    result = []
    periods = root.findall('{*}TimeSeries/{*}Period')
    for period in periods:
        period_start = period.find('{*}timeInterval/{*}start').text
        period_start = datetime.fromisoformat(period_start.replace('Z', '')) - timedelta(hours=1)
        for point in period.findall('{*}Point'):
            position = point.find('{*}position').text
            price_amount = point.find('{*}price.amount').text
            # TODO: Figure out what happens on daylight savings switch
            timestamp = period_start + timedelta(hours=int(position))
            result.append({
                'timestamp': pd.Timestamp(timestamp),
                'price_cent': int(float(price_amount)*100)
            })

    return pd.DataFrame(result).astype({
      'timestamp': pd.DatetimeTZDtype(tz=ZoneInfo('UTC')),
      'price_cent': 'int'
    })


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert len(output) <= 25, 'The output is more than 25 hours'
    assert output['timestamp'].min() + timedelta(hours=25) >= output['timestamp'].max(), 'Time contains outliers'
    assert output['timestamp'].min().hour in [22, 23], 'First position does not start at Norwegian midnight'

