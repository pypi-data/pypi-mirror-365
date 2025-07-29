import keyword
import re
from typing import Iterable, Generator

_deduplicate_underscore_pattern = re.compile(r"_{2,}")


def _normalize_char(c: str) -> str:
    """
    Drop non-alphanumeric characters and convert spaces and hyphens to underscores
    """
    return "_" if c in (" ", "-", "_") else (c if c.isalnum() else "")


def _normalize(column: str) -> str:
    """
    Normalize column name to a valid Python identifier
    """
    column = column.strip().lower()
    column = "".join(_normalize_char(c) for c in column)
    if not column:
        column = "col"
    elif column[0].isdigit():
        column = "col_" + column
    column = _deduplicate_underscore_pattern.sub("_", column)
    return column


def make_unique(names: Iterable[str]) -> Generator[str, None, None]:
    """
    Add suffixes to column names to make them unique
    """
    seen = set()
    for name in names:
        while name in seen or keyword.iskeyword(name):
            name += "_"
        seen.add(name)
        yield name


def normalize_columns(columns: list[str]) -> list[str]:
    """
    Normalize a list of column names to unique, valid Python identifiers
    """
    return list(make_unique(_normalize(column) for column in columns))
