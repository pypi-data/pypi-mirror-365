import json
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

import openmarkets.tools.financial_statements as fs


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_income_statement_annual(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "income"}'
    mock_ticker = MagicMock()
    type(mock_ticker).income_stmt = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_income_statement("AAPL", quarterly=False)
    assert result == '{"mock": "income"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_income_statement_quarterly(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "quarterly_income"}'
    mock_ticker = MagicMock()
    type(mock_ticker).quarterly_income_stmt = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_income_statement("AAPL", quarterly=True)
    assert result == '{"mock": "quarterly_income"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_income_statement_no_data(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = True
    mock_ticker = MagicMock()
    type(mock_ticker).income_stmt = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_income_statement("AAPL", quarterly=False)
    assert json.loads(result)["error"] == "No income statement data available"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_balance_sheet_annual(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "balance"}'
    mock_ticker = MagicMock()
    type(mock_ticker).balance_sheet = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_balance_sheet("AAPL", quarterly=False)
    assert result == '{"mock": "balance"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_balance_sheet_quarterly(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "quarterly_balance"}'
    mock_ticker = MagicMock()
    type(mock_ticker).quarterly_balance_sheet = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_balance_sheet("AAPL", quarterly=True)
    assert result == '{"mock": "quarterly_balance"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_balance_sheet_no_data(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = True
    mock_ticker = MagicMock()
    type(mock_ticker).balance_sheet = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_balance_sheet("AAPL", quarterly=False)
    assert json.loads(result)["error"] == "No balance sheet data available"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_cash_flow_annual(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "cashflow"}'
    mock_ticker = MagicMock()
    type(mock_ticker).cashflow = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_cash_flow("AAPL", quarterly=False)
    assert result == '{"mock": "cashflow"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_cash_flow_quarterly(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "quarterly_cashflow"}'
    mock_ticker = MagicMock()
    type(mock_ticker).quarterly_cashflow = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_cash_flow("AAPL", quarterly=True)
    assert result == '{"mock": "quarterly_cashflow"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_cash_flow_no_data(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = True
    mock_ticker = MagicMock()
    type(mock_ticker).cashflow = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_cash_flow("AAPL", quarterly=False)
    assert json.loads(result)["error"] == "No cash flow data available"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_earnings(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_json.return_value = '{"mock": "earnings"}'
    mock_ticker = MagicMock()
    type(mock_ticker).earnings = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_income_statement("AAPL")
    assert result == '{"error": "No income statement data available"}'


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_earnings_no_data(mock_ticker_cls):
    mock_df = MagicMock()
    mock_df.empty = True
    mock_ticker = MagicMock()
    type(mock_ticker).earnings = PropertyMock(return_value=mock_df)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_income_statement("AAPL")
    assert json.loads(result)["error"] == "No income statement data available"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_financials_summary(mock_ticker_cls):
    mock_info = {
        "totalRevenue": 100,
        "revenueGrowth": 0.1,
        "grossProfits": 50,
        "grossMargins": 0.5,
        "operatingMargins": 0.2,
        "profitMargins": 0.15,
        "operatingCashflow": 30,
        "freeCashflow": 20,
        "totalCash": 10,
        "totalDebt": 5,
        "totalCashPerShare": 1.5,
        "earningsGrowth": 0.05,
        "currentRatio": 2.0,
        "quickRatio": 1.8,
        "returnOnAssets": 0.12,
        "returnOnEquity": 0.18,
        "debtToEquity": 0.3,
    }
    mock_ticker = MagicMock()
    type(mock_ticker).info = PropertyMock(return_value=mock_info)
    mock_ticker_cls.return_value = mock_ticker

    result = await fs.get_financials_summary("AAPL")
    data = json.loads(result)
    assert data["totalRevenue"] == 100
    assert data["grossMargins"] == 0.5


from unittest.mock import patch

import pandas as pd
import pytest

# Module to test
from openmarkets.tools import financial_statements


# Helper to create a mock DataFrame
def create_mock_df(empty=False):
    if empty:
        # For empty DataFrames, yfinance might return them without a to_json method
        # or it might be there. For testing, we'll assume it might not be called.
        return pd.DataFrame()
    # For non-empty, ensure to_json is a MagicMock
    df_dict = {"col1": [1], "col2": [2]}  # Minimal non-empty data
    df = pd.DataFrame(df_dict)
    # Mock the to_json method specifically on this instance for assertion
    df.to_json = MagicMock(return_value=json.dumps(df_dict))  # Simplified return for testing
    return df


@pytest.mark.asyncio
class TestFinancialStatementFunctions:
    @pytest.mark.parametrize("quarterly_flag", [True, False])
    async def test_get_income_statement(self, quarterly_flag):
        mock_df_non_empty = create_mock_df()
        mock_df_empty = create_mock_df(empty=True)

        mock_ticker_instance = MagicMock()

        # Scenario 1: Non-empty dataframe
        if quarterly_flag:
            mock_ticker_instance.quarterly_income_stmt = mock_df_non_empty
        else:
            mock_ticker_instance.income_stmt = mock_df_non_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await financial_statements.get_income_statement("AAPL", quarterly=quarterly_flag)
            mock_yf_ticker.assert_called_once_with("AAPL")
            mock_df_non_empty.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df_non_empty.to_json()

        # Reset mocks for scenario 2 if necessary (patch creates new mock_ticker_instance each time)
        mock_ticker_instance_empty = MagicMock()
        # Scenario 2: Empty dataframe
        if quarterly_flag:
            mock_ticker_instance_empty.quarterly_income_stmt = mock_df_empty
        else:
            mock_ticker_instance_empty.income_stmt = mock_df_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance_empty) as mock_yf_ticker:
            result = await financial_statements.get_income_statement("AAPL", quarterly=quarterly_flag)
            mock_yf_ticker.assert_called_once_with("AAPL")
            expected_error = json.dumps({"error": "No income statement data available"})
            assert result == expected_error

    @pytest.mark.parametrize("quarterly_flag", [True, False])
    async def test_get_balance_sheet(self, quarterly_flag):
        mock_df_non_empty = create_mock_df()
        mock_df_empty = create_mock_df(empty=True)

        mock_ticker_instance = MagicMock()
        if quarterly_flag:
            mock_ticker_instance.quarterly_balance_sheet = mock_df_non_empty
        else:
            mock_ticker_instance.balance_sheet = mock_df_non_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await financial_statements.get_balance_sheet("MSFT", quarterly=quarterly_flag)
            mock_yf_ticker.assert_called_once_with("MSFT")
            mock_df_non_empty.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df_non_empty.to_json()

        mock_ticker_instance_empty = MagicMock()
        if quarterly_flag:
            mock_ticker_instance_empty.quarterly_balance_sheet = mock_df_empty
        else:
            mock_ticker_instance_empty.balance_sheet = mock_df_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance_empty) as mock_yf_ticker:
            result = await financial_statements.get_balance_sheet("MSFT", quarterly=quarterly_flag)
            mock_yf_ticker.assert_called_once_with("MSFT")
            expected_error = json.dumps({"error": "No balance sheet data available"})
            assert result == expected_error

    @pytest.mark.parametrize("quarterly_flag", [True, False])
    async def test_get_cash_flow(self, quarterly_flag):
        mock_df_non_empty = create_mock_df()
        mock_df_empty = create_mock_df(empty=True)

        mock_ticker_instance = MagicMock()
        if quarterly_flag:
            mock_ticker_instance.quarterly_cashflow = mock_df_non_empty
        else:
            mock_ticker_instance.cashflow = mock_df_non_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await financial_statements.get_cash_flow("GOOG", quarterly=quarterly_flag)
            mock_yf_ticker.assert_called_once_with("GOOG")
            mock_df_non_empty.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df_non_empty.to_json()

        mock_ticker_instance_empty = MagicMock()
        if quarterly_flag:
            mock_ticker_instance_empty.quarterly_cashflow = mock_df_empty
        else:
            mock_ticker_instance_empty.cashflow = mock_df_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance_empty) as mock_yf_ticker:
            result = await financial_statements.get_cash_flow("GOOG", quarterly=quarterly_flag)
            mock_yf_ticker.assert_called_once_with("GOOG")
            expected_error = json.dumps({"error": "No cash flow data available"})
            assert result == expected_error

    async def test_get_income_statement_2(self):
        mock_df_non_empty = create_mock_df()
        mock_df_empty = create_mock_df(empty=True)

        mock_ticker_instance = MagicMock()
        mock_ticker_instance.income_stmt = mock_df_non_empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result = await financial_statements.get_income_statement("TSLA")
            mock_yf_ticker.assert_called_once_with("TSLA")
            mock_df_non_empty.to_json.assert_called_once_with(date_format="iso")
            assert result == mock_df_non_empty.to_json()

        mock_ticker_instance_empty = MagicMock()
        mock_ticker_instance_empty.income_stmt = mock_df_empty
        with patch("yfinance.Ticker", return_value=mock_ticker_instance_empty) as mock_yf_ticker:
            result = await financial_statements.get_income_statement("TSLA")
            mock_yf_ticker.assert_called_once_with("TSLA")
            expected_error = json.dumps({"error": "No income statement data available"})
            assert result == expected_error


