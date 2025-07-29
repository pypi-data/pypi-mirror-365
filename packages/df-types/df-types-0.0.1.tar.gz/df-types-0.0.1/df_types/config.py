from dataclasses import dataclass


@dataclass
class DFTypesConfig:
    sample_head_rows: int = 10
    """
    Number of rows to sample from the head of the DataFrame to infer types
    """

    sample_middle_rows: int = 1_000
    """
    Number of rows to sample from the middle of the DataFrame to infer types
    """

    sample_tail_rows: int = 10
    """
    Number of rows to sample from the tail of the DataFrame to infer types
    """

    max_literal_size: int = 10
    """
    Maximum number of literals to infer
    """

    max_literal_repr_len: int = 100
    """
    Maximum cumulative repr size of all literals
    """

    random_seed: int | None = None
    """
    Random seed to use for sampling
    """

    output_file: str = "typed_df.py"
    """
    Output file path
    """

    class_name: str = "TypedRowData"
    """
    Name for the generated class
    """

    infer_literals: bool = True
    """
    Whether to infer literals
    """

    use_slots: bool = True
    """
    Whether to use __slots__ in the generated class
    """

    nan_to_none: bool = True
    """
    Whether to convert NaN values to None
    """
