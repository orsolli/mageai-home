import pandas as pd
import math

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@transformer
def transform_df(tomorrow_df: pd.DataFrame, today_df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
        Concatenates todays prices with tomorrows filled prices to fill tomorrows prices
    """
    data = pd\
        .concat([today_df, tomorrow_df])\
        .drop_duplicates(subset='timestamp', keep='last')

    # Set the 'timestamp' column as the index
    df = data.set_index('timestamp')

    # Resample the DataFrame to hourly frequency, filling missing hours
    df = df.resample('H').ffill()

    return df.reset_index()


@test
def test_output(df) -> None:
    """
    Template code for testing the output of the block.
    """
    assert df is not None, 'The output is undefined'