@pytest.mark.asyncio
class TestGetFinancialsSummary:
    async def test_get_financials_summary_all_data(self):
        mock_info_data = {
            "totalRevenue": 1000,
            "revenueGrowth": 0.1,
            "grossProfits": 500,
            "grossMargins": 0.5,
            "operatingMargins": 0.2,
            "profitMargins": 0.15,
            "operatingCashflow": 300,
            "freeCashflow": 200,
            "totalCash": 100,
            "totalDebt": 50,
            "totalCashPerShare": 1.0,
            "earningsGrowth": 0.12,
            "currentRatio": 2.0,
            "quickRatio": 1.5,
            "returnOnAssets": 0.05,
            "returnOnEquity": 0.1,
            "debtToEquity": 0.25,
        }
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info_data

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result_str = await financial_statements.get_financials_summary("FB")
            mock_yf_ticker.assert_called_once_with("FB")

            result_json = json.loads(result_str)
            assert result_json["totalRevenue"] == 1000
            assert result_json["debtToEquity"] == 0.25
            assert len(result_json.keys()) == len(mock_info_data.keys())

    async def test_get_financials_summary_missing_data(self):
        mock_info_data = {
            "totalRevenue": 1000,
            "revenueGrowth": 0.1,
            "grossMargins": 0.5,
            "operatingMargins": 0.2,
            "operatingCashflow": 300,
            "freeCashflow": 200,
        }
        expected_summary_structure_keys = [
            "totalRevenue",
            "revenueGrowth",
            "grossProfits",
            "grossMargins",
            "operatingMargins",
            "profitMargins",
            "operatingCashflow",
            "freeCashflow",
            "totalCash",
            "totalDebt",
            "totalCashPerShare",
            "earningsGrowth",
            "currentRatio",
            "quickRatio",
            "returnOnAssets",
            "returnOnEquity",
            "debtToEquity",
        ]

        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info_data

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result_str = await financial_statements.get_financials_summary("AMZN")
            mock_yf_ticker.assert_called_once_with("AMZN")

            result_json = json.loads(result_str)

            assert result_json["totalRevenue"] == 1000
            assert result_json["grossProfits"] is None
            assert result_json["profitMargins"] is None
            assert result_json["totalCash"] is None

            for key in expected_summary_structure_keys:
                assert key in result_json


