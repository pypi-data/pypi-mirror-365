import json
from typing import Optional

import numpy as np
import pandas as pd


class JSONSerializer(json.JSONEncoder):
    """Custom JSON encoder for pandas and numpy objects."""

    def default(self, o):
        if isinstance(o, pd.Timestamp):
            return o.isoformat()
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, (np.ndarray, pd.Series)):
            return o.tolist()
        return super().default(o)


def safe_json_dumps(data, indent: Optional[int] = None) -> str:
    """Serialize data to a JSON string, converting pandas/numpy objects to JSON serializable types.

    Args:
        data: The data to serialize.
        indent: If not None, then JSON array elements and object members will be pretty-printed
                with that indent level.

    Returns:
        JSON string.
    """
    return json.dumps(data, cls=JSONSerializer, indent=indent)
