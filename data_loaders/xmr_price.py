import io
import pandas as pd
import requests
from pandas import json_normalize
import json
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from mage_ai.data_preparation.shared.secrets import get_secret_value



@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    api_key = get_secret_value('cmc_api_key')
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    response = requests.get(url + '?symbol=XMR&convert=EUR', headers={"X-CMC_PRO_API_KEY":api_key})

    content = response.content
    return json_normalize(json.loads(content))


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert len(output['data.XMR']), 'The output is empty'