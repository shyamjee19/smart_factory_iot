from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from operators.data_quality_check import DataQualityCheckOperator

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email': ['admin@smartfactory.local'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the checks to run against PostgreSQL
# (In production, you'd also run similar checks against Snowflake)
dq_checks = [
    {
        # Ensure we have received data from all 5 devices in the last hour
        'check_sql': "SELECT COUNT(DISTINCT device_id) FROM sensor_data WHERE timestamp >= NOW() - INTERVAL '1 hour'",
        'expected_result': 5
    },
    {
        # Check for physically impossible temperatures
        'check_sql': "SELECT COUNT(*) FROM sensor_data WHERE temperature < -50 OR temperature > 500",
        'expected_result': 0
    },
    {
        # Ensure device_health is being updated
        'check_sql': "SELECT COUNT(*) FROM device_health WHERE updated_at < NOW() - INTERVAL '1 hour'",
        'expected_result': 0
    },
    {
        # Check for orphans in alerts (alerts referencing non-existent devices)
        'check_sql': "SELECT COUNT(*) FROM alerts WHERE device_id NOT IN (SELECT device_id FROM device_master)",
        'expected_result': 0
    }
]

with DAG(
    'data_quality_checks',
    default_args=default_args,
    description='Run Data Quality Checks',
    schedule_interval='@hourly',
    catchup=False,
    tags=['smart_factory', 'dq'],
) as dag:

    start = DummyOperator(task_id='start')
    
    run_postgres_dq_checks = DataQualityCheckOperator(
        task_id='run_postgres_dq_checks',
        postgres_conn_id='postgres_default',
        dq_checks=dq_checks
    )
    
    # Mocking snowflake check task
    # run_snowflake_dq_checks = DataQualityCheckOperator(...)
    
    end = DummyOperator(task_id='end')
    
    start >> run_postgres_dq_checks >> end
