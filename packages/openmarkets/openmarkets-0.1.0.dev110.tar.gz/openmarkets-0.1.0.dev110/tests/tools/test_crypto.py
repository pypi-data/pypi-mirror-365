import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import yfinance as yf  # To help with yfinance.Ticker typing if needed

from openmarkets.tools.crypto import (
    get_crypto_fear_greed_proxy,
    get_crypto_historical_data,
    get_crypto_info,
    get_top_cryptocurrencies,
    register_crypto_tools,
)

# Common mock data
mock_btc_info_data = {
    "symbol": "BTC-USD",
    "shortName": "Bitcoin USD",
    "currentPrice": 40000.0,
    "marketCap": 800000000000,
    "volume24Hr": 50000000000,
    "circulatingSupply": 19000000,
    "maxSupply": 21000000,
    "previousClose": 39000.0,
    "dayLow": 38500.0,
    "dayHigh": 40500.0,
    "fiftyTwoWeekLow": 20000.0,
    "fiftyTwoWeekHigh": 70000.0,
    "currency": "USD",
}

mock_eth_info_data = {
    "symbol": "ETH-USD",
    "shortName": "Ethereum USD",
    "currentPrice": 3000.0,
    "marketCap": 360000000000,
    "volume24Hr": 20000000000,
    "circulatingSupply": 120000000,
    "maxSupply": None,  # Example
    "previousClose": 2900.0,
    # ... (other fields can be added if needed by tests)
}


def create_mock_history_df(dates, close_prices, other_cols=None):
    if other_cols is None:
        other_cols = {}
    data = {"Close": close_prices, **other_cols}
    return pd.DataFrame(data, index=pd.to_datetime(dates))


@pytest.fixture
def mock_yfinance_ticker():
    """Fixture to mock yfinance.Ticker."""
    mock_ticker_instance = MagicMock(spec=yf.Ticker)  # Use spec for stricter mocking
    mock_ticker_instance.info = {}
    mock_ticker_instance.history = MagicMock(return_value=pd.DataFrame())  # Default empty history
    return mock_ticker_instance


# Tests for get_crypto_info
@pytest.mark.asyncio
async def test_get_crypto_info_success(mock_yfinance_ticker):
    mock_yfinance_ticker.info = mock_btc_info_data
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker) as mock_ticker_constructor:
        result_str = await get_crypto_info("BTC")  # Test without -USD
        result = json.loads(result_str)
        mock_ticker_constructor.assert_called_once_with("BTC-USD")
        assert result["symbol"] == "BTC-USD"
        assert result["name"] == "Bitcoin USD"
        assert result["currentPrice"] == 40000.0


@pytest.mark.asyncio
async def test_get_crypto_info_with_suffix_success(mock_yfinance_ticker):
    mock_yfinance_ticker.info = mock_eth_info_data
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker) as mock_ticker_constructor:
        result_str = await get_crypto_info("ETH-USD")  # Test with -USD
        result = json.loads(result_str)
        mock_ticker_constructor.assert_called_once_with("ETH-USD")
        assert result["symbol"] == "ETH-USD"
        assert result["name"] == "Ethereum USD"


@pytest.mark.asyncio
async def test_get_crypto_info_error(mock_yfinance_ticker):
    mock_yfinance_ticker.info = {}  # Simulate no data or error
    # Or mock_yfinance_ticker.info.get.side_effect = some_exception if needed
    # For now, empty info will result in many None values
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_crypto_info("UNKNOWN")
        result = json.loads(result_str)
        # Expecting None for most fields if info is empty
        assert result["symbol"] is None
        assert result["name"] is None


# Tests for get_crypto_historical_data
@pytest.mark.asyncio
async def test_get_crypto_historical_data_success(mock_yfinance_ticker):
    dates = pd.date_range(start="2023-01-01", periods=5, freq="D")
    prices = [100, 101, 102, 103, 104]
    mock_df = create_mock_history_df(dates, prices)
    mock_yfinance_ticker.history.return_value = mock_df

    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker) as mock_ticker_constructor:
        result_str = await get_crypto_historical_data("BTC", period="5d", interval="1d")
        result = json.loads(result_str)
        # print(f"DEBUG: result[Close].keys() = {list(result['Close'].keys())}") # Print actual keys
        actual_keys = list(result["Close"].keys())
        mock_ticker_constructor.assert_called_once_with("BTC-USD")
        mock_yfinance_ticker.history.assert_called_once_with(period="5d", interval="1d")
        assert len(result["Close"]) == 5
        assert result["Close"][actual_keys[0]] == prices[0]  # Use the actual first key


