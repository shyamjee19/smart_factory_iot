from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from operators.postgres_extract import PostgresExtractOperator
from operators.snowflake_load import SnowflakeLoadOperator
import logging

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'sla': timedelta(minutes=30)
}

def transform_data(**context):
    """
    Mock transformation step. In a real scenario, this would use Pandas/Spark
    to transform the data extracted from Postgres before loading to Snowflake.
    """
    extract_info = context['ti'].xcom_pull(task_ids='extract_from_postgres')
    
    if not extract_info:
        logging.info("No data to transform.")
        return
        
    file_path = extract_info['file_path']
    row_count = extract_info['row_count']
    
    logging.info(f"Transforming {row_count} rows from {file_path}")
    # Read CSV, apply transformations (e.g., date_key generation, anomaly detection), save back
    # For now, we just pass it along
    return extract_info

with DAG(
    'sensor_data_etl',
    default_args=default_args,
    description='Extract sensor data from Postgres and load to Snowflake',
    schedule_interval='*/15 * * * *',
    catchup=False,
    tags=['smart_factory', 'etl', 'sensor_data'],
) as dag:

    start = DummyOperator(task_id='start')
    
    # 1. Extract from Postgres
    # Query gets data from the last 15 minutes (or since last successful run)
    extract_from_postgres = PostgresExtractOperator(
        task_id='extract_from_postgres',
        postgres_conn_id='postgres_default',
        sql="""
            SELECT id, device_id, timestamp, temperature, humidity, pressure, vibration, voltage, current 
            FROM sensor_data 
            WHERE created_at >= NOW() - INTERVAL '15 minutes'
        """
    )
    
    # 2. Transform Data (Python operator wrapping pandas logic)
    transform_sensor_data = PythonOperator(
        task_id='transform_sensor_data',
        python_callable=transform_data,
        provide_context=True
    )
    
    # 3. Load to Snowflake
    load_to_snowflake = SnowflakeLoadOperator(
        task_id='load_to_snowflake',
        snowflake_conn_id='snowflake_default',
        database='SMART_FACTORY_DWH',
        schema='STAGING',
        table_name='SENSOR_DATA_STG',
        extract_task_id='transform_sensor_data'
    )
    
    # Extract Alerts
    extract_alerts = PostgresExtractOperator(
        task_id='extract_alerts',
        postgres_conn_id='postgres_default',
        sql="""
            SELECT id, device_id, alert_type, severity, metric, threshold_value, actual_value, message, created_at 
            FROM alerts 
            WHERE created_at >= NOW() - INTERVAL '15 minutes'
        """
    )
    
    load_alerts_to_snowflake = SnowflakeLoadOperator(
        task_id='load_alerts_to_snowflake',
        snowflake_conn_id='snowflake_default',
        database='SMART_FACTORY_DWH',
        schema='STAGING',
        table_name='ALERTS_STG',
        extract_task_id='extract_alerts'
    )
    
    # 4. Execute Merge/Insert in Snowflake using SnowflakeOperator
    # Note: Using PostgresOperator as a mock here since we might not have Snowflake credentials setup yet
    # In production, this would be a SnowflakeOperator executing the transform_queries.sql
    merge_dimensions = PostgresOperator(
        task_id='merge_dimensions',
        postgres_conn_id='postgres_default',
        sql="SELECT 1;" # Mock SQL
    )
    
    # 5. Audit Logging
    audit_logging = PostgresOperator(
        task_id='audit_logging',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO etl_audit (job_name, dag_id, task_id, start_time, end_time, status)
            VALUES ('sensor_data_etl', '{{ dag.dag_id }}', '{{ task.task_id }}', '{{ ts }}', NOW(), 'SUCCESS')
        """
    )
    
    end = DummyOperator(task_id='end')

    # Define Dependencies
    start >> extract_from_postgres >> transform_sensor_data >> load_to_snowflake >> merge_dimensions
    start >> extract_alerts >> load_alerts_to_snowflake >> merge_dimensions
    merge_dimensions >> audit_logging >> end
