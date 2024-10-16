from typing import List
import pandas as pd
from datetime import datetime, timezone

@data_source
def filter_data(block_data_ouput: List, **kwargs):
    return [
        df.loc[
            df['timestamp']
            > datetime.now(
                timezone.utc
            )
        ]
        for df in block_data_ouput
    ]
