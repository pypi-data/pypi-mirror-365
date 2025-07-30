"""
bigdata_utils.py

Expanded Big Data utilities with Google Cloud, AWS S3 support,
streaming ingestion, robust error handling, logging, and workflow hooks.

Dependencies:
- google-cloud-storage
- google-cloud-bigquery
- google-cloud-pubsub (optional)
- boto3
- dask[dataframe]
- pyspark
- tenacity (for retries)
- pandas
- logging
- asyncio

Install with:
pip install google-cloud-storage google-cloud-bigquery google-cloud-pubsub boto3 dask pyspark tenacity pandas
"""

import os
import logging
import asyncio
from typing import Optional, List, Union, Dict, Any, Callable
from pathlib import Path

import pandas as pd
import dask.dataframe as dd
from pyspark.sql import SparkSession
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Google Cloud
from google.cloud import storage, bigquery, pubsub_v1
from google.api_core.exceptions import GoogleAPIError

# AWS S3
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Setup logging
logger = logging.getLogger("bigdata_utils")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# ----------------------------------------
# Retry Decorator for Cloud Ops
# ----------------------------------------

def is_transient_error(exc):
    return isinstance(exc, (GoogleAPIError, BotoCoreError, ClientError))

def retry_cloud_op():
    return retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception) & retry_if_exception_type(is_transient_error)
    )


# ----------------------------------------
# Google Cloud Storage (GCS) Client
# ----------------------------------------