@pytest.mark.asyncio
async def test_get_crypto_historical_data_no_data(mock_yfinance_ticker):
    mock_yfinance_ticker.history.return_value = pd.DataFrame()  # Empty DataFrame
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_crypto_historical_data("NODATA")
        result = json.loads(result_str)
        assert "error" in result
        assert result["error"] == "No historical data available"


# Tests for get_top_cryptocurrencies
@pytest.mark.asyncio
@patch("yfinance.Ticker")  # Patch Ticker for all calls within this test
async def test_get_top_cryptocurrencies_default_count(mock_ticker_constructor):
    # import importlib, sys # For reload - Removed
    # import openmarkets.tools.crypto as crypto_module # For reload - Removed
    # try: # Ensure reload even if test fails early
    #     importlib.reload(crypto_module)
    # except Exception as e:
    #     print(f"DEBUG: Reload failed {e}")

    # Mock multiple Ticker instances and their data
    def mock_ticker_side_effect(symbol):
        instance = MagicMock()  # Removed spec=yf.Ticker
        instance.symbol = symbol  # yf.Ticker has this attribute
        if symbol == "BTC-USD":
            instance.info = mock_btc_info_data
            instance.history = MagicMock(
                return_value=create_mock_history_df(["2023-01-01", "2023-01-02"], [39000, 40000])
            )
        elif symbol == "ETH-USD":
            instance.info = mock_eth_info_data
            instance.history = MagicMock(
                return_value=create_mock_history_df(["2023-01-01", "2023-01-02"], [2900, 3000])
            )
        else:  # Default for other cryptos in the top list
            instance.info = {
                "shortName": symbol.replace("-USD", ""),
                "currentPrice": 100,
                "marketCap": 10000,
                "volume": 1000,
            }
            instance.history = MagicMock(return_value=create_mock_history_df(["2023-01-01", "2023-01-02"], [99, 100]))
        return instance

    mock_ticker_constructor.side_effect = mock_ticker_side_effect

    result_str = await get_top_cryptocurrencies()  # Default count = 10
    result = json.loads(result_str)

    assert result["count"] == 10
    assert len(result["cryptocurrencies"]) == 10
    assert result["cryptocurrencies"][0]["symbol"] == "BTC-USD"
    assert result["cryptocurrencies"][0]["currentPrice"] == 40000.0
    assert result["cryptocurrencies"][0]["dailyChangePercent"] == pytest.approx((40000 - 39000) / 39000 * 100)
    assert result["cryptocurrencies"][1]["symbol"] == "ETH-USD"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_top_cryptocurrencies_custom_count(mock_ticker_constructor):
    # import importlib, sys # Removed
    # import openmarkets.tools.crypto as crypto_module  # Removed
    # try:
    #     importlib.reload(crypto_module)
    # except Exception as e:
    #     print(f"DEBUG: Reload failed {e}")
    mock_ticker_constructor.side_effect = lambda symbol: MagicMock(
        info={"shortName": symbol.replace("-USD", ""), "currentPrice": 10, "marketCap": 100, "volume": 10},
        history=MagicMock(return_value=create_mock_history_df(["2023-01-01", "2023-01-02"], [9, 10])),
    )
    result_str = await get_top_cryptocurrencies(count=3)
    result = json.loads(result_str)
    assert result["count"] == 3
    assert len(result["cryptocurrencies"]) == 3


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_top_cryptocurrencies_max_count(mock_ticker_constructor):
    # import importlib, sys # Removed
    # import openmarkets.tools.crypto as crypto_module # Removed
    # try:
    #     importlib.reload(crypto_module)
    # except Exception as e:
    #     print(f"DEBUG: Reload failed {e}")
    mock_ticker_constructor.side_effect = lambda symbol: MagicMock(
        info={"shortName": symbol.replace("-USD", ""), "currentPrice": 10, "marketCap": 100, "volume": 10},
        history=MagicMock(return_value=create_mock_history_df(["2023-01-01", "2023-01-02"], [9, 10])),
    )
    result_str = await get_top_cryptocurrencies(count=25)  # Should cap at 20
    result = json.loads(result_str)
    assert result["count"] == 20
    assert len(result["cryptocurrencies"]) == 20


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_top_cryptocurrencies_api_error(mock_ticker_constructor):
    mock_ticker_constructor.side_effect = Exception("API limit hit")
    result_str = await get_top_cryptocurrencies(count=2)
    result = json.loads(result_str)
    assert "error" in result
    assert "Failed to get crypto data: API limit hit" in result["error"]


