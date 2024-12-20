from mage_ai.streaming.sinks.base_python import BasePythonSink
from typing import Callable, Dict, List
from mage_ai.io.file import FileIO
from pandas import json_normalize
import subprocess

if 'streaming_sink' not in globals():
    from mage_ai.data_preparation.decorators import streaming_sink


@streaming_sink
class CustomSink(BasePythonSink):
    def init_client(self):
        """
        Implement the logic of initializing the client.
        """

    def batch_write(self, messages: List[Dict]):
        """
        Batch write the messages to the sink.

        For each message, the message format could be one of the following ones:
        1. message is the whole data to be wirtten into the sink
        2. message contains the data and metadata with the foramt {"data": {...}, "metadata": {...}}
            The data value is the data to be written into the sink. The metadata is used to store
            extra information that can be used in the write method (e.g. timestamp, index, etc.).
        """
        for msg in messages:
            for key in msg:
                if key not in [
                    'timestamp',
                    'device_name',
                    'serial_number'
                ]:
                    date = msg['timestamp']
                    filepath = f'HAN/{key}-{date.year}-{date.month:02}Z.csv'
                    existing = subprocess.check_output(f"tail -1 {filepath} || echo -n ',N/A'", shell=True).decode("utf-8").strip() + ',N/A'
                    if str(existing.split(",")[1]) != str(msg[key]):
                        FileIO().export(
                            json_normalize(msg),
                            filepath,
                            columns=['timestamp', key],
                            index=False,
                            header=False,
                            mode='a'
                        )
                        print(filepath)
