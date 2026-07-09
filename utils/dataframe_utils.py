from typing import Any, Literal

import numpy as np
from pandas import DataFrame, Series
from pandas.api.extensions import register_dataframe_accessor

@register_dataframe_accessor("utils")
class MyUtilsAccessor:
    def __init__(self, pandas_obj):
        self._df : DataFrame = pandas_obj

    def get_ids_columns(self, pattern: str = r'^id$|_id$') -> list[str]:
        return self._df.columns[
                self._df.columns.str.contains(pattern, regex=True)
            ].tolist()


def get_ids_columns(df: DataFrame, pattern: str = r'^id$|_id$') -> list[str]:
    """
    Return the name of column that are ids column or contain 'id' not as a part of a word.
    """
    return df.columns[
        df.columns.str.contains(pattern, regex=True)
    ].tolist()
    
def get_columns_by_dtype(
    df: DataFrame,
    dtype: str | type | np.dtype,
) -> list[str]:
    """Return column names matching a given dtype.
 
    Accepts pandas' broad dtype aliases as well as concrete numpy/pandas
    dtype objects, so both of these work:
        get_columns_by_dtype(df, "number")     # any numeric column
        get_columns_by_dtype(df, "object")     # any object/string column
        get_columns_by_dtype(df, np.float64)   # a specific numpy dtype
        get_columns_by_dtype(df, "datetime64[ns]")
 
    Args:
        df: The DataFrame to inspect.
        dtype: A dtype string (including pandas-only aliases like
            'number' or 'category'), a Python type, or a numpy/pandas
            dtype object.
 
    Returns:
        List of column names matching that dtype.
    """
    return df.select_dtypes(include=[dtype]).columns.tolist()  # pyright: ignore[reportCallIssue, reportArgumentType]
 
 
# --------------------------------------------------------------------------- #
# Missing values
# --------------------------------------------------------------------------- #
 
def missing_value_report(df: DataFrame) -> DataFrame:
    """Summarize missing values per column.
 
    Args:
        df: The DataFrame to inspect.
 
    Returns:
        A DataFrame indexed by column name with two columns:
            'missing_count' - number of null values
            'missing_pct'   - percentage of rows that are null (0-100)
        Sorted descending by missing_count. Columns with zero missing
        values are still included.
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100
    report = DataFrame({
        "missing_count": missing_count,
        "missing_pct": missing_pct.round(2),
    })
    return report.sort_values("missing_count", ascending=False)
 
 
def drop_high_missing_columns(df: DataFrame, threshold: float = 0.5) -> DataFrame:
    """Drop columns whose missing-value ratio exceeds a threshold.
 
    Args:
        df: The DataFrame to clean.
        threshold: Fraction of missing values (0-1) above which a
            column is dropped. Defaults to 0.5 (i.e. drop columns
            that are more than 50% empty).
 
    Returns:
        A new DataFrame with the offending columns removed.
        The original DataFrame is not modified.
    """
    missing_ratio = df.isnull().mean()
    cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()
    return df.drop(columns=cols_to_drop)
 
 
def fill_missing(
    df: DataFrame,
    columns: list[str],
    strategy: str = "median",
    constant: Any = None,
) -> DataFrame:
    """Fill missing values in specified columns using a chosen strategy.
 
    Args:
        df: The DataFrame to clean.
        columns: List of column names to fill.
        strategy: One of 'median', 'mean', 'mode', or 'constant'.
            'median'/'mean' only make sense for numeric columns.
            'mode' uses the most frequent value (works for any dtype).
            'constant' fills every missing value with `constant`.
        constant: The value to use when strategy='constant'. Ignored
            for other strategies.
 
    Returns:
        A new DataFrame with missing values filled in the given columns.
        The original DataFrame is not modified.
 
    Raises:
        ValueError: If strategy is not one of the supported options.
    """
    df = df.copy()
    for col in columns:
        if strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "mode":
            df[col] = df[col].fillna(df[col].mode().iloc[0])
        elif strategy == "constant":
            df[col] = df[col].fillna(constant)
        else:
            raise ValueError(
                f"Unknown strategy '{strategy}'. "
                "Expected one of: 'median', 'mean', 'mode', 'constant'."
            )
    return df
 
 
# --------------------------------------------------------------------------- #
# Duplicates
# --------------------------------------------------------------------------- #
 
def duplicate_report(df: DataFrame, subset: list[str] | None = None) -> dict[str, int]:
    """Count exact and subset-based duplicate rows.
 
    Args:
        df: The DataFrame to inspect.
        subset: Optional list of columns to check duplicates on
            (e.g. a supposed primary key like ['order_id']).
            If None, checks full-row duplicates.
 
    Returns:
        A dict with:
            'total_rows'      - row count of df
            'duplicate_rows'  - number of duplicate rows found
            'unique_rows'     - total_rows - duplicate_rows
    """
    dup_count = int(df.duplicated(subset=subset).sum())
    return {
        "total_rows": len(df),
        "duplicate_rows": dup_count,
        "unique_rows": len(df) - dup_count,
    }
 
 
def drop_duplicate_rows(
    df: DataFrame,
    subset: list[str] | None = None,
    keep: Literal["first", "last", False] = "first",
) -> DataFrame:
    """Remove duplicate rows.
 
    Args:
        df: The DataFrame to clean.
        subset: Optional list of columns to consider when identifying
            duplicates (e.g. a primary-key column). If None, compares
            full rows.
        keep: Which duplicate to keep: 'first', 'last', or False
            (drop all occurrences of duplicated rows).
 
    Returns:
        A new DataFrame with duplicates removed and the index reset.
        The original DataFrame is not modified.
    """
    return df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
 
def normalize_text_columns(
    df: DataFrame,
    columns: list[str],
    lower: bool = True,
    strip: bool = True,
) -> DataFrame:
    """Standardize text columns (case + whitespace).
 
    Useful for categorical columns like city/state names that may have
    inconsistent capitalization or stray whitespace (e.g. 'Sao Paulo'
    vs ' sao paulo ').
 
    Args:
        df: The DataFrame to clean.
        columns: List of text column names to normalize.
        lower: If True, lowercase all values.
        strip: If True, strip leading/trailing whitespace.
 
    Returns:
        A new DataFrame with normalized text columns.
        The original DataFrame is not modified.
    """
    df = df.copy()
    for col in columns:
        series = df[col].astype("string")
        if strip:
            series = series.str.strip()
        if lower:
            series = series.str.lower()
        df[col] = series
    return df
 
 
def iqr_outlier_bounds(series: Series, k: float = 1.5) -> tuple[float, float]:
    """Compute lower/upper outlier bounds using the IQR method.
 
    Args:
        series: A numeric pandas Series.
        k: Multiplier for the IQR (1.5 is the common default,
            3.0 is used for 'extreme' outliers).
 
    Returns:
        A (lower_bound, upper_bound) tuple. Values outside this range
        are considered outliers.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return (q1 - k * iqr, q3 + k * iqr)
 
 
