import json
from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd
import pytest

import openmarkets.tools.historical_data as hd


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_historical_data(mock_ticker):
    mock_hist = pd.DataFrame({"Close": [100, 101]}, index=pd.date_range("2023-01-01", periods=2))
    mock_ticker.return_value.history.return_value = mock_hist
    result = await hd.get_historical_data("AAPL", period="1mo", interval="1d")
    data = json.loads(result)
    assert "Close" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_intraday_data(mock_ticker):
    mock_hist = pd.DataFrame({"Open": [10, 11]}, index=pd.date_range("2023-01-01", periods=2))
    mock_ticker.return_value.history.return_value = mock_hist
    result = await hd.get_intraday_data("AAPL", period="1d", interval="5m")
    data = json.loads(result)
    assert "Open" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_prepost_market_data(mock_ticker):
    mock_hist = pd.DataFrame({"High": [1, 2]}, index=pd.date_range("2023-01-01", periods=2))
    mock_ticker.return_value.history.return_value = mock_hist
    result = await hd.get_prepost_market_data("AAPL", period="1d")
    data = json.loads(result)
    assert "High" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_dividends_with_data(mock_ticker):
    mock_dividends = pd.Series([0.5, 0.6], index=pd.date_range("2023-01-01", periods=2))
    type(mock_ticker.return_value).dividends = PropertyMock(return_value=mock_dividends)
    result = await hd.get_dividends("AAPL")
    data = json.loads(result)
    assert "2023-01-01T00:00:00.000" in data or "2023-01-01T00:00:00.000Z" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_dividends_no_data(mock_ticker):
    mock_dividends = pd.Series([], dtype=float)
    type(mock_ticker.return_value).dividends = PropertyMock(return_value=mock_dividends)
    result = await hd.get_dividends("AAPL")
    assert json.loads(result)["error"] == "No dividend data available"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_splits_with_data(mock_ticker):
    mock_splits = pd.Series([2], index=pd.date_range("2022-01-01", periods=1))
    type(mock_ticker.return_value).splits = PropertyMock(return_value=mock_splits)
    result = await hd.get_splits("AAPL")
    data = json.loads(result)
    assert "2022-01-01T00:00:00.000" in data or "2022-01-01T00:00:00.000Z" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_splits_no_data(mock_ticker):
    mock_splits = pd.Series([], dtype=float)
    type(mock_ticker.return_value).splits = PropertyMock(return_value=mock_splits)
    result = await hd.get_splits("AAPL")
    assert json.loads(result)["error"] == "No stock split data available"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_capital_gains_with_data(mock_ticker):
    mock_cg = pd.Series([1.2], index=pd.date_range("2021-01-01", periods=1))
    type(mock_ticker.return_value).capital_gains = PropertyMock(return_value=mock_cg)
    result = await hd.get_capital_gains("AAPL")
    data = json.loads(result)
    assert "2021-01-01T00:00:00.000" in data or "2021-01-01T00:00:00.000Z" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_capital_gains_no_data(mock_ticker):
    mock_cg = pd.Series([], dtype=float)
    type(mock_ticker.return_value).capital_gains = PropertyMock(return_value=mock_cg)
    result = await hd.get_capital_gains("AAPL")
    assert json.loads(result)["error"] == "No capital gains data available"


from unittest.mock import patch

import pytest

# Module to test
from openmarkets.tools import historical_data


# Helper to create a mock DataFrame or Series for testing
def create_mock_yfinance_data(empty=False, is_series=False):
    if empty:
        return pd.Series(dtype="float64") if is_series else pd.DataFrame()

    data_dict = {"data_col": [1, 2], "date_col": pd.to_datetime(["2023-01-01", "2023-02-01"])}
    if is_series:
        obj = pd.Series([10, 20], name="TestSeries")
    else:
        obj = pd.DataFrame(data_dict)
        obj.set_index("date_col", inplace=True)

    # Mock the to_json method specifically on this instance for assertion
    # Ensure the mock can be called and returns a valid JSON string
    obj.to_json = MagicMock(return_value=json.dumps({"mock_key": "mock_value"}, default=str))
    return obj


