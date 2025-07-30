import json
from unittest.mock import patch

import pytest

import openmarkets.tools.funds as funds


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_profile_success(mock_ticker):
    mock_info = {
        "symbol": "VTI",
        "longName": "Vanguard Total Stock Market ETF",
        "fundFamily": "Vanguard",
        "category": "Large Blend",
        "fundInceptionDate": "2001-05-24",
        "totalAssets": 1000000000,
        "annualReportExpenseRatio": 0.03,
        "beta3Year": 1.02,
        "yield": 1.5,
        "ytdReturn": 0.12,
        "threeYearAverageReturn": 0.10,
        "fiveYearAverageReturn": 0.11,
        "morningStarRiskRating": 4,
        "morningStarOverallRating": 5,
        "currency": "USD",
        "navPrice": 200.0,
    }
    mock_ticker.return_value.info = mock_info
    result = await funds.get_fund_profile("VTI")
    data = json.loads(result)
    assert data["symbol"] == "VTI"
    assert data["longName"] == "Vanguard Total Stock Market ETF"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_profile_error(mock_ticker):
    mock_ticker.side_effect = Exception("fail")
    result = await funds.get_fund_profile("BAD")
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_holdings_success(mock_ticker):
    mock_info = {"holdings": [{"symbol": "AAPL"}, {"symbol": "MSFT"}, {"symbol": "GOOG"}]}
    mock_ticker.return_value.info = mock_info
    result = await funds.get_fund_holdings("VTI", count=2)
    data = json.loads(result)
    assert data["symbol"] == "VTI"
    assert len(data["top_holdings"]) == 2


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_holdings_no_data(mock_ticker):
    mock_ticker.return_value.info = {}
    result = await funds.get_fund_holdings("VTI")
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_sector_allocation_success(mock_ticker):
    mock_info = {
        "sectorWeightings": {"Tech": 0.5},
        "bondRatings": {"AAA": 0.2},
        "bondHoldings": 10,
        "stockHoldings": 90,
    }
    mock_ticker.return_value.info = mock_info
    result = await funds.get_fund_sector_allocation("VTI")
    data = json.loads(result)
    assert data["sectorWeightings"]["Tech"] == 0.5


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_sector_allocation_error(mock_ticker):
    mock_ticker.side_effect = Exception("fail")
    result = await funds.get_fund_sector_allocation("BAD")
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_performance_success(mock_ticker):
    mock_info = {
        "ytdReturn": 0.1,
        "oneYearReturn": 0.09,
        "threeYearAverageReturn": 0.08,
        "fiveYearAverageReturn": 0.07,
        "tenYearAverageReturn": 0.06,
        "alpha": 1.1,
        "beta": 1.0,
        "rSquared": 0.95,
        "standardDeviation": 0.2,
        "sharpeRatio": 1.2,
        "treynorRatio": 0.5,
    }
    mock_ticker.return_value.info = mock_info
    result = await funds.get_fund_performance("VTI")
    data = json.loads(result)
    assert data["ytdReturn"] == 0.1


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_fund_performance_error(mock_ticker):
    mock_ticker.side_effect = Exception("fail")
    result = await funds.get_fund_performance("BAD")
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_compare_funds_success(mock_ticker):
    mock_info = {
        "longName": "Fund",
        "annualReportExpenseRatio": 0.01,
        "yield": 1.2,
        "ytdReturn": 0.1,
        "threeYearAverageReturn": 0.09,
        "fiveYearAverageReturn": 0.08,
        "totalAssets": 1000000,
        "beta": 1.0,
        "morningStarOverallRating": 5,
    }
    mock_ticker.return_value.info = mock_info
    result = await funds.compare_funds(["VTI", "VOO"])
    data = json.loads(result)
    assert "fund_comparison" in data
    assert len(data["fund_comparison"]) == 2


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_compare_funds_error(mock_ticker):
    mock_ticker.side_effect = Exception("fail")
    result = await funds.compare_funds(["BAD"])
    data = json.loads(result)
    assert "error" in data
