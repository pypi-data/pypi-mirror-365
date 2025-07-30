import json
from unittest.mock import MagicMock, patch

import pytest

import openmarkets.tools.market_data as md


@pytest.mark.xfail
@patch("yfinance.Ticker")
async def test_get_market_status_success(mock_ticker_cls):
    mock_ticker = MagicMock()
    mock_ticker.state = {
        "marketState": "OPEN",
        "exchangeTimezoneName": "America/New_York",
        "regularMarketTime": 1234567890,
        "preMarketPrice": 400.0,
        "postMarketPrice": 405.0,
        "currency": "USD",
    }
    mock_ticker_cls.return_value = mock_ticker

    result = await md.get_market_status("US")
    data = json.loads(result)
    assert data["marketState"] == "OPEN"
    assert data["exchangeTimezone"] == "America/New_York"
    assert data["regularMarketTime"] == 1234567890
    assert data["preMarketPrice"] == 400.0
    assert data["postMarketPrice"] == 405.0
    assert data["currency"] == "USD"


@pytest.mark.xfail
@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_sector_performance_success(mock_ticker_cls):
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "currentPrice": 100.0,
        "volume": 10000,
    }
    # Mock DataFrame for history
    mock_hist = MagicMock()
    mock_hist.__len__.return_value = 2
    mock_hist.iloc.__getitem__.side_effect = [
        {"Close": 90.0, "Volume": 9000},
        {"Close": 100.0, "Volume": 10000},
    ]
    mock_ticker.history.return_value = mock_hist
    mock_ticker_cls.return_value = mock_ticker

    result = await md.get_sector_performance()
    data = json.loads(result)
    assert "sector_performance" in data
    assert isinstance(data["sector_performance"], list)
    assert data["sector_performance"][0]["current_price"] == 100.0


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_sector_performance_exception(mock_ticker_cls):
    mock_ticker_cls.side_effect = Exception("fail")
    result = await md.get_sector_performance()
    data = json.loads(result)
    assert "error" in data


@pytest.mark.xfail
@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_index_data_success(mock_ticker_cls):
    mock_ticker = MagicMock()
    # Mock DataFrame for history
    mock_hist = MagicMock()
    mock_hist.__len__.return_value = 2
    mock_hist.iloc.__getitem__.side_effect = [
        {"Close": 3900.0, "Volume": 100000},
        {"Close": 4000.0, "Volume": 110000},
    ]
    mock_ticker.history.return_value = mock_hist
    mock_ticker_cls.return_value = mock_ticker

    result = await md.get_index_data(indices=["^GSPC"])
    data = json.loads(result)
    assert "indices" in data
    assert data["indices"][0]["symbol"] == "^GSPC"
    assert data["indices"][0]["current_price"] == 4000.0


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_index_data_exception(mock_ticker_cls):
    mock_ticker_cls.side_effect = Exception("fail")
    result = await md.get_index_data(indices=["^GSPC"])
    data = json.loads(result)
    assert "error" in data
