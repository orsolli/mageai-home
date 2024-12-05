if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from datetime import timezone, datetime
import pandas as pd


@transformer
def transform(xmr_price, cost_of_mining, *args, **kwargs):
    xmr_price = xmr_price['quote.EUR.price'].iloc[-1]
    eur_per_xmr = cost_of_mining['EUR/XMR']

    cost_of_mining['profitable'] = eur_per_xmr < xmr_price

    return cost_of_mining


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'