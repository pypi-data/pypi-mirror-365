import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openmarkets.tools.analyst_data import (
    get_analyst_price_targets,
    get_recommendations,
    register_analyst_data_tools,
)


@pytest.fixture
def mock_ticker():
    """Fixture to mock the yfinance.Ticker object."""
    mock = MagicMock()
    # Mock the 'info' attribute to be a dictionary
    mock.info = {}
    return mock


@pytest.mark.asyncio
async def test_get_recommendations_success(mock_ticker):
    """Test get_recommendations with valid data."""
    data = {"Firm": ["A", "B"], "To Grade": ["Buy", "Hold"]}
    df = pd.DataFrame(data)
    mock_ticker.recommendations = df
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_recommendations("AAPL")
        assert json.loads(result) == json.loads(df.to_json(date_format="iso"))


@pytest.mark.asyncio
async def test_get_recommendations_no_data(mock_ticker):
    """Test get_recommendations with no data available."""
    mock_ticker.recommendations = None
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_recommendations("AAPL")
        assert json.loads(result) == {"error": "No recommendations available"}


@pytest.mark.asyncio
async def test_get_analyst_price_targets_success(mock_ticker):
    """Test get_analyst_price_targets with valid data."""
    info_data = {
        "targetHighPrice": 200,
        "targetLowPrice": 100,
        "targetMeanPrice": 150,
        "targetMedianPrice": 140,
        "recommendationMean": 2.0,
        "recommendationKey": "buy",
        "numberOfAnalystOpinions": 10,
    }
    mock_ticker.info = info_data
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_analyst_price_targets("AAPL")
        assert json.loads(result) == info_data


def test_register_analyst_data_tools():
    """Test register_analyst_data_tools."""
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()  # Simplified mock setup

    register_analyst_data_tools(mock_mcp)

    # Assert that mcp.tool() was called for each async public function
    expected_calls = [
        get_recommendations,
        get_analyst_price_targets,
    ]

    # Check that the `tool` method was called with the expected functions
    # This part of the test needs to be adjusted based on how you can inspect calls to the mock_mcp.tool()
    # For example, if it stores the decorated functions or if you can check call_args_list

    # Get the functions that were actually registered
    # print(f"call_args_list: {mock_mcp.tool.call_args_list}") # Incorrect call_args_list
    # print(f"call_args_list: {mock_mcp.tool.return_value.call_args_list}") # Correct call_args_list
    registered_funcs = [call_args[0][0] for call_args in mock_mcp.tool.return_value.call_args_list]

    assert len(registered_funcs) == len(expected_calls)
    for func in expected_calls:
        assert func in registered_funcs
