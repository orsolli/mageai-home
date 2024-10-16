from mage_ai.io.file import FileIO
from pandas import DataFrame

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_file(df: DataFrame, **kwargs) -> None:
    """
    Docs: https://docs.mage.ai/design/data-loading#fileio
    """

    df['month'] = df['timestamp'].dt.tz_convert('Europe/Oslo').dt.to_period('M')

    for date, group in df.groupby('month'):
        filepath = f'energy-price-NO2-{date.year}-{date.month:0d}.csv'
        FileIO().export(
            group,
            filepath,
            columns=['timestamp', 'price_cent'],
            index=False,
        )
        print(filepath)