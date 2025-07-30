"""
data_viz_utils.py

Comprehensive data visualization utilities integrating matplotlib, seaborn, and plotly.
Supports Pandas, Dask, and Spark DataFrames, large datasets, theming, export, and dashboards.

Dependencies:
- matplotlib
- seaborn
- plotly
- pandas
- dask[dataframe]
- pyspark

Install with:
pip install matplotlib seaborn plotly pandas dask pyspark
"""

import os
import math
import pandas as pd
import dask.dataframe as dd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Union, List, Dict

try:
    from pyspark.sql import DataFrame as SparkDataFrame
except ImportError:
    SparkDataFrame = None

# ---------------------------
# Utility Functions
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
# Downsampling Large Datasets
# ---------------------------

def downsample_df(df: Union[pd.DataFrame, dd.DataFrame, 'SparkDataFrame'], max_rows: int = 10000) -> pd.DataFrame:
    """
    Downsample large datasets to max_rows by random sampling for visualization.
    """
    pdf = to_pandas(df)
    if len(pdf) > max_rows:
        pdf = pdf.sample(n=max_rows, random_state=42).reset_index(drop=True)
    return pdf

# ---------------------------
# Theming & Styling
# ---------------------------

def set_matplotlib_theme(style: str = "darkgrid") -> None:
    """
    Set seaborn/matplotlib theme.
    """
    sns.set_theme(style=style)

def set_plotly_theme(template: str = "plotly_dark") -> None:
    """
    Set plotly theme globally.
    """
    px.defaults.template = template

# ---------------------------
# Matplotlib/Seaborn Basic Plots
# ---------------------------

