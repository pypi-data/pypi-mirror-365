"""
compression_utils.py

Advanced compression and decompression utilities for data files.
Supports gzip, bz2, lzma compression, chunked file handling,
and DataFrame serialization to compressed formats.

Dependencies: pandas, pathlib, gzip, bz2, lzma, shutil, os, typing
"""

import os
import gzip
import bz2
import lzma
import shutil
from pathlib import Path
from typing import Optional, List, Union
import pandas as pd


# ----------------------------------------
# Compression Helpers for Files
# ----------------------------------------

def compress_file_gzip(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Compress file using gzip."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    with open(input_path, 'rb') as f_in, gzip.open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def decompress_file_gzip(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Decompress gzip file."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    with gzip.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def compress_file_bz2(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Compress file using bz2."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    with open(input_path, 'rb') as f_in, bz2.open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def decompress_file_bz2(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Decompress bz2 file."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    with bz2.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def compress_file_lzma(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Compress file using lzma."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    with open(input_path, 'rb') as f_in, lzma.open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def decompress_file_lzma(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Decompress lzma file."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    with lzma.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


# ----------------------------------------
# Compression Helpers for DataFrames
# ----------------------------------------

def to_parquet_compressed(df: pd.DataFrame, path: Union[str, Path], compression: str = 'snappy') -> None:
    """
    Save DataFrame to Parquet with compression.
    Compression options: 'snappy', 'gzip', 'brotli', 'none', etc.
    """
    df.to_parquet(path, compression=compression)


def from_parquet_compressed(path: Union[str, Path]) -> pd.DataFrame:
    """Read Parquet file."""
    return pd.read_parquet(path)


def to_csv_compressed(df: pd.DataFrame, path: Union[str, Path], compression: Optional[str] = 'gzip') -> None:
    """
    Save DataFrame to CSV with optional compression.
    Compression options: 'gzip', 'bz2', 'xz', None.
    """
    df.to_csv(path, index=False, compression=compression)


def from_csv_compressed(path: Union[str, Path], compression: Optional[str] = 'infer') -> pd.DataFrame:
    """
    Read CSV file with optional compression.
    Compression options: 'gzip', 'bz2', 'xz', 'infer', None.
    """
    return pd.read_csv(path, compression=compression)


# ----------------------------------------
# Chunked Compression and Decompression
# ----------------------------------------

def compress_large_file_in_chunks(input_path: Union[str, Path], output_dir: Union[str, Path],
                                  chunk_size_bytes: int = 100_000_000,
                                  compression_method: str = 'gzip') -> List[Path]:
    """
    Compress large file by splitting into chunks and compressing each chunk.
    Returns list of compressed chunk file paths.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_files = []
    compressor_map = {
        'gzip': gzip.open,
        'bz2': bz2.open,
        'lzma': lzma.open,
    }

    if compression_method not in compressor_map:
        raise ValueError(f"Unsupported compression method: {compression_method}")

    open_compressor = compressor_map[compression_method]

    with open(input_path, 'rb') as f_in:
        chunk_index = 0
        while True:
            chunk_data = f_in.read(chunk_size_bytes)
            if not chunk_data:
                break
            chunk_file = output_dir / f'{input_path.stem}_chunk{chunk_index}.{compression_method}'
            with open_compressor(chunk_file, 'wb') as f_out:
                f_out.write(chunk_data)
            chunk_files.append(chunk_file)
            chunk_index += 1

    return chunk_files


def decompress_chunks(chunk_files: List[Union[str, Path]], output_path: Union[str, Path]) -> None:
    """
    Decompress chunked compressed files and merge into single output file.
    Assumes chunk files are named in order.
    """
    output_path = Path(output_path)
    with open(output_path, 'wb') as f_out:
        for chunk_file in chunk_files:
            chunk_file = Path(chunk_file)
            if chunk_file.suffix == '.gz':
                open_func = gzip.open
            elif chunk_file.suffix == '.bz2':
                open_func = bz2.open
            elif chunk_file.suffix == '.xz' or chunk_file.suffix == '.lzma':
                open_func = lzma.open
            else:
                raise ValueError(f"Unsupported chunk file suffix: {chunk_file.suffix}")
            with open_func(chunk_file, 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)


# ----------------------------------------
# Compression Ratio Utilities
# ----------------------------------------

def file_size_bytes(path: Union[str, Path]) -> int:
    """Return file size in bytes."""
    return Path(path).stat().st_size


def compression_ratio(original_path: Union[str, Path], compressed_path: Union[str, Path]) -> float:
    """
    Calculate compression ratio = compressed size / original size.
    Lower is better.
    """
    orig_size = file_size_bytes(original_path)
    comp_size = file_size_bytes(compressed_path)
    return comp_size / orig_size if orig_size != 0 else float('inf')


# ----------------------------------------
# Utility: Clear Directory
# ----------------------------------------

def clear_directory(path: Union[str, Path]) -> None:
    """Remove all files in a directory."""
    path = Path(path)
    for file in path.iterdir():
        if file.is_file():
            file.unlink()


# ----------------------------------------
# Testing and Demo
# ----------------------------------------

if __name__ == '__main__':
    import tempfile
    import pandas as pd

    print("Compression Utils Demo")

    df = pd.DataFrame({
        'col1': range(1000),
        'col2': ['foo', 'bar', 'baz'] * 333 + ['foo']
    })

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, 'test.csv')
        gzip_path = os.path.join(tmpdir, 'test.csv.gz')
        bz2_path = os.path.join(tmpdir, 'test.csv.bz2')
        lzma_path = os.path.join(tmpdir, 'test.csv.xz')

        print("Saving CSV compressed with gzip...")
        to_csv_compressed(df, gzip_path, compression='gzip')
        print(f"Size: {file_size_bytes(gzip_path)} bytes")

        print("Loading CSV compressed with gzip...")
        df_loaded = from_csv_compressed(gzip_path, compression='gzip')
        assert df.equals(df_loaded)
        print("Loaded CSV matches original.")

        print("Compressing file with bz2...")
        compress_file_bz2(csv_path, bz2_path)  # Will error if csv_path missing, so save first:
        df.to_csv(csv_path, index=False)
        compress_file_bz2(csv_path, bz2_path)

        print("Decompressing bz2 file...")
        decompress_file_bz2(bz2_path, os.path.join(tmpdir, 'decompressed.csv'))

        print("Demo complete.")
