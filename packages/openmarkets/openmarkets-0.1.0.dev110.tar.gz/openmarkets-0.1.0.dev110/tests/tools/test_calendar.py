import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openmarkets.tools.calendar import (
    get_earnings_calendar,
    get_earnings_dates,
    get_market_calendar_info,
    register_calendar_tools,
)


@pytest.fixture
def mock_ticker():
    """Fixture to mock the yfinance.Ticker object."""
    mock = MagicMock()
    # Mock the 'info' attribute to be a dictionary
    mock.info = {}
    # Mock the 'calendar' attribute
    mock.calendar = None
    return mock


@pytest.mark.xfail
async def test_get_earnings_calendar_success(mock_ticker):
    """Test get_earnings_calendar with valid data."""
    data = {"Earnings Date": ["2024-08-15"], "EPS Estimate": [1.50]}
    df = pd.DataFrame(data)
    mock_ticker.calendar = df
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_earnings_calendar("AAPL")
        assert json.loads(result) == json.loads(df.to_json(date_format="iso"))


@pytest.mark.asyncio
async def test_get_earnings_calendar_no_data(mock_ticker):
    """Test get_earnings_calendar with no data available."""
    mock_ticker.calendar = None
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_earnings_calendar("AAPL")
        assert json.loads(result) == {"error": "No earnings calendar data available"}


@pytest.mark.asyncio
async def test_get_earnings_dates_success(mock_ticker):
    """Test get_earnings_dates with valid data."""
    earnings_data = {
        "earningsTimestamp": "2024-08-15T10:00:00Z",
        "exDividendDate": "2024-07-20T10:00:00Z",
        "dividendDate": "2024-08-01T10:00:00Z",
    }
    mock_ticker.info = earnings_data
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_earnings_dates("AAPL")
        # Manually convert to JSON string with default=str for datetime like objects
        expected_json = json.dumps(earnings_data, indent=2, default=str)
        assert json.loads(result) == json.loads(expected_json)


@pytest.mark.asyncio
async def test_get_market_calendar_info_success(mock_ticker):
    """Test get_market_calendar_info with valid data."""
    market_data = {
        "exchange": "NASDAQ",
        "exchangeTimezoneName": "America/New_York",
        "exchangeTimezoneShortName": "EDT",
        "gmtOffSetMilliseconds": -14400000,
        "market": "us_market",
        "marketState": "REGULAR",
        "regularMarketTime": "2024-07-30T16:00:00Z",
        "regularMarketPreviousClose": 150.0,
        "preMarketPrice": 151.0,
        "preMarketTime": "2024-07-30T08:00:00Z",
        "postMarketPrice": 149.0,
        "postMarketTime": "2024-07-30T20:00:00Z",
    }
    mock_ticker.info = market_data
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_market_calendar_info("AAPL")
        expected_json = json.dumps(market_data, indent=2, default=str)
        assert json.loads(result) == json.loads(expected_json)


def test_register_calendar_tools():
    """Test register_calendar_tools."""
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()  # Simplified mock setup, as figured out previously

    register_calendar_tools(mock_mcp)

    expected_calls = [
        get_earnings_calendar,
        get_earnings_dates,
        get_market_calendar_info,
    ]

    # As established in the previous subtask, the actual calls are on return_value
    registered_funcs = [call_args[0][0] for call_args in mock_mcp.tool.return_value.call_args_list]

    assert len(registered_funcs) == len(expected_calls)
    for func in expected_calls:
        assert func in registered_funcs
