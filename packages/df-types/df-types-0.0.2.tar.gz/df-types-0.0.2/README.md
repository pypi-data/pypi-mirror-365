# df-types

[![PyPI version](https://badge.fury.io/py/df-types.svg)](https://badge.fury.io/py/df-types)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python tool for automatically generating dataclass definitions from pandas DataFrames.

## Getting Started

```bash
pip install df-types
```

```python
from df_types import DFTypes
import pandas as pd
import random

# Load your data
df = pd.DataFrame({
    "id": list(range(1, 301)),
    "name": ["Alice", "Bob", "Charlie"] * 100,
    "age": [random.randint(18, 100) for _ in range(300)],
    "prefers-pizza": [random.choice([True, False]) for _ in range(300)]  # Not a valid Python identifier, will be normalized
})

# Generate type definitions
dft = DFTypes(df)
dft.write_types()  # Creates typed_df.py

# Creates the following dataclass:
#
# @dataclass(slots=True)
# class TypedRowData:
#     id: int
#     name: Literal['Alice', 'Bob', 'Charlie']
#     age: int
#     prefers_pizza: bool

# Use the generated types
from typed_df import convert, iter_dataclasses

df_typed = convert(df)  # Converts NaNs to None, normalizes column names to Python identifiers
for row_data in iter_dataclasses(df_typed):
    # Each row_data is now a typed dataclass
    print(f"ID: {row_data.id}, Name: {row_data.name}, Age: {row_data.age}, Prefers Pizza: {row_data.prefers_pizza}")
```

## Features

### Supported Types

| Feature             | Example                       | Description                            |
| ------------------- | ----------------------------- | -------------------------------------- |
| **Literal Types**   | `Literal["A", "B", "C"]`      | For categorical data with known values |
| **Union Types**     | `int \| float`                | For columns with mixed numeric types   |
| **Optional Types**  | `str \| None`                 | For columns with missing values        |
| **Custom Types**    | `pd.Timestamp`, `Decimal`     | Import and use external types          |
| **Primitive Types** | `int`, `str`, `bool`, `float` | Standard Python types                  |

### Configuration

```python
from df_types.config import DFTypesConfig

# Basic options
config = DFTypesConfig(
    filename="my_types.py",
    class_name="MyRow",  # Default is "TypedRowData"
    max_literal_values=10  # Increase if you have more categories you want to infer as Literal types
)

dft = DFTypes(df, config=config)
dft.write_types()

from my_types import convert, iter_dataclasses, MyRow

# Use the generated types
```

## Considerations

If a type cannot be imported from the generated file, it will be given the type hint `object` and a warning will be printed. Most often this occurs because the type is contained in the calling module (e.g., `main.py` which imports `df_types` and provides `CustomType` that is contained in the DataFrame). You can manually move the type definition to another file to avoid this warning.

Due to sampling, if you have a column with a large number of rows and a disproportionate distribution of values, the inferred literals may not include all possible values. You can increase `sample_middle_rows`, `sample_head_rows`, or `sample_tail_rows` if you want to sample more rows.

## Future Features

- [ ] Support for typed containers (e.g., `List[int]`, `Dict[str, int]`)
- [ ] Support for nested dataclasses
- [ ] More advanced configuration options

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
