from dataclasses import dataclass
import logging

import pandas as pd

from df_types.config import DFTypesConfig


@dataclass
class InferredTypeNames:
    contains_nans: bool
    type_names: set[tuple[str, str]]


@dataclass
class InferredLiterals:
    literal_reprs: set[str]


def _get_package_name(type_: type) -> tuple[str, str]:
    """
    Hack for getting a maybe-importable module name and type name

    Such names should only be used while type checking, and should not be imported
    at runtime
    """
    return "" if type_.__module__ == "builtins" else type_.__module__, type_.__name__


def _convert_circular(type_name: tuple[str, str]):
    if type_name[0] == "__main__":
        logging.warning(
            "Type %s.%s is not importable. Move it to another module",
            *type_name,
        )
        return ("", "object")
    return type_name


_literal_types = {int, float, str, bytes, bool, type(None)}


def infer_types(
    series: pd.Series, config: DFTypesConfig
) -> InferredTypeNames | InferredLiterals:
    """
    Infers the types of a Series
    """

    contains_nans = series.isna().any().tolist()  # convert np.bool to bool
    series = series.dropna()

    types: set[type] = set(series.map(type).unique().tolist())

    if not config.infer_literals or types > _literal_types:
        # Contains non-literal types or user does not want to infer literals
        # Do not attempt to infer literals
        type_names = {_convert_circular(_get_package_name(type_)) for type_ in types}
        return InferredTypeNames(contains_nans=contains_nans, type_names=type_names)

    value_counts = series.value_counts().sort_values(ascending=False)

    if len(value_counts) < config.max_literal_size:
        reprs = {repr(value) for value in value_counts.index}
        if sum(len(r) for r in reprs) < config.max_literal_repr_len:
            return InferredLiterals(literal_reprs=reprs)

    type_names = {_convert_circular(_get_package_name(type_)) for type_ in types}
    return InferredTypeNames(contains_nans=contains_nans, type_names=type_names)
