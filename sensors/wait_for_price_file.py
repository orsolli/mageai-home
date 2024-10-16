from mage_ai.orchestration.run_status_checker import check_status

if 'sensor' not in globals():
    from mage_ai.data_preparation.decorators import sensor


@sensor
def check_condition(*args, **kwargs) -> bool:
    """
    Wait for block to run complete.
    """

    return check_status(
        'entso_e',
        kwargs['execution_date'],
        block_uuid='store_energy_price_file',
        hours=11,
    )