# Tests for get_crypto_fear_greed_proxy
@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_crypto_fear_greed_proxy_extreme_greed(mock_ticker_constructor):
    # All cryptos up > 10% weekly
    mock_ticker_constructor.side_effect = lambda symbol: MagicMock(
        history=MagicMock(
            return_value=create_mock_history_df(
                pd.date_range(end=pd.Timestamp.now(), periods=7, freq="D"),
                [100, 102, 104, 106, 108, 110, 111],  # >10% increase (111 vs 100)
            )
        )
    )
    result_str = await get_crypto_fear_greed_proxy(["BTC-USD", "ETH-USD"])
    result = json.loads(result_str)
    assert result["sentiment_proxy"] == "Extreme Greed"
    assert result["average_weekly_change"] == pytest.approx(11.0)


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_crypto_fear_greed_proxy_extreme_fear(mock_ticker_constructor):
    # All cryptos down > 10% weekly
    mock_ticker_constructor.side_effect = lambda symbol: MagicMock(
        history=MagicMock(
            return_value=create_mock_history_df(
                pd.date_range(end=pd.Timestamp.now(), periods=7, freq="D"),
                [100, 98, 96, 94, 92, 90, 89],  # >10% decrease (89 vs 100)
            )
        )
    )
    result_str = await get_crypto_fear_greed_proxy(["BTC-USD"])
    result = json.loads(result_str)
    assert result["sentiment_proxy"] == "Extreme Fear"
    assert result["average_weekly_change"] == pytest.approx(-11.0)


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_crypto_fear_greed_proxy_mixed(mock_ticker_constructor):
    def side_effect(symbol):
        mock = MagicMock()
        if symbol == "BTC-USD":  # Up 5%
            mock.history.return_value = create_mock_history_df(
                pd.date_range(end=pd.Timestamp.now(), periods=7), [100, 101, 102, 103, 104, 105, 105]
            )
        elif symbol == "ETH-USD":  # Down 5%
            mock.history.return_value = create_mock_history_df(
                pd.date_range(end=pd.Timestamp.now(), periods=7), [100, 99, 98, 97, 96, 95, 95]
            )
        return mock

    mock_ticker_constructor.side_effect = side_effect

    result_str = await get_crypto_fear_greed_proxy(["BTC-USD", "ETH-USD"])
    result = json.loads(result_str)
    assert result["sentiment_proxy"] == "Neutral-Negative"  # Avg is 0, falls into > -5
    assert result["average_weekly_change"] == pytest.approx(0.0)


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_crypto_fear_greed_proxy_api_error(mock_ticker_constructor):
    mock_ticker_constructor.side_effect = Exception("API error")
    result_str = await get_crypto_fear_greed_proxy()
    result = json.loads(result_str)
    assert "error" in result
    assert "Failed to calculate sentiment proxy: API error" in result["error"]


# Test for register_crypto_tools
def test_register_crypto_tools():
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()

    # import importlib # Removed
    # import openmarkets.tools.crypto as crypto_module # Removed
    # importlib.reload(crypto_module) # Removed

    # Register using the direct import now that reload is not used session-wide from other tests
    register_crypto_tools(mock_mcp)

    registered_funcs = [call_arg[0][0] for call_arg in mock_mcp.tool.return_value.call_args_list]

    # Use direct imports for expected functions
    expected_public_async_funcs = [
        get_crypto_info,
        get_crypto_historical_data,
        get_top_cryptocurrencies,
        get_crypto_fear_greed_proxy,
    ]
    assert len(registered_funcs) == len(expected_public_async_funcs), (
        f"Expected {len(expected_public_async_funcs)} funcs, got {len(registered_funcs)}. Registered: {registered_funcs}"
    )
    for func in expected_public_async_funcs:
        assert func in registered_funcs, f"{func.__name__} not found in {registered_funcs}"
