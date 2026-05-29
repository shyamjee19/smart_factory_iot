from airflow.models.baseoperator import BaseOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.utils.decorators import apply_defaults
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import logging
import os

class SnowflakeLoadOperator(BaseOperator):
    """
    Loads data from a local CSV file (extracted previously) into Snowflake.
    Uses Snowflake's write_pandas utility for efficient bulk loading.
    """
    
    @apply_defaults
    def __init__(self, snowflake_conn_id, table_name, extract_task_id, database, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snowflake_conn_id = snowflake_conn_id
        self.table_name = table_name
        self.extract_task_id = extract_task_id
        self.database = database
        self.schema = schema
        
    def execute(self, context):
        # Retrieve the file path from XCom
        extract_info = context['ti'].xcom_pull(task_ids=self.extract_task_id)
        
        if not extract_info or 'file_path' not in extract_info:
            logging.info("No data extracted. Skipping load.")
            return 0
            
        file_path = extract_info['file_path']
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Extracted file not found: {file_path}")
            
        # Read the CSV back into Pandas
        df = pd.read_csv(file_path)
        row_count = len(df)
        
        if row_count == 0:
            logging.info("Empty dataframe. Skipping Snowflake load.")
            os.remove(file_path)
            return 0
            
        logging.info(f"Preparing to load {row_count} rows to {self.database}.{self.schema}.{self.table_name}")
        
        # Convert column names to uppercase for Snowflake compatibility
        df.columns = [col.upper() for col in df.columns]
        
        hook = SnowflakeHook(snowflake_conn_id=self.snowflake_conn_id)
        
        # NOTE: For local testing without real Snowflake credentials, we can mock this out
        # by checking an environment variable.
        if os.getenv("SNOWFLAKE_ENABLED", "false").lower() == "true":
            conn = hook.get_conn()
            success, nchunks, nrows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name=self.table_name,
                database=self.database,
                schema=self.schema,
                quote_identifiers=False
            )
            logging.info(f"Successfully loaded {nrows} rows into Snowflake.")
        else:
            logging.info("[MOCK MODE] Snowflake connection disabled. Simulated load of {row_count} rows.")
            nrows = row_count
            
        # Cleanup temp file
        try:
            os.remove(file_path)
        except OSError as e:
            logging.warning(f"Failed to remove temp file {file_path}: {e}")
            
        return nrows
