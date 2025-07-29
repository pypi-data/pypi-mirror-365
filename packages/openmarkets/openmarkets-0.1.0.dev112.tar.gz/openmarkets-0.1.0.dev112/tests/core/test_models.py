import pytest
from pydantic import ValidationError

from openmarkets.core.models import Price, Symbol


# Tests for Symbol model
def test_create_symbol_success():
    """Test successful creation of a Symbol instance."""
    symbol = Symbol(name="AAPL")
    assert symbol.name == "AAPL"


def test_symbol_name_must_be_uppercase_valid():
    """Test Symbol validation passes for uppercase name."""
    symbol = Symbol(name="GOOG")
    assert symbol.name == "GOOG"


def test_symbol_name_must_be_uppercase_invalid():
    """Test Symbol validation fails for lowercase name."""
    with pytest.raises(ValidationError) as excinfo:
        Symbol(name="aapl")
    assert "Symbol name must be uppercase" in str(excinfo.value)


def test_symbol_serialization():
    """Test Symbol model serialization."""
    symbol = Symbol(name="MSFT")
    assert symbol.model_dump() == {"name": "MSFT"}


def test_symbol_deserialization():
    """Test Symbol model deserialization."""
    data = {"name": "TSLA"}
    symbol = Symbol.model_validate(data)
    assert symbol.name == "TSLA"


def test_symbol_deserialization_invalid_type():
    """Test Symbol model deserialization with invalid type for name."""
    data = {"name": 123}
    with pytest.raises(ValidationError):
        Symbol.model_validate(data)


# Tests for Price model
def test_create_price_success():
    """Test successful creation of a Price instance."""
    symbol = Symbol(name="AMZN")
    price = Price(symbol=symbol, value=150.75)
    assert price.symbol.name == "AMZN"
    assert price.value == 150.75


def test_price_value_must_be_positive_valid():
    """Test Price validation passes for positive value."""
    symbol = Symbol(name="NVDA")
    price = Price(symbol=symbol, value=0.01)
    assert price.value == 0.01


def test_price_value_must_be_positive_invalid_zero():
    """Test Price validation fails for zero value."""
    symbol = Symbol(name="META")
    with pytest.raises(ValidationError) as excinfo:
        Price(symbol=symbol, value=0.0)
    assert "Input should be greater than 0" in str(excinfo.value)  # Default Pydantic message for PositiveFloat


def test_price_value_must_be_positive_invalid_negative():
    """Test Price validation fails for negative value."""
    symbol = Symbol(name="JPM")
    with pytest.raises(ValidationError) as excinfo:
        Price(symbol=symbol, value=-10.5)
    assert "Input should be greater than 0" in str(excinfo.value)  # Default Pydantic message for PositiveFloat


def test_price_serialization():
    """Test Price model serialization."""
    symbol = Symbol(name="V")
    price = Price(symbol=symbol, value=250.00)
    expected_dict = {"symbol": {"name": "V"}, "value": 250.00}
    assert price.model_dump() == expected_dict


def test_price_deserialization():
    """Test Price model deserialization."""
    data = {"symbol": {"name": "BAC"}, "value": 40.25}
    price = Price.model_validate(data)
    assert price.symbol.name == "BAC"
    assert price.value == 40.25


def test_price_deserialization_invalid_symbol_type():
    """Test Price model deserialization with invalid type for symbol."""
    data = {"symbol": "NOTASYMBOL", "value": 40.25}
    with pytest.raises(ValidationError):
        Price.model_validate(data)


def test_price_deserialization_invalid_value_type():
    """Test Price model deserialization with invalid type for value."""
    data = {"symbol": {"name": "XOM"}, "value": "not_a_float"}
    with pytest.raises(ValidationError):
        Price.model_validate(data)


def test_price_with_invalid_symbol_instance():
    """Test Price creation with an invalid Symbol instance (e.g., lowercase name)."""
    with pytest.raises(ValidationError, match="Symbol name must be uppercase"):
        Price(symbol=Symbol(name="invalid"), value=100.0)


def test_price_symbol_is_symbol_instance():
    """Test that Price.symbol is an instance of Symbol."""
    price = Price(symbol=Symbol(name="TEST"), value=1.0)
    assert isinstance(price.symbol, Symbol)
