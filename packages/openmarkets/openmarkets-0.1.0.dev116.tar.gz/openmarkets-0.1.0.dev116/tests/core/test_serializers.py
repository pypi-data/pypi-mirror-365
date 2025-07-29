# --- Tests for JSONSerializer and safe_json_dumps ---
import json
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.serializers import safe_json_dumps


class TestSafeJsonDumps:
    def test_safe_json_dumps_standard_types(self):
        data = {
            "string": "hello",
            "integer": 123,
            "float": 45.67,
            "boolean": True,
            "none": None,
            "list": [1, "two", 3.0],
            "dict": {"a": 1, "b": "bee"},
        }
        expected_json = '{"string": "hello", "integer": 123, "float": 45.67, "boolean": true, "none": null, "list": [1, "two", 3.0], "dict": {"a": 1, "b": "bee"}}'
        assert json.loads(safe_json_dumps(data)) == json.loads(expected_json)

    def test_safe_json_dumps_with_indent(self):
        data = {"a": 1, "b": 2}
        # Exact string with indent can be brittle, so check if it's valid JSON and loads back
        # Also check if newline and indent spaces are present
        dumped_str = safe_json_dumps(data, indent=2)
        assert json.loads(dumped_str) == data
        assert '\n  "' in dumped_str  # Check for newline and indent

    def test_pandas_timestamp(self):
        now = datetime.now()
        ts = pd.Timestamp(now)
        data = {"time": ts}
        # pd.Timestamp.isoformat() might have more precision than datetime.isoformat()
        # We need to match what JSONSerializer produces
        expected_json = f'{{"time": "{ts.isoformat()}"}}'
        assert safe_json_dumps(data) == expected_json

    def test_numpy_integer(self):
        data = {"np_int": np.int64(12345)}
        expected_json = '{"np_int": 12345}'
        assert safe_json_dumps(data) == expected_json

    def test_numpy_floating(self):
        data = {"np_float": np.float64(12.345)}
        expected_json = '{"np_float": 12.345}'
        assert safe_json_dumps(data) == expected_json

    def test_numpy_array(self):
        data = {"np_array": np.array([1, 2, 3])}
        expected_json = '{"np_array": [1, 2, 3]}'
        assert safe_json_dumps(data) == expected_json

    def test_pandas_series(self):
        data = {"pd_series": pd.Series([10.1, 20.2, 30.3])}
        expected_json = '{"pd_series": [10.1, 20.2, 30.3]}'
        assert safe_json_dumps(data) == expected_json

    def test_mixed_numpy_pandas_and_standard(self):
        data = {
            "np_array": np.array([1, 2]),
            "pd_series": pd.Series([1.1, 2.2]),
            "timestamp": pd.Timestamp("2023-01-01T12:00:00"),
            "np_int": np.int32(100),
            "np_float": np.float32(99.9),
            "regular_int": 50,
            "regular_list": ["a", "b"],
        }
        # Load and compare for complex dicts to avoid issues with key order or float precision strings
        result_json = safe_json_dumps(data)
        loaded_result = json.loads(result_json)

        expected_data = {
            "np_array": [1, 2],
            "pd_series": [1.1, 2.2],
            "timestamp": "2023-01-01T12:00:00",
            "np_int": 100,
            "np_float": pytest.approx(99.9, abs=1e-5),  # Handle potential float precision
            "regular_int": 50,
            "regular_list": ["a", "b"],
        }
        assert loaded_result == expected_data

    def test_unserializable_object_raises_typeerror(self):
        class Unserializable:
            pass

        data = {"custom_obj": Unserializable()}
        # This error is raised by the original json.JSONEncoder.default method
        with pytest.raises(TypeError, match="Object of type Unserializable is not JSON serializable"):
            safe_json_dumps(data)


if __name__ == "__main__":
    pytest.main()
