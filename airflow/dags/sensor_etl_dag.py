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

def run_snowflake_transformations(**context):
    import os
    import logging
    from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
    
    snowflake_enabled = os.getenv("SNOWFLAKE_ENABLED", "false").lower() == "true"
    
    if snowflake_enabled:
        logging.info("Executing Snowflake transformation queries...")
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        
        queries = [
            # Ensure staging and analytics tables are created if not exists
            """
            CREATE TABLE IF NOT EXISTS SMART_FACTORY_DWH.STAGING.SENSOR_DATA_STG (
                ID BIGINT,
                DEVICE_ID VARCHAR(50),
                TIMESTAMP TIMESTAMP,
                TEMPERATURE DECIMAL(8,3),
                HUMIDITY DECIMAL(8,3),
                PRESSURE DECIMAL(8,3),
                VIBRATION DECIMAL(8,4),
                VOLTAGE DECIMAL(8,3),
                CURRENT_AMPS DECIMAL(8,3)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS SMART_FACTORY_DWH.STAGING.DEVICE_MASTER_STG (
                DEVICE_ID VARCHAR(50),
                DEVICE_NAME VARCHAR(100),
                DEVICE_TYPE VARCHAR(50),
                LOCATION VARCHAR(100),
                INSTALL_DATE DATE,
                STATUS VARCHAR(20),
                UPDATED_AT TIMESTAMP
            )
            """,
            """
            MERGE INTO SMART_FACTORY_DWH.ANALYTICS.DIM_DEVICE T
            USING SMART_FACTORY_DWH.STAGING.DEVICE_MASTER_STG S
            ON T.DEVICE_ID = S.DEVICE_ID AND T.IS_CURRENT = TRUE
            WHEN MATCHED AND (T.STATUS != S.STATUS OR T.LOCATION != S.LOCATION) THEN
                UPDATE SET 
                    T.IS_CURRENT = FALSE, 
                    T.EXPIRY_DATE = CURRENT_TIMESTAMP(),
                    T.UPDATED_AT = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (DEVICE_ID, DEVICE_NAME, DEVICE_TYPE, LOCATION, INSTALL_DATE, STATUS, EFFECTIVE_DATE)
                VALUES (S.DEVICE_ID, S.DEVICE_NAME, S.DEVICE_TYPE, S.LOCATION, S.INSTALL_DATE, S.STATUS, CURRENT_TIMESTAMP())
            """,
            """
            INSERT INTO SMART_FACTORY_DWH.ANALYTICS.FACT_SENSOR_DATA (
                DEVICE_KEY, DATE_KEY, READING_TIMESTAMP, TEMPERATURE, HUMIDITY, 
                PRESSURE, VIBRATION, VOLTAGE, CURRENT_AMPS, HOUR_OF_DAY, ETL_BATCH_ID
            )
            SELECT 
                D.DEVICE_KEY,
                CAST(TO_CHAR(S.TIMESTAMP, 'YYYYMMDD') AS INT) AS DATE_KEY,
                S.TIMESTAMP,
                S.TEMPERATURE,
                S.HUMIDITY,
                S.PRESSURE,
                S.VIBRATION,
                S.VOLTAGE,
                S.CURRENT_AMPS,
                EXTRACT(HOUR FROM S.TIMESTAMP),
                'BATCH_' || TO_CHAR(CURRENT_TIMESTAMP(), 'YYYYMMDD_HH24MISS')
            FROM SMART_FACTORY_DWH.STAGING.SENSOR_DATA_STG S
            LEFT JOIN SMART_FACTORY_DWH.ANALYTICS.DIM_DEVICE D 
                ON S.DEVICE_ID = D.DEVICE_ID AND D.IS_CURRENT = TRUE
            """,
            "TRUNCATE TABLE SMART_FACTORY_DWH.STAGING.SENSOR_DATA_STG"
        ]
        
        for idx, query in enumerate(queries, 1):
            logging.info(f"Running Snowflake Query #{idx}...")
            hook.run(query)
        logging.info("Snowflake transformations executed successfully.")
    else:
        logging.info("[MOCK MODE] Snowflake connection disabled. Simulated dimensions merge.")

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
    merge_dimensions = PythonOperator(
        task_id='merge_dimensions',
        python_callable=run_snowflake_transformations,
        provide_context=True
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
