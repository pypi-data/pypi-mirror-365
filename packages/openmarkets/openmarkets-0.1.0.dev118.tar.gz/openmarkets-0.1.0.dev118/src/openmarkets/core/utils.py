# General utility functions


def normalize_symbol(symbol: str) -> str:
    """
    Normalizes a trading symbol.

    The normalization process includes:
    - Removing leading/trailing whitespace from the input.
    - Converting the symbol to uppercase.
    - Replacing dots ('.') and hyphens ('-') with spaces.
    - Splitting the result by whitespace (which handles multiple spaces/separators).
    - Joining the parts with a single underscore ('_').

    Example: " aapl . us " becomes "AAPL_US"
             "--foo-bar--" becomes "FOO_BAR"
             " .baz.qux- " becomes "BAZ_QUX"
    """
    if not isinstance(symbol, str):
        return ""  # Handle non-string input

    normalized = symbol.strip()  # 1. Remove leading/trailing whitespace
    normalized = normalized.upper()  # 2. Convert to uppercase

    # 3. Replace dots and hyphens with a space.
    # This helps ensure that sequences like ".-" or ". ." are treated as single separator occurrences
    # after splitting by whitespace.
    normalized = normalized.replace(".", " ")
    normalized = normalized.replace("-", " ")

    # 4. Split by whitespace. This handles multiple spaces between words
    # (e.g. "A  B" becomes ["A", "B"]) and also removes leading/trailing spaces
    # if they were introduced by replacements at the ends of the string.
    parts = normalized.split()

    # 5. Join with a single underscore. If 'parts' is empty (e.g. input was "  .  "),
    # this will result in an empty string, which is correct.
    return "_".join(parts)
