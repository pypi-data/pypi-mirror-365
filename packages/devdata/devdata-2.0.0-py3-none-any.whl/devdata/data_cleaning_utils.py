"""
data_cleaning_utils.py

Comprehensive data cleaning and transformation utilities with support for
Pandas, Dask, and Spark DataFrames.

Dependencies:
- pandas
- dask[dataframe]
- pyspark

Install with:
pip install pandas dask pyspark
"""

import pandas as pd
import dask.dataframe as dd
import numpy as np
from typing import Optional, Union, List, Dict, Callable

try:
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql.functions import col, when, isnan, lit, to_date, to_timestamp, udf
    from pyspark.sql.types import StringType
except ImportError:
    SparkDataFrame = None

# ---------------------------
# DataFrame Type Checks
# ---------------------------

def is_spark_df(df) -> bool:
    return SparkDataFrame is not None and isinstance(df, SparkDataFrame)

def is_dask_df(df) -> bool:
    return isinstance(df, dd.DataFrame)

def is_pandas_df(df) -> bool:
    return isinstance(df, pd.DataFrame)

def to_pandas(df) -> pd.DataFrame:
    if is_pandas_df(df):
        return df
    elif is_dask_df(df):
        return df.compute()
    elif is_spark_df(df):
        return df.toPandas()
    else:
        raise TypeError("Unsupported DataFrame type")

# ---------------------------
# Missing Data Handling
# ---------------------------

def fill_missing(df, value: Optional[Union[int, float, str, dict]] = 0, columns: Optional[List[str]] = None):
    """
    Fill missing values in specified columns or entire DataFrame.
    value can be scalar or dict mapping column->fill value.
    """
    if is_spark_df(df):
        # Spark fillna supports dict or scalar
        if columns:
            subset = columns
        else:
            subset = df.columns
        return df.fillna(value, subset=subset)
    else:
        if columns:
            if isinstance(value, dict):
                fill_vals = value
            else:
                fill_vals = {col: value for col in columns}
            return df.fillna(fill_vals)
        else:
            return df.fillna(value)

def drop_missing(df, columns: Optional[List[str]] = None, how: str = 'any'):
    """
    Drop rows with missing values.
    how: 'any' or 'all'
    """
    if is_spark_df(df):
        if columns:
            return df.dropna(how=how, subset=columns)
        else:
            return df.dropna(how=how)
    else:
        return df.dropna(subset=columns, how=how)

def interpolate_missing(df, columns: Optional[List[str]] = None, method: str = 'linear'):
    """
    Interpolate missing numeric values (only for Pandas/Dask).
    """
    if is_pandas_df(df):
        if columns:
            for col in columns:
                df[col] = df[col].interpolate(method=method)
        else:
            df.interpolate(method=method, inplace=True)
        return df
    elif is_dask_df(df):
        pdf = df.compute()
        pdf = interpolate_missing(pdf, columns, method)
        return dd.from_pandas(pdf, npartitions=df.npartitions)
    else:
        raise NotImplementedError("Interpolation not supported for Spark DataFrame")

# ---------------------------
# Data Type Conversion and Normalization
# ---------------------------

def convert_dtype(df, columns: Dict[str, str]):
    """
    Convert columns to specified data types.
    columns: dict of column name -> dtype string (e.g. 'float', 'int', 'category', 'datetime64[ns]')
    """
    if is_spark_df(df):
        for col_name, dtype in columns.items():
            spark_type = _spark_dtype_from_str(dtype)
            df = df.withColumn(col_name, col(col_name).cast(spark_type))
        return df
    else:
        return df.astype(columns)

def _spark_dtype_from_str(dtype_str: str):
    from pyspark.sql.types import (
        StringType, IntegerType, FloatType, DoubleType, BooleanType, DateType, TimestampType
    )
    dtype_map = {
        'string': StringType(),
        'int': IntegerType(),
        'integer': IntegerType(),
        'float': FloatType(),
        'double': DoubleType(),
        'bool': BooleanType(),
        'boolean': BooleanType(),
        'date': DateType(),
        'datetime': TimestampType(),
        'timestamp': TimestampType(),
    }
    dt = dtype_map.get(dtype_str.lower())
    if dt is None:
        raise ValueError(f"Unsupported Spark dtype string: {dtype_str}")
    return dt