class GCSClient:
    def __init__(self, project: Optional[str] = None):
        self.client = storage.Client(project=project)

    @retry_cloud_op()
    def list_blobs(self, bucket_name: str, prefix: str = '') -> List[str]:
        bucket = self.client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        result = [blob.name for blob in blobs]
        logger.info(f"Listed {len(result)} blobs in bucket '{bucket_name}' with prefix '{prefix}'")
        return result

    @retry_cloud_op()
    def upload_file(self, bucket_name: str, source_file_name: str, destination_blob_name: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        logger.info(f"Uploaded file {source_file_name} to gs://{bucket_name}/{destination_blob_name}")

    @retry_cloud_op()
    def download_file(self, bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        logger.info(f"Downloaded gs://{bucket_name}/{source_blob_name} to {destination_file_name}")

    @retry_cloud_op()
    def delete_blob(self, bucket_name: str, blob_name: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
        logger.info(f"Deleted gs://{bucket_name}/{blob_name}")

    # Async versions (using asyncio.to_thread for thread pool)
    async def upload_file_async(self, bucket_name: str, source_file_name: str, destination_blob_name: str):
        await asyncio.to_thread(self.upload_file, bucket_name, source_file_name, destination_blob_name)

    async def download_file_async(self, bucket_name: str, source_blob_name: str, destination_file_name: str):
        await asyncio.to_thread(self.download_file, bucket_name, source_blob_name, destination_file_name)


# ----------------------------------------
# AWS S3 Client (basic)
# ----------------------------------------

class S3Client:
    def __init__(self, aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None):
        self.s3 = boto3.client('s3',
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key,
                               region_name=region_name)

    @retry_cloud_op()
    def upload_file(self, bucket_name: str, source_file_name: str, key: str) -> None:
        self.s3.upload_file(source_file_name, bucket_name, key)
        logger.info(f"Uploaded file {source_file_name} to s3://{bucket_name}/{key}")

    @retry_cloud_op()
    def download_file(self, bucket_name: str, key: str, destination_file_name: str) -> None:
        self.s3.download_file(bucket_name, key, destination_file_name)
        logger.info(f"Downloaded s3://{bucket_name}/{key} to {destination_file_name}")

    @retry_cloud_op()
    def list_objects(self, bucket_name: str, prefix: str = '') -> List[str]:
        paginator = self.s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        keys = []
        for page in page_iterator:
            if 'Contents' in page:
                keys.extend([obj['Key'] for obj in page['Contents']])
        logger.info(f"Listed {len(keys)} objects in bucket '{bucket_name}' with prefix '{prefix}'")
        return keys


# ----------------------------------------
# Google BigQuery Client
# ----------------------------------------

class BigQueryClient:
    def __init__(self, project: Optional[str] = None):
        self.client = bigquery.Client(project=project)

    @retry_cloud_op()
    def run_query(self, query: str) -> pd.DataFrame:
        query_job = self.client.query(query)
        result = query_job.result()
        df = result.to_dataframe()
        logger.info(f"Ran query: {query[:50]}... and got {len(df)} rows")
        return df

    @retry_cloud_op()
    def load_dataframe_to_table(self, dataframe: pd.DataFrame, table_id: str,
                                if_exists: str = 'append', batch_size: int = 5000) -> None:
        # Map if_exists to BigQuery disposition
        write_disposition_map = {
            'append': bigquery.WriteDisposition.WRITE_APPEND,
            'replace': bigquery.WriteDisposition.WRITE_TRUNCATE,
            'fail': bigquery.WriteDisposition.WRITE_EMPTY
        }
        job_config = bigquery.LoadJobConfig(write_disposition=write_disposition_map[if_exists])
        # BigQuery API can chunk uploads, but we do manual batching to limit memory spikes
        for start in range(0, len(dataframe), batch_size):
            batch_df = dataframe.iloc[start:start+batch_size]
            load_job = self.client.load_table_from_dataframe(batch_df, table_id, job_config=job_config)
            load_job.result()
            logger.info(f"Loaded batch {start}-{start+len(batch_df)} rows into {table_id}")

    @retry_cloud_op()
    def export_table_to_gcs(self, table_id: str, destination_uri: str,
                            compression: str = 'NONE') -> None:
        extract_job = self.client.extract_table(
            table_id,
            destination_uri,
            compression=compression
        )
        extract_job.result()
        logger.info(f"Exported {table_id} to {destination_uri} with compression {compression}")


# ----------------------------------------
# Google Pub/Sub (Streaming ingestion hooks)
# ----------------------------------------

class PubSubClient:
    def __init__(self, project: Optional[str] = None):
        self.project = project
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()

    def subscribe(self, subscription_path: str, callback: Callable[[pubsub_v1.subscriber.message.Message], None]):
        future = self.subscriber.subscribe(subscription_path, callback=callback)
        logger.info(f"Subscribed to {subscription_path}")
        return future

    def publish(self, topic_path: str, message: bytes, attributes: Optional[Dict[str, str]] = None):
        future = self.publisher.publish(topic_path, message, **(attributes or {}))
        logger.info(f"Published message to {topic_path}")
        return future


# ----------------------------------------
# Dask Utilities
# ----------------------------------------

def dask_read_csv(path: str, npartitions: Optional[int] = None) -> dd.DataFrame:
    df = dd.read_csv(path)
    if npartitions:
        df = df.repartition(npartitions=npartitions)
    logger.info(f"Loaded CSV at {path} into Dask DataFrame with {df.npartitions} partitions")
    return df

def dask_to_pandas(ddf: dd.DataFrame) -> pd.DataFrame:
    pdf = ddf.compute()
    logger.info(f"Converted Dask DataFrame to Pandas DataFrame with {len(pdf)} rows")
    return pdf

def dask_map_partitions(ddf: dd.DataFrame, func: Callable) -> dd.DataFrame:
    ddf_new = ddf.map_partitions(func)
    logger.info(f"Applied function to each Dask partition")
    return ddf_new


# ----------------------------------------
# PySpark Utilities
# ----------------------------------------

def get_spark_session(app_name: str = "DevDataSpark") -> SparkSession:
    spark = SparkSession.builder.appName(app_name).getOrCreate()
    logger.info(f"SparkSession created with app name {app_name}")
    return spark

def spark_read_csv(spark: SparkSession, path: str, header: bool = True, inferSchema: bool = True):
    df = spark.read.csv(path, header=header, inferSchema=inferSchema)
    logger.info(f"Spark read CSV from {path}")
    return df

def spark_write_parquet(df, path: str, mode: str = 'overwrite'):
    df.write.mode(mode).parquet(path)
    logger.info(f"Spark wrote Parquet to {path} with mode {mode}")


# ----------------------------------------
# Chunked CSV Reading and Processing
# ----------------------------------------

def chunked_read_csv(path: str, chunksize: int = 100_000):
    logger.info(f"Reading CSV {path} in chunks of {chunksize}")
    for chunk in pd.read_csv(path, chunksize=chunksize):
        yield chunk

def batch_process_chunks(path: str, func: Callable[[pd.DataFrame], pd.DataFrame], chunksize: int = 100_000,
                         *args, **kwargs) -> pd.DataFrame:
    results = []
    for chunk in chunked_read_csv(path, chunksize=chunksize):
        processed = func(chunk, *args, **kwargs)
        results.append(processed)
        logger.info(f"Processed chunk with {len(chunk)} rows")
    combined = pd.concat(results, ignore_index=True)
    logger.info(f"Combined processed chunks into DataFrame with {len(combined)} rows")
    return combined


# ----------------------------------------
# Schema Evolution and Validation Helpers
# ----------------------------------------

def validate_schema(df: pd.DataFrame, schema: Dict[str, Any]) -> bool:
    for col, validator in schema.items():
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
        series = df[col]
        if callable(validator):
            if not validator(series):
                raise ValueError(f"Validation failed for column: {col}")
        else:
            if not pd.api.types.is_dtype_equal(series.dtype, validator):
                raise TypeError(f"Expected {col} dtype {validator}, got {series.dtype}")
    logger.info("Schema validation passed")
    return True

def evolve_schema(df: pd.DataFrame, schema: Dict[str, Any]) -> pd.DataFrame:
    # Add missing columns with default values (None)
    for col in schema.keys():
        if col not in df.columns:
            df[col] = None
            logger.info(f"Added missing column {col} with default None")
    return df


# ----------------------------------------
# Integration Hooks (Airflow / Prefect)
# ----------------------------------------

def airflow_task(func):
    """Decorator for Airflow PythonOperator task."""
    def wrapper(*args, **kwargs):
        logger.info(f"Starting Airflow task {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"Completed Airflow task {func.__name__}")
        return result
    return wrapper

def prefect_task(func):
    """Decorator for Prefect task."""
    try:
        from prefect import task
        return task(func)
    except ImportError:
        logger.warning("Prefect not installed; returning original function")
        return func


# ----------------------------------------
# Example / Demo Main
# ----------------------------------------

if __name__ == "__main__":
    import sys

    logger.info("Running bigdata_utils.py demo")

    # Instantiate clients
    gcs_client = GCSClient()
    bq_client = BigQueryClient()
    s3_client = S3Client()

    # Example bucket and table (replace with your own)
    example_bucket = os.getenv('EXAMPLE_BUCKET', 'my-bucket')
    example_table = os.getenv('EXAMPLE_BQ_TABLE', 'my-project.my_dataset.my_table')

    try:
        blobs = gcs_client.list_blobs(example_bucket, prefix='')
        logger.info(f"GCS blobs: {blobs[:5]}")
    except Exception as e:
        logger.error(f"Failed listing GCS blobs: {e}")

    # Run simple BigQuery query (replace with valid SQL)
    try:
        df = bq_client.run_query("SELECT CURRENT_DATE() as today")
        logger.info(f"BigQuery query result: {df}")
    except Exception as e:
        logger.error(f"BigQuery query failed: {e}")

    # Dask example with dummy CSV path
    csv_path = "large_file.csv"
    if Path(csv_path).exists():
        ddf = dask_read_csv(csv_path, npartitions=4)
        print(ddf.head())

    logger.info("Demo complete")
