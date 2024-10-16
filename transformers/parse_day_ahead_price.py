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
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

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
            result.append({
                'time': pd.Timestamp(period_start + timedelta(hours=int(position))),
                'price_cent': int(float(price_amount)*100)
            })

    return pd.DataFrame(result).astype({
      'time': pd.DatetimeTZDtype(tz=ZoneInfo('UTC')),
      'price_cent': 'int'
    })



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert len(output) <= 24, 'The output is not 24 hours'
    assert output['time'].min() + timedelta(hours=24) >= output['time'].max(), 'Time contains outliers'

