from airflow.models.baseoperator import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException
import logging

class DataQualityCheckOperator(BaseOperator):
    """
    Runs a series of SQL-based data quality checks against a database.
    Expects a list of dictionaries with 'check_sql' and 'expected_result'.
    """
    
    def __init__(self, postgres_conn_id, dq_checks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.dq_checks = dq_checks
        
    def execute(self, context):
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        
        error_count = 0
        failing_tests = []
        
        for i, check in enumerate(self.dq_checks):
            sql = check.get('check_sql')
            expected = check.get('expected_result')
            
            logging.info(f"Running Check {i+1}: {sql}")
            
            try:
                # get_first returns a tuple of the first row
                result = hook.get_first(sql)[0]
                
                if str(result) == str(expected):
                    logging.info(f"Check {i+1} Passed. Expected: {expected}, Got: {result}")
                else:
                    logging.error(f"Check {i+1} Failed. Expected: {expected}, Got: {result}")
                    error_count += 1
                    failing_tests.append({"sql": sql, "expected": expected, "actual": result})
                    
            except Exception as e:
                logging.error(f"Error running check {i+1}: {e}")
                error_count += 1
                failing_tests.append({"sql": sql, "error": str(e)})
                
        if error_count > 0:
            error_msg = f"{error_count} Data Quality Check(s) failed: {failing_tests}"
            raise AirflowException(error_msg)
            
        logging.info("All Data Quality Checks Passed!")
        return "Passed"
