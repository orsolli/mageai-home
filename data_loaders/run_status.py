from mage_ai.orchestration.run_status_checker import check_status
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import pandas as pd

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    try:
        check_status(
            'entso_e',
            kwargs['execution_date'],
            block_uuid='store_energy_price_file',
            hours=24,
        )
    except:
        return 'Failed to run Entso-E pipeline'

    try:
        check_status(
            'alert_energy_price',
            kwargs['execution_date'],
            block_uuid='email_sender',
            hours=24,
        )
    except:
        return 'Failed to run Alert Energy Price pipeline'
