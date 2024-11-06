if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import pandas as pd
from datetime import timezone, datetime


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
    execution_date = kwargs.get('execution_date', datetime.utcnow())
    from_time = pd.Timestamp(execution_date).replace(tzinfo=timezone.utc)
    threshold = data['price_cent'].median() * 2
    data = data.loc[data['timestamp'] > from_time]
    data['high_price'] = data['price_cent'] > threshold
    if data['high_price'].any():
        return f"""
            Energy price will be high at this time:
            {data.loc[data['high_price']]['timestamp'].iloc[0]}
        """