class TestRegisterFinancialStatementsTools:
    def test_register_tools(self):
        mock_mcp = MagicMock()

        # This mock_actual_decorator will be what mcp.tool() returns.
        mock_actual_decorator = MagicMock(side_effect=lambda f: f)  # side_effect preserves the function

        # Configure mcp.tool (which is a MagicMock by default when mock_mcp is MagicMock)
        # so that when it's called (as mcp.tool()), it returns our mock_actual_decorator.
        mock_mcp.tool.return_value = mock_actual_decorator

        financial_statements.register_financial_statements_tools(mock_mcp)

        expected_tool_names = [
            "get_income_statement",
            "get_balance_sheet",
            "get_cash_flow",
            "get_financials_summary",
        ]

        # Assert that mcp.tool() was called (once for each tool)
        assert mock_mcp.tool.call_count == len(expected_tool_names)

        actual_registered_tool_names = []
        # Now, check the calls to the mock_actual_decorator
        for call_obj in mock_actual_decorator.call_args_list:
            # call_obj is a call tuple (args, kwargs). args is (func_object,)
            func_object = call_obj[0][0]
            actual_registered_tool_names.append(func_object.__name__)

        assert sorted(actual_registered_tool_names) == sorted(expected_tool_names)

        for func_name in actual_registered_tool_names:
            assert not func_name.startswith("_")
            assert func_name != "register_financial_statements_tools"


if __name__ == "__main__":
    pytest.main([__file__])
