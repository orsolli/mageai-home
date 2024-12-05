if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import pandas as pd
from datetime import timezone, datetime

@transformer
def transform(data, *args, **kwargs):
    execution_date = kwargs.get('execution_date', datetime.utcnow())
    from_time = pd.Timestamp(execution_date).replace(tzinfo=timezone.utc)

    df = data.loc[data['timestamp'] > (from_time - pd.Timedelta(60, 'min'))]
    df['seconds'] = df['timestamp'].diff().dt.total_seconds().fillna(10)
    df['Wh'] = df['seconds'] * df['HAN/ACTIVE_POWER_PLUS'] / df['seconds'].sum()
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert output['BAC/extract_air_temperature'].iloc[-1] is not None, 'Missing temperatures'
    assert output['BAC/supply_air_temperature'].iloc[-1] is not None, 'Missing temperatures'