def plot_line(df, x: str, y: Union[str, List[str]], hue: Optional[str] = None,
              title: Optional[str] = None, figsize=(10,6), save_path: Optional[str] = None):
    pdf = to_pandas(df)
    plt.figure(figsize=figsize)
    sns.lineplot(data=pdf, x=x, y=y, hue=hue)
    if title:
        plt.title(title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

def plot_bar(df, x: str, y: Union[str, List[str]], hue: Optional[str] = None,
             title: Optional[str] = None, figsize=(10,6), save_path: Optional[str] = None):
    pdf = to_pandas(df)
    plt.figure(figsize=figsize)
    sns.barplot(data=pdf, x=x, y=y, hue=hue)
    if title:
        plt.title(title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

def plot_scatter(df, x: str, y: str, hue: Optional[str] = None,
                 size: Optional[str] = None, title: Optional[str] = None,
                 figsize=(10,6), save_path: Optional[str] = None):
    pdf = to_pandas(df)
    plt.figure(figsize=figsize)
    sns.scatterplot(data=pdf, x=x, y=y, hue=hue, size=size)
    if title:
        plt.title(title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

def plot_heatmap(df, x: str, y: str, values: str,
                 aggfunc='mean', cmap='viridis', figsize=(10,8), save_path: Optional[str] = None):
    pdf = to_pandas(df)
    pivot_table = pd.pivot_table(pdf, index=y, columns=x, values=values, aggfunc=aggfunc)
    plt.figure(figsize=figsize)
    sns.heatmap(pivot_table, cmap=cmap)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

# ---------------------------
# Plotly Interactive Plots
# ---------------------------

def interactive_line(df, x: str, y: Union[str, List[str]], color: Optional[str] = None,
                     title: Optional[str] = None, save_html: Optional[str] = None) -> go.Figure:
    pdf = to_pandas(df)
    fig = px.line(pdf, x=x, y=y, color=color, title=title)
    if save_html:
        fig.write_html(save_html)
    else:
        fig.show()
    return fig

def interactive_bar(df, x: str, y: Union[str, List[str]], color: Optional[str] = None,
                    title: Optional[str] = None, save_html: Optional[str] = None) -> go.Figure:
    pdf = to_pandas(df)
    fig = px.bar(pdf, x=x, y=y, color=color, title=title)
    if save_html:
        fig.write_html(save_html)
    else:
        fig.show()
    return fig

def interactive_scatter(df, x: str, y: str, color: Optional[str] = None,
                        size: Optional[str] = None, title: Optional[str] = None,
                        save_html: Optional[str] = None) -> go.Figure:
    pdf = to_pandas(df)
    fig = px.scatter(pdf, x=x, y=y, color=color, size=size, title=title)
    if save_html:
        fig.write_html(save_html)
    else:
        fig.show()
    return fig

# ---------------------------
# EDA Summary Plot
# ---------------------------

def eda_summary(df, max_cat_unique: int = 20, figsize=(15, 10)):
    """
    Produce a multi-plot exploratory data analysis summary:
    - Histograms for numeric
    - Bar plots for categoricals (limited unique)
    """
    pdf = to_pandas(df)
    numeric_cols = pdf.select_dtypes(include='number').columns
    cat_cols = [c for c in pdf.select_dtypes(include='object').columns if pdf[c].nunique() <= max_cat_unique]

    n_plots = len(numeric_cols) + len(cat_cols)
    n_cols = 3
    n_rows = math.ceil(n_plots / n_cols)
    fig, axs = plt.subplots(n_rows, n_cols, figsize=figsize)
    axs = axs.flatten()

    for i, col in enumerate(numeric_cols):
        sns.histplot(pdf[col], kde=True, ax=axs[i])
        axs[i].set_title(f"Histogram of {col}")

    for j, col in enumerate(cat_cols):
        sns.countplot(y=pdf[col], order=pdf[col].value_counts().index, ax=axs[len(numeric_cols) + j])
        axs[len(numeric_cols) + j].set_title(f"Countplot of {col}")

    for k in range(n_plots, len(axs)):
        fig.delaxes(axs[k])

    plt.tight_layout()
    plt.show()

# ---------------------------
# Dashboard Layout Helper
# ---------------------------

def multi_plot_dashboard(plot_funcs: List[callable], data, layout: Optional[Dict] = None,
                         figsize=(15, 10), save_path: Optional[str] = None):
    """
    Plot multiple plots in a grid dashboard.
    plot_funcs: list of functions accepting 'data' as first arg and plotting on current axes.
    layout: dict with 'rows' and 'cols', defaults to square layout.
    """
    n = len(plot_funcs)
    if layout is None:
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
    else:
        rows = layout.get('rows', 1)
        cols = layout.get('cols', n)

    fig, axs = plt.subplots(rows, cols, figsize=figsize)
    axs = axs.flatten() if n > 1 else [axs]

    for i, plot_func in enumerate(plot_funcs):
        plt.sca(axs[i])
        plot_func(data)
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

# ---------------------------
# Export Helpers
# ---------------------------

def save_figure(fig, path: str):
    """
    Save matplotlib or plotly figure to file.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']:
        fig.savefig(path)
    elif ext == '.html':
        fig.write_html(path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

# ---------------------------
# Example usage / tests
# ---------------------------

if __name__ == "__main__":
    # Set theme
    set_matplotlib_theme()
    set_plotly_theme()

    # Create sample data
    df = pd.DataFrame({
        'x': range(100),
        'y': [v**0.5 for v in range(100)],
        'category': ['A' if v % 2 == 0 else 'B' for v in range(100)],
        'size': [v/10 for v in range(100)]
    })

    print("Plotting Matplotlib line plot...")
    plot_line(df, x='x', y='y', hue='category', title='Line Plot Example')

    print("Plotting Plotly interactive scatter...")
    interactive_scatter(df, x='x', y='y', color='category', size='size', title='Interactive Scatter')

    print("Showing EDA summary...")
    eda_summary(df)

    print("Dashboard multiple plots...")
    def plot1(data): sns.lineplot(data=data, x='x', y='y')
    def plot2(data): sns.barplot(data=data, x='category', y='y')
    multi_plot_dashboard([plot1, plot2], df)