def flag_outliers(df: DataFrame, column: str, k: float = 1.5) -> Series:
    """Return a boolean mask flagging IQR-based outliers in a column.
 
    Args:
        df: The DataFrame to inspect.
        column: Numeric column name to check for outliers.
        k: IQR multiplier, see `iqr_outlier_bounds`.
 
    Returns:
        A boolean Series aligned with df's index; True where the value
        falls outside the IQR bounds.
    """
    lower, upper = iqr_outlier_bounds(df[column], k=k)
    return (df[column] < lower) | (df[column] > upper)
 
 
def cap_outliers(df: DataFrame, column: str, k: float = 1.5) -> DataFrame:
    """Clip outlier values in a column to the IQR bounds (winsorizing).
 
    Args:
        df: The DataFrame to clean.
        column: Numeric column name to cap.
        k: IQR multiplier, see `iqr_outlier_bounds`.
 
    Returns:
        A new DataFrame with the column's outliers clipped to the
        computed lower/upper bounds. The original DataFrame is not
        modified.
    """
    df = df.copy()
    lower, upper = iqr_outlier_bounds(df[column], k=k)
    df[column] = df[column].clip(lower=lower, upper=upper)
    return df
 
 
def quick_summary(df: DataFrame) -> None:
    """Print a fast overview of a DataFrame's shape and quality.
 
    Prints row/column counts, dtype breakdown, missing-value report,
    and duplicate-row count. Intended for quick EDA in a notebook cell,
    not for programmatic use (returns None).
 
    Args:
        df: The DataFrame to summarize.
    """
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n")
 
    print("Dtypes:")
    print(df.dtypes.value_counts().to_string())
    print()
 
    print("Missing values (top 10):")
    print(missing_value_report(df).head(10).to_string())
    print()
 
    dups = duplicate_report(df)
    print(f"Duplicate rows: {dups['duplicate_rows']} / {dups['total_rows']}")
 