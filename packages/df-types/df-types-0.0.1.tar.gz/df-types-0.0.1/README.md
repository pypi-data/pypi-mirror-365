# df_types

Python tool for generating dataclass type files for pandas DataFrame rows.

## Installation

```bash
pip install df-types
```

## Usage

```python
from df_types import DFTypes
import pandas as pd

df = pd.read_csv("dev.csv")

dft = DFTypes(df)
dft.write_types()  # creates typed_df.py in the current directory
# see df_types.config.DFTypesConfig for options

# then use the types file as a module
from typed_df import convert, iter_dataclasses

df = convert(df)

for dc in iter_dataclasses(df):
    ...  # do something with dc
```

In the above example, `convert` and `iter_dataclasses` are generated from `typed_df.py`. `convert` is a function that takes a DataFrame and normalizes the column names, replacing `NaN` values with `None` (by default).

`iter_dataclasses` is a generator that takes a DataFrame and yields a dataclass for each row.

## Features

Currently, the following features are supported:

- Literal types for primitive types (e.g. `Literal["some_type", "other_type"]`)
- Union types (e.g. `int | float`)
- Optional types (e.g. `int | None`)
- Imported/custom types (e.g. `pd.Timestamp`, user defined types)

In the future, I'd like to add support for typed containers (e.g. `Dict[str, int]`, `List[int]`).

## License

MIT