def normalize_numeric(df, columns: Optional[List[str]] = None, method: str = 'minmax'):
    """
    Normalize numeric columns.
    method: 'minmax' or 'zscore'
    """
    pdf = to_pandas(df)
    if columns is None:
        columns = pdf.select_dtypes(include=[np.number]).columns.tolist()

    for col in columns:
        if method == 'minmax':
            min_val = pdf[col].min()
            max_val = pdf[col].max()
            pdf[col] = (pdf[col] - min_val) / (max_val - min_val) if max_val != min_val else 0.0
        elif method == 'zscore':
            mean = pdf[col].mean()
            std = pdf[col].std()
            pdf[col] = (pdf[col] - mean) / std if std != 0 else 0.0
        else:
            raise ValueError(f"Unsupported normalization method: {method}")

    if is_pandas_df(df):
        return pdf
    elif is_dask_df(df):
        return dd.from_pandas(pdf, npartitions=df.npartitions)
    else:
        # For Spark, convert pandas back
        spark = df.sql_ctx.sparkSession
        return spark.createDataFrame(pdf)

# ---------------------------
# Outlier Detection and Removal
# ---------------------------

def detect_outliers_iqr(df, columns: Optional[List[str]] = None, multiplier: float = 1.5) -> Dict[str, pd.Series]:
    """
    Detect outliers using IQR method in Pandas DataFrame.
    Returns dictionary col -> boolean Series marking outliers.
    """
    pdf = to_pandas(df)
    if columns is None:
        columns = pdf.select_dtypes(include=[np.number]).columns.tolist()

    outliers = {}
    for col in columns:
        q1 = pdf[col].quantile(0.25)
        q3 = pdf[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        mask = (pdf[col] < lower_bound) | (pdf[col] > upper_bound)
        outliers[col] = mask
    return outliers

def remove_outliers_iqr(df, columns: Optional[List[str]] = None, multiplier: float = 1.5):
    """
    Remove outliers detected by IQR method.
    """
    outliers = detect_outliers_iqr(df, columns, multiplier)
    pdf = to_pandas(df)
    combined_mask = pd.Series(False, index=pdf.index)
    for mask in outliers.values():
        combined_mask = combined_mask | mask
    filtered = pdf[~combined_mask]
    if is_pandas_df(df):
        return filtered
    elif is_dask_df(df):
        return dd.from_pandas(filtered, npartitions=df.npartitions)
    else:
        spark = df.sql_ctx.sparkSession
        return spark.createDataFrame(filtered)

# ---------------------------
# String/Text Cleaning Utilities
# ---------------------------

def clean_string_column(df, column: str, lower: bool = True, strip: bool = True,
                        remove_punctuation: bool = True, fillna: Optional[str] = None):
    """
    Clean text data in a column.
    """
    if is_spark_df(df):
        if fillna is not None:
            df = df.fillna({column: fillna})
        if lower:
            df = df.withColumn(column, col(column).cast("string"))
            df = df.withColumn(column,  when(col(column).isNotNull(), col(column)).otherwise(lit('')))
            df = df.withColumn(column, col(column).lower())
        if strip:
            strip_udf = udf(lambda x: x.strip() if x else x, StringType())
            df = df.withColumn(column, strip_udf(col(column)))
        if remove_punctuation:
            import re
            def remove_punc(text):
                if text:
                    return re.sub(r'[^\w\s]', '', text)
                return text
            remove_punc_udf = udf(remove_punc, StringType())
            df = df.withColumn(column, remove_punc_udf(col(column)))
        return df
    else:
        if fillna is not None:
            df[column] = df[column].fillna(fillna)
        if lower:
            df[column] = df[column].str.lower()
        if strip:
            df[column] = df[column].str.strip()
        if remove_punctuation:
            df[column] = df[column].str.replace(r'[^\w\s]', '', regex=True)
        return df

# ---------------------------
# Date/Time Parsing and Feature Extraction
# ---------------------------

def parse_dates(df, columns: List[str], format: Optional[str] = None):
    """
    Parse date/time columns.
    """
    if is_spark_df(df):
        for col_name in columns:
            if format:
                df = df.withColumn(col_name, to_date(col(col_name), format))
            else:
                df = df.withColumn(col_name, to_timestamp(col(col_name)))
        return df
    else:
        for col_name in columns:
            df[col_name] = pd.to_datetime(df[col_name], format=format, errors='coerce')
        return df

def extract_date_features(df, date_col: str, prefix: Optional[str] = None):
    """
    Extract year, month, day, weekday features from a date/datetime column.
    """
    if prefix is None:
        prefix = date_col
    if is_spark_df(df):
        df = df.withColumn(f"{prefix}_year", col(date_col).cast("date").substr(1,4).cast("int"))
        df = df.withColumn(f"{prefix}_month", col(date_col).cast("date").substr(6,2).cast("int"))
        df = df.withColumn(f"{prefix}_day", col(date_col).cast("date").substr(9,2).cast("int"))
        from pyspark.sql.functions import dayofweek
        df = df.withColumn(f"{prefix}_weekday", dayofweek(col(date_col)))
        return df
    else:
        df[f"{prefix}_year"] = df[date_col].dt.year
        df[f"{prefix}_month"] = df[date_col].dt.month
        df[f"{prefix}_day"] = df[date_col].dt.day
        df[f"{prefix}_weekday"] = df[date_col].dt.weekday
        return df

# ---------------------------
# Encoding Categorical Variables
# ---------------------------

def one_hot_encode(df, columns: Optional[List[str]] = None, drop_first: bool = True):
    """
    One-hot encode categorical variables.
    """
    if is_spark_df(df):
        from pyspark.ml.feature import OneHotEncoder, StringIndexer
        from pyspark.ml import Pipeline

        if columns is None:
            columns = [f.name for f in df.schema.fields if f.dataType == StringType()]

        stages = []
        for col_name in columns:
            indexer = StringIndexer(inputCol=col_name, outputCol=col_name + "_idx", handleInvalid='keep')
            encoder = OneHotEncoder(inputCols=[col_name + "_idx"], outputCols=[col_name + "_oh"], dropLast=drop_first)
            stages += [indexer, encoder]

        pipeline = Pipeline(stages=stages)
        model = pipeline.fit(df)
        df = model.transform(df)
        return df

    else:
        pdf = to_pandas(df)
        if columns is None:
            columns = pdf.select_dtypes(include=['object', 'category']).columns.tolist()
        pdf = pd.get_dummies(pdf, columns=columns, drop_first=drop_first)
        if is_pandas_df(df):
            return pdf
        elif is_dask_df(df):
            return dd.from_pandas(pdf, npartitions=df.npartitions)
        else:
            raise TypeError("Unsupported DataFrame type for one_hot_encode")

def label_encode(df, columns: List[str]):
    """
    Label encode categorical variables.
    """
    from sklearn.preprocessing import LabelEncoder

    if is_spark_df(df):
        # Spark label encoding is StringIndexer only
        from pyspark.ml.feature import StringIndexer
        for col_name in columns:
            indexer = StringIndexer(inputCol=col_name, outputCol=col_name + "_idx", handleInvalid='keep')
            model = indexer.fit(df)
            df = model.transform(df)
        return df

    else:
        pdf = to_pandas(df)
        for col in columns:
            le = LabelEncoder()
            pdf[col] = le.fit_transform(pdf[col].astype(str))
        if is_pandas_df(df):
            return pdf
        elif is_dask_df(df):
            return dd.from_pandas(pdf, npartitions=df.npartitions)
        else:
            raise TypeError("Unsupported DataFrame type for label_encode")

# ---------------------------
# Example Usage / Tests
# ---------------------------

if __name__ == "__main__":
    print("Running data_cleaning_utils.py demo...")

    data = {
        'A': [1, 2, None, 4, 1000],
        'B': ['foo', 'bar', None, 'baz', 'foo'],
        'C': ['2021-01-01', '2021-01-02', 'not a date', None, '2021-01-05'],
        'D': [10, 15, 14, 13, 100]
    }
    df = pd.DataFrame(data)

    print("Original DataFrame:")
    print(df)

    df = fill_missing(df, value={'A': 0, 'B': 'missing'})
    print("\nAfter fill_missing:")
    print(df)

    df = drop_missing(df, columns=['C'])
    print("\nAfter drop_missing on column C:")
    print(df)

    df = parse_dates(df, ['C'])
    print("\nAfter parse_dates:")
    print(df)

    df = extract_date_features(df, 'C')
    print("\nAfter extract_date_features:")
    print(df)

    outliers = detect_outliers_iqr(df, columns=['A', 'D'])
    print("\nOutliers detected (IQR method):")
    for col, mask in outliers.items():
        print(f"{col}: {mask.tolist()}")

    df = remove_outliers_iqr(df, columns=['A', 'D'])
    print("\nAfter remove_outliers_iqr:")
    print(df)

    df = normalize_numeric(df, method='zscore')
    print("\nAfter normalize_numeric (zscore):")
    print(df)

    df = clean_string_column(df, 'B')
    print("\nAfter clean_string_column on B:")
    print(df)

    df = one_hot_encode(df, columns=['B'])
    print("\nAfter one_hot_encode on B:")
    print(df)

    print("Demo complete.")
