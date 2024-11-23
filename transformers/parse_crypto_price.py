if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import json
from pandas import json_normalize


@transformer
def transform(data, *args, **kwargs):
    return json_normalize(data['data.XMR'][0])


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output['quote.EUR.price'] is not None, 'The output is undefined'