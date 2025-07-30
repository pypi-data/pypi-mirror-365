import pytest

from openmarkets.core.utils import normalize_symbol


@pytest.mark.parametrize(
    "input_symbol, expected_output",
    [
        ("AAPL", "AAPL"),  # No changes needed
        ("aapl", "AAPL"),  # Needs uppercasing
        ("  GOOG  ", "GOOG"),  # Leading/trailing whitespace
        ("BRK.A", "BRK_A"),  # Contains a dot
        ("MSFT-US", "MSFT_US"),  # Contains a hyphen
        ("  arkk.invest-us ", "ARKK_INVEST_US"),  # Mix of dot, hyphen, whitespace, casing
        ("BHP.AX", "BHP_AX"),  # Dot and casing
        ("RIO-L", "RIO_L"),  # Hyphen and casing
        ("   spaced.out-symbol  ", "SPACED_OUT_SYMBOL"),  # All transformations
        ("", ""),  # Empty string
        ("   ", ""),  # String with only whitespace
        ("ALREADY_NORMALIZED", "ALREADY_NORMALIZED"),  # Already has underscore
        ("DOT.AND-HYPHEN", "DOT_AND_HYPHEN"),  # Both dot and hyphen
        (" multiple.dots.here ", "MULTIPLE_DOTS_HERE"),  # Multiple dots
        (
            "--multiple-hyphens--",
            "MULTIPLE_HYPHENS",
        ),  # Multiple hyphens (leading/trailing become part of symbol then replaced)
        (" .leading-dot-hyphen_ ", "LEADING_DOT_HYPHEN_"),  # Leading dot/hyphen after strip
    ],
)
def test_normalize_symbol_various_cases(input_symbol, expected_output):
    """Test normalize_symbol with various valid string inputs."""
    assert normalize_symbol(input_symbol) == expected_output


def test_normalize_symbol_non_string_input():
    """Test normalize_symbol with non-string inputs (e.g., None, int)."""
    # Based on the current implementation, it should return "" for non-strings
    assert normalize_symbol(None) == ""  # type: ignore
    assert normalize_symbol(123) == ""  # type: ignore
    assert normalize_symbol([]) == ""  # type: ignore
    assert normalize_symbol({}) == ""  # type: ignore


def test_normalize_symbol_real_world_examples():
    """Test with a few more realistic examples."""
    assert normalize_symbol("vbt.ax") == "VBT_AX"
    assert normalize_symbol("  XOM ") == "XOM"
    assert normalize_symbol("BRK-B") == "BRK_B"
    assert normalize_symbol("csco.us-nasdaq") == "CSCO_US_NASDAQ"
    assert normalize_symbol(" HYG ") == "HYG"
    assert normalize_symbol("GLD.US.ARCA") == "GLD_US_ARCA"


if __name__ == "__main__":
    pytest.main()
