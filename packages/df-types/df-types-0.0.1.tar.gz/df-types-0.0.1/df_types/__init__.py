from dataclasses import dataclass, field

import pandas as pd

from df_types._infer_types import infer_types
from df_types._codegen import write_types
from df_types._util import normalize_columns

from df_types._version import __version__

from df_types.config import DFTypesConfig


@dataclass
class DFTypes:
    df: pd.DataFrame
    config: DFTypesConfig = field(default_factory=DFTypesConfig)

    def __post_init__(self):
        self.df = _sample_df(self.df, self.config)

    def write_types(self) -> None:
        col_to_attr_names = {
            col: name
            for col, name in zip(
                self.df.columns, normalize_columns(self.df.columns.tolist())
            )
            if col != name
        }
        types = {col: infer_types(self.df[col], self.config) for col in self.df.columns}

        write_types(col_to_attr_names, types, self.config)


def _sample_df(df: pd.DataFrame, config: DFTypesConfig) -> pd.DataFrame:
    """
    Returns a sample of the DataFrame
    """

    head_rows = config.sample_head_rows
    tail_rows = config.sample_tail_rows
    middle_rows = config.sample_middle_rows

    if len(df.index) <= head_rows + middle_rows + tail_rows:
        return df

    head_sample = df.head(head_rows)
    middle_sample = df.iloc[head_rows:-tail_rows].sample(middle_rows, random_state=config.random_seed)
    tail_sample = df.tail(tail_rows)

    return pd.concat([head_sample, middle_sample, tail_sample])
