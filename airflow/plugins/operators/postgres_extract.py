from airflow.models.baseoperator import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.decorators import apply_defaults
import pandas as pd
import logging

class PostgresExtractOperator(BaseOperator):
    """
    Extracts data from PostgreSQL and returns it as a DataFrame in XCom (for small datasets)
    or saves to a staging area (for large datasets).
    For this demo, we'll keep it simple and return the row count, assuming the actual
    data movement might happen via an external stage or a pandas-based intermediate step
    handled by the load operator.
    """
    
    @apply_defaults
    def __init__(self, postgres_conn_id, sql, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.sql = sql
        
    def execute(self, context):
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        logging.info(f"Executing query: {self.sql}")
        
        # In a real production scenario with large data, you would dump to CSV/Parquet 
        # in S3/GCS here, not load entirely into memory.
        df = hook.get_pandas_df(self.sql)
        row_count = len(df)
        
        logging.info(f"Extracted {row_count} rows from PostgreSQL.")
        
        # We'll save the data to a temporary local file to pass between tasks
        # (This avoids XCom size limits for pandas dataframes)
        temp_file = f"/tmp/{self.task_id}_{context['execution_date'].strftime('%Y%m%d%H%M%S')}.csv"
        df.to_csv(temp_file, index=False)
        
        # Push file path and row count to XCom
        return {"file_path": temp_file, "row_count": row_count}
