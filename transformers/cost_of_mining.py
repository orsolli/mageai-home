if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from datetime import timezone, datetime
import pandas as pd


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

    #hash_per_sec = 54000 #1800
    #watt_per_hour = 280 #40
    def kwh_per_Mhash(hash_per_sec, watt_per_hour):
        Mhash_per_hour = hash_per_sec*3600/1000000
        kwh = watt_per_hour / 1000
        return kwh / Mhash_per_hour

    def add_vector(hash_per_sec, watt_per_hour):
        eur_cent_per_Mwh = data['price_cent']
        eur_per_kwh = eur_cent_per_Mwh / 100000
        _kwh_per_Mhash = kwh_per_Mhash(hash_per_sec, watt_per_hour)
        _wh_per_Mhash = _kwh_per_Mhash * 1000
        eur_per_Mhash = eur_per_kwh * _kwh_per_Mhash
        xmr_per_Mhash = 0.00673252/3600
        eur_per_xmr = eur_per_Mhash / xmr_per_Mhash
        data['EUR/XMR'] = eur_per_xmr.round()

    add_vector(kwargs['hashrate'], kwargs['effect'])
    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'