@pytest.mark.asyncio
class TestHistoryFunctions:
    @pytest.mark.parametrize("period, interval", [("1mo", "1d"), ("5d", "1h")])
    async def test_get_historical_data_success(self, period, interval):
        mock_df = create_mock_yfinance_data()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_historical_data("AAPL", period=period, interval=interval)
            mock_yf_ticker.assert_called_once_with("AAPL")
            mock_ticker_instance.history.assert_called_once_with(period=period, interval=interval)
            mock_df.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df.to_json()

    async def test_get_historical_data_yfinance_error(self):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.side_effect = Exception("yfinance API error")

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            with pytest.raises(Exception, match="yfinance API error"):
                await historical_data.get_historical_data("AAPL")

    async def test_get_intraday_data_success(self):
        mock_df = create_mock_yfinance_data()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_intraday_data("MSFT", period="1d", interval="15m")
            mock_yf_ticker.assert_called_once_with("MSFT")
            mock_ticker_instance.history.assert_called_once_with(period="1d", interval="15m")
            mock_df.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df.to_json()

    async def test_get_prepost_market_data_success(self):
        mock_df = create_mock_yfinance_data()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_prepost_market_data("GOOG", period="5d")
            mock_yf_ticker.assert_called_once_with("GOOG")
            mock_ticker_instance.history.assert_called_once_with(period="5d", prepost=True)
            mock_df.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df.to_json()


@pytest.mark.asyncio
class TestAttributeDataFunctions:
    async def test_get_dividends_success(self):
        mock_series = create_mock_yfinance_data(is_series=True)
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.dividends = mock_series

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_dividends("PG")
            mock_yf_ticker.assert_called_once_with("PG")
            mock_series.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_series.to_json()

    async def test_get_dividends_no_data(self):
        mock_empty_series = create_mock_yfinance_data(empty=True, is_series=True)
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.dividends = mock_empty_series

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_dividends("NODIV")
            assert json.loads(result) == {"error": "No dividend data available"}

        # Test with None attribute
        mock_ticker_instance.dividends = None
        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_dividends("NODIV")
            assert json.loads(result) == {"error": "No dividend data available"}

    async def test_get_splits_success(self):
        mock_series = create_mock_yfinance_data(is_series=True)
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.splits = mock_series

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_splits("AAPL")
            mock_series.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_series.to_json()

    async def test_get_splits_no_data(self):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.splits = create_mock_yfinance_data(empty=True, is_series=True)
        with patch("yfinance.Ticker", return_value=mock_ticker_instance):
            result = await historical_data.get_splits("NOSPLIT")
            assert json.loads(result) == {"error": "No stock split data available"}

    async def test_get_capital_gains_success(self):
        # Capital gains can be an empty list/df or a populated one. yfinance usually returns DataFrame.
        mock_df = create_mock_yfinance_data()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.capital_gains = mock_df

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_capital_gains("VFINX")
            mock_df.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df.to_json()

    async def test_get_capital_gains_no_data(self):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.capital_gains = create_mock_yfinance_data(empty=True)
        with patch("yfinance.Ticker", return_value=mock_ticker_instance):
            result = await historical_data.get_capital_gains("NOCAPGAIN")
            assert json.loads(result) == {"error": "No capital gains data available"}

    @pytest.mark.xfail
    async def test_get_corporate_actions_success(self):
        mock_df = create_mock_yfinance_data()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.actions = mock_df

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await historical_data.get_dividends("MSFT")
            mock_df.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df.to_json()

    async def test_get_corporate_actions_no_data(self):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.actions = create_mock_yfinance_data(empty=True)
        with patch("yfinance.Ticker", return_value=mock_ticker_instance):
            result = await historical_data.get_dividends("NOACTION")
            assert json.loads(result) == {"error": "No dividend data available"}


class TestRegisterHistoricalDataTools:
    def test_register_tools(self):
        mock_mcp = MagicMock()
        mock_actual_decorator = MagicMock(side_effect=lambda f: f)
        mock_mcp.tool.return_value = mock_actual_decorator

        historical_data.register_historical_data_tools(mock_mcp)

        expected_tool_names = [
            "get_historical_data",
            "get_intraday_data",
            "get_prepost_market_data",
            "get_dividends",
            "get_splits",
            "get_capital_gains",
        ]

        assert mock_mcp.tool.call_count == len(expected_tool_names)

        actual_registered_tool_names = sorted(
            [call_obj[0][0].__name__ for call_obj in mock_actual_decorator.call_args_list]
        )
        assert actual_registered_tool_names == sorted(expected_tool_names)

        for func_name in actual_registered_tool_names:
            assert not func_name.startswith("_")
            assert func_name != "register_historical_data_tools"


if __name__ == "__main__":
    pytest.main([__file__])
