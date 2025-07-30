"""
transform_utils.py

Advanced data transformation utilities for scaling, encoding,
dimensionality reduction, feature engineering, and more.

Dependencies: pandas, numpy, sklearn, scipy, category_encoders, typing
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer, OneHotEncoder, LabelEncoder
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.pipeline import Pipeline
from typing import Optional, List, Union, Dict, Any
import category_encoders as ce


# ----------------------------------------
# Scaling Utilities
# ----------------------------------------

def scale_standard(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Apply standard scaling (zero mean, unit variance) to columns."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[cols])
    df_scaled = df.copy()
    df_scaled[cols] = scaled
    return df_scaled


def scale_minmax(df: pd.DataFrame, columns: Optional[List[str]] = None, feature_range: tuple = (0, 1)) -> pd.DataFrame:
    """Apply min-max scaling to columns."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    scaler = MinMaxScaler(feature_range=feature_range)
    scaled = scaler.fit_transform(df[cols])
    df_scaled = df.copy()
    df_scaled[cols] = scaled
    return df_scaled


def scale_robust(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Apply robust scaling (median and IQR) to columns."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    scaler = RobustScaler()
    scaled = scaler.fit_transform(df[cols])
    df_scaled = df.copy()
    df_scaled[cols] = scaled
    return df_scaled


def scale_power_transform(df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = 'yeo-johnson') -> pd.DataFrame:
    """Apply power transformation to columns (Yeo-Johnson or Box-Cox)."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    pt = PowerTransformer(method=method)
    scaled = pt.fit_transform(df[cols])
    df_scaled = df.copy()
    df_scaled[cols] = scaled
    return df_scaled


# ----------------------------------------
# Encoding Utilities
# ----------------------------------------

def one_hot_encode(df: pd.DataFrame, columns: Optional[List[str]] = None, drop_first: bool = True) -> pd.DataFrame:
    """Perform one-hot encoding on categorical columns."""
    cols = columns or df.select_dtypes(include=['object', 'category']).columns.tolist()
    df_encoded = pd.get_dummies(df, columns=cols, drop_first=drop_first)
    return df_encoded


def label_encode(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Apply label encoding to categorical columns."""
    from sklearn.preprocessing import LabelEncoder
    df_encoded = df.copy()
    cols = columns or df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in cols:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
    return df_encoded


def target_encode(df: pd.DataFrame, target: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Perform target encoding for categorical variables."""
    df_encoded = df.copy()
    cols = columns or df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in cols:
        means = df_encoded.groupby(col)[target].mean()
        df_encoded[col + '_te'] = df_encoded[col].map(means)
        df_encoded.drop(columns=[col], inplace=True)
    return df_encoded


def binary_encode(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Perform binary encoding for categorical variables using category_encoders."""
    cols = columns or df.select_dtypes(include=['object', 'category']).columns.tolist()
    encoder = ce.BinaryEncoder(cols=cols)
    return encoder.fit_transform(df)


# ----------------------------------------
# Dimensionality Reduction
# ----------------------------------------

def pca_reduce(df: pd.DataFrame, n_components: int = 2, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Apply PCA to reduce dimensionality."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(df[cols])
    df_pca = pd.DataFrame(components, columns=[f'PC{i+1}' for i in range(n_components)], index=df.index)
    return df_pca


def truncated_svd_reduce(df: pd.DataFrame, n_components: int = 2, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Apply Truncated SVD (suitable for sparse data)."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    svd = TruncatedSVD(n_components=n_components)
    components = svd.fit_transform(df[cols])
    df_svd = pd.DataFrame(components, columns=[f'SVD{i+1}' for i in range(n_components)], index=df.index)
    return df_svd


# ----------------------------------------
# Feature Selection
# ----------------------------------------

def select_k_best_classification(df: pd.DataFrame, target: str, k: int = 10) -> pd.DataFrame:
    """Select top k features for classification using ANOVA F-test."""
    X = df.drop(columns=[target])
    y = df[target]
    selector = SelectKBest(score_func=f_classif, k=k)
    X_new = selector.fit_transform(X, y)
    cols = X.columns[selector.get_support()]
    return pd.DataFrame(X_new, columns=cols)


def select_k_best_regression(df: pd.DataFrame, target: str, k: int = 10) -> pd.DataFrame:
    """Select top k features for regression using F-test."""
    X = df.drop(columns=[target])
    y = df[target]
    selector = SelectKBest(score_func=f_regression, k=k)
    X_new = selector.fit_transform(X, y)
    cols = X.columns[selector.get_support()]
    return pd.DataFrame(X_new, columns=cols)


# ----------------------------------------
# Feature Engineering Helpers
# ----------------------------------------

def create_interaction_terms(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Create pairwise interaction terms between specified columns."""
    df_inter = df.copy()
    for i in range(len(columns)):
        for j in range(i+1, len(columns)):
            col1 = columns[i]
            col2 = columns[j]
            new_col = f'{col1}_x_{col2}'
            df_inter[new_col] = df_inter[col1] * df_inter[col2]
    return df_inter


def create_polynomial_features(df: pd.DataFrame, columns: List[str], degree: int = 2) -> pd.DataFrame:
    """Create polynomial features of specified degree for columns."""
    from sklearn.preprocessing import PolynomialFeatures
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    features = poly.fit_transform(df[columns])
    feature_names = poly.get_feature_names_out(columns)
    df_poly = pd.DataFrame(features, columns=feature_names, index=df.index)
    df_out = pd.concat([df, df_poly.drop(columns=columns)], axis=1)
    return df_out


def encode_cyclical(df: pd.DataFrame, column: str, max_val: int) -> pd.DataFrame:
    """Encode cyclical features (e.g., day of week, month) using sine/cosine transforms."""
    df_copy = df.copy()
    df_copy[column + '_sin'] = np.sin(2 * np.pi * df_copy[column] / max_val)
    df_copy[column + '_cos'] = np.cos(2 * np.pi * df_copy[column] / max_val)
    return df_copy


# ----------------------------------------
# Pipeline Helpers
# ----------------------------------------

def build_scaling_pipeline(method: str = 'standard', columns: Optional[List[str]] = None) -> Pipeline:
    """Build sklearn Pipeline with scaler for specified columns."""
    scaler_map = {
        'standard': StandardScaler(),
        'minmax': MinMaxScaler(),
        'robust': RobustScaler(),
        'power': PowerTransformer()
    }
    if method not in scaler_map:
        raise ValueError(f"Unsupported scaling method: {method}")
    scaler = scaler_map[method]

    def selector(X):
        return X[columns] if columns else X.select_dtypes(include=np.number)

    pipeline = Pipeline([
        ('selector', FunctionTransformer(func=selector)),
        ('scaler', scaler)
    ])
    return pipeline


# ----------------------------------------
# Utility Functions
# ----------------------------------------

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Return list of numeric columns."""
    return df.select_dtypes(include=np.number).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Return list of categorical columns."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Drop specified columns."""
    return df.drop(columns=columns)


def rename_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """Rename columns according to mapping dict."""
    return df.rename(columns=mapping)


# ----------------------------------------
# Example Usage Test
# ----------------------------------------

if __name__ == "__main__":
    # Demo with sample DataFrame
    df = pd.DataFrame({
        'age': [25, 32, 47, 51, 62],
        'salary': [50000, 60000, 80000, 90000, 120000],
        'city': ['New York', 'Paris', 'Paris', 'London', 'New York']
    })

    print("Original DataFrame:")
    print(df)

    print("\nScaled (Standard):")
    print(scale_standard(df))

    print("\nOne-Hot Encoded:")
    print(one_hot_encode(df))

    print("\nPCA Reduced:")
    print(pca_reduce(df[['age', 'salary']], n_components=2))
