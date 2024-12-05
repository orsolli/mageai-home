from mage_ai.io.file import FileIO
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
import pandas as pd
from zoneinfo import ZoneInfo
from pandas import merge_ordered
from datetime import datetime, timezone

def load_data_from_file(key, date):
    filepath = f'{key}-{date.year}-{date.month:02}Z.csv'
    df = FileIO().load(filepath, names=['timestamp', key]).astype({
        'timestamp': pd.DatetimeTZDtype(tz=ZoneInfo('UTC')),
    })
    return df.loc[df['timestamp'] > date - pd.Timedelta(6, 'h')]

@data_loader
def d(**kwargs):
    execution_date = pd.Timestamp(kwargs.get('execution_date', datetime.utcnow())).replace(tzinfo=timezone.utc)
    df = load_data_from_file('BAC/supply_air_temperature', execution_date)
    #df = merge_ordered(df, load_data_from_file('BAC/exhaust_air_temperature', execution_date), fill_method="ffill")
    df = merge_ordered(df, load_data_from_file('BAC/outside_air_temperature', execution_date), fill_method="ffill")
    df = merge_ordered(df, load_data_from_file('BAC/extract_air_temperature', execution_date), fill_method="ffill")
    df = merge_ordered(df, load_data_from_file('HAN/ACTIVE_POWER_PLUS', execution_date), fill_method="ffill")

    return df
