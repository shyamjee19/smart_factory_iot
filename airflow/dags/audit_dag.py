"""
Smart Factory IoT Analytics — ETL Audit & Cleanup DAG
======================================================

DAG ID: etl_audit_cleanup
Schedule: @weekly (Sunday midnight UTC)

Tasks:
    1. archive_old_audits   — Move audit records older than 90 days to archive
    2. compute_etl_stats    — Calculate success rate, avg duration, rows/day
    3. sla_monitoring       — Check if any DAG missed its SLA in the past week
    4. cleanup_temp_tables  — Drop staging temp tables older than 7 days

Dependencies:
    archive_old_audits >> compute_etl_stats >> sla_monitoring >> cleanup_temp_tables

Author: Smart Factory Data Engineering Team
Created: 2026-05-29
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SNOWFLAKE_CONN_ID: str = Variable.get("smart_factory_snowflake_conn_id", default_var="smart_factory_snowflake")
SNOWFLAKE_DATABASE: str = Variable.get("snowflake_database", default_var="SMART_FACTORY_DWH")
SNOWFLAKE_WAREHOUSE: str = Variable.get("snowflake_warehouse", default_var="FACTORY_ETL_WH")
ALERT_EMAIL: str = Variable.get("alert_email", default_var="data-engineering@smartfactory.io")

AUDIT_RETENTION_DAYS: int = 90
STAGING_RETENTION_DAYS: int = 7

default_args: Dict[str, Any] = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": [ALERT_EMAIL],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}


def _get_snowflake_cursor(sf_hook: SnowflakeHook):
    """Return a Snowflake cursor with warehouse and database context set."""
    conn = sf_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
    cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    return conn, cursor


# ===================================================================
# TASK 1: Archive old audit records
# ===================================================================

def archive_old_audits(**context: Any) -> str:
    """
    Move audit records older than AUDIT_RETENTION_DAYS to an archive table.
    Creates the archive table if it does not exist.
    """
    sf_hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn, cursor = _get_snowflake_cursor(sf_hook)

    try:
        # Ensure archive table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS AUDIT.ETL_AUDIT_LOG_ARCHIVE
            LIKE AUDIT.ETL_AUDIT_LOG
            """
        )

        # Count records to archive
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM AUDIT.ETL_AUDIT_LOG
            WHERE CREATED_AT < DATEADD('DAY', -%s, CURRENT_TIMESTAMP())
            """,
            (AUDIT_RETENTION_DAYS,),
        )
        archive_count = cursor.fetchone()[0]

        if archive_count == 0:
            logger.info("No audit records older than %d days to archive", AUDIT_RETENTION_DAYS)
            context["ti"].xcom_push(key="archived_count", value=0)
            return "No records to archive"

        # Copy to archive
        cursor.execute(
            """
            INSERT INTO AUDIT.ETL_AUDIT_LOG_ARCHIVE
            SELECT *
            FROM AUDIT.ETL_AUDIT_LOG
            WHERE CREATED_AT < DATEADD('DAY', -%s, CURRENT_TIMESTAMP())
            """,
            (AUDIT_RETENTION_DAYS,),
        )

        # Delete archived records from main table
        cursor.execute(
            """
            DELETE FROM AUDIT.ETL_AUDIT_LOG
            WHERE CREATED_AT < DATEADD('DAY', -%s, CURRENT_TIMESTAMP())
            """,
            (AUDIT_RETENTION_DAYS,),
        )

        conn.commit()
        context["ti"].xcom_push(key="archived_count", value=archive_count)

        logger.info("Archived %d audit records older than %d days", archive_count, AUDIT_RETENTION_DAYS)
        return f"Archived {archive_count} records"

    except Exception as exc:
        logger.error("Archive operation failed: %s", exc)
        raise
    finally:
        cursor.close()
        conn.close()


# ===================================================================
# TASK 2: Compute ETL statistics
# ===================================================================

def compute_etl_stats(**context: Any) -> str:
    """
    Calculate key ETL performance metrics for the past 7 days:
      - Total ETL runs
      - Success rate
      - Average duration
      - Average rows per day
      - Most common failure reasons
    """
    sf_hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn, cursor = _get_snowflake_cursor(sf_hook)

    try:
        # Overall stats for the past week
        cursor.execute(
            """
            SELECT
                COUNT(*)                                                           AS total_runs,
                SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END)               AS success_count,
                SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END)                AS failed_count,
                ROUND(
                    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(*), 0), 2
                )                                                                  AS success_rate_pct,
                ROUND(AVG(DURATION_SECONDS), 2)                                    AS avg_duration_sec,
                ROUND(MAX(DURATION_SECONDS), 2)                                    AS max_duration_sec,
                ROUND(SUM(ROWS_LOADED) / NULLIF(COUNT(DISTINCT DATE(START_TIME)), 0), 0)
                                                                                   AS avg_rows_per_day,
                SUM(ROWS_LOADED)                                                   AS total_rows_loaded,
                SUM(ROWS_REJECTED)                                                 AS total_rows_rejected
            FROM AUDIT.ETL_AUDIT_LOG
            WHERE CREATED_AT >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
            """
        )
        row = cursor.fetchone()

        stats = {
            "period": "last_7_days",
            "total_runs": int(row[0] or 0),
            "success_count": int(row[1] or 0),
            "failed_count": int(row[2] or 0),
            "success_rate_pct": float(row[3] or 0),
            "avg_duration_sec": float(row[4] or 0),
            "max_duration_sec": float(row[5] or 0),
            "avg_rows_per_day": int(row[6] or 0),
            "total_rows_loaded": int(row[7] or 0),
            "total_rows_rejected": int(row[8] or 0),
        }

        # Top failure reasons
        cursor.execute(
            """
            SELECT ERROR_MESSAGE, COUNT(*) AS cnt
            FROM AUDIT.ETL_AUDIT_LOG
            WHERE STATUS = 'FAILED'
              AND CREATED_AT >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
              AND ERROR_MESSAGE IS NOT NULL
            GROUP BY ERROR_MESSAGE
            ORDER BY cnt DESC
            LIMIT 5
            """
        )
        failure_rows = cursor.fetchall()
        stats["top_failures"] = [
            {"error": r[0][:200], "count": int(r[1])} for r in failure_rows
        ]

        # Per-DAG breakdown
        cursor.execute(
            """
            SELECT
                DAG_ID,
                COUNT(*) AS runs,
                SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) AS successes,
                ROUND(AVG(DURATION_SECONDS), 2) AS avg_duration
            FROM AUDIT.ETL_AUDIT_LOG
            WHERE CREATED_AT >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
            GROUP BY DAG_ID
            ORDER BY runs DESC
            """
        )
        dag_rows = cursor.fetchall()
        stats["per_dag"] = [
            {
                "dag_id": r[0],
                "runs": int(r[1]),
                "successes": int(r[2]),
                "avg_duration_sec": float(r[3] or 0),
            }
            for r in dag_rows
        ]

        stats_json = json.dumps(stats, indent=2)
        context["ti"].xcom_push(key="etl_stats", value=stats_json)

        logger.info("ETL stats computed: %s", stats_json)
        return f"Stats: {stats['total_runs']} runs, {stats['success_rate_pct']}% success rate"

    except Exception as exc:
        logger.error("ETL stats computation failed: %s", exc)
        raise
    finally:
        cursor.close()
        conn.close()


# ===================================================================
# TASK 3: SLA monitoring
# ===================================================================

def sla_monitoring(**context: Any) -> str:
    """
    Check if any DAG has had runs exceeding its expected SLA in the past week.
    SLA thresholds are defined per DAG.
    """
    sla_thresholds = {
        "sensor_data_etl": 1800,       # 30 minutes
        "data_quality_checks": 1200,   # 20 minutes
        "etl_audit_cleanup": 1800,     # 30 minutes
    }

    sf_hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn, cursor = _get_snowflake_cursor(sf_hook)

    try:
        cursor.execute(
            """
            SELECT
                DAG_ID,
                DAG_RUN_ID,
                DURATION_SECONDS,
                START_TIME,
                END_TIME,
                STATUS
            FROM AUDIT.ETL_AUDIT_LOG
            WHERE CREATED_AT >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
              AND DURATION_SECONDS IS NOT NULL
            ORDER BY DURATION_SECONDS DESC
            """
        )
        rows = cursor.fetchall()

        sla_violations: list = []
        for row in rows:
            dag_id = row[0]
            duration = float(row[2] or 0)
            threshold = sla_thresholds.get(dag_id, 3600)  # default 1 hour

            if duration > threshold:
                sla_violations.append({
                    "dag_id": dag_id,
                    "run_id": row[1],
                    "duration_sec": duration,
                    "sla_threshold_sec": threshold,
                    "exceeded_by_sec": round(duration - threshold, 2),
                    "start_time": str(row[3]),
                    "status": row[5],
                })

        result = {
            "check": "sla_monitoring",
            "period": "last_7_days",
            "total_runs_checked": len(rows),
            "violations": sla_violations,
            "violation_count": len(sla_violations),
            "passed": len(sla_violations) == 0,
        }

        context["ti"].xcom_push(key="sla_result", value=json.dumps(result, default=str))

        if sla_violations:
            logger.warning("SLA violations found: %d", len(sla_violations))
            for v in sla_violations:
                logger.warning(
                    "  %s run %s: %.0fs (SLA: %.0fs, exceeded by %.0fs)",
                    v["dag_id"], v["run_id"], v["duration_sec"],
                    v["sla_threshold_sec"], v["exceeded_by_sec"],
                )
        else:
            logger.info("No SLA violations in the past 7 days")

        return f"SLA: {len(sla_violations)} violations found"

    except Exception as exc:
        logger.error("SLA monitoring failed: %s", exc)
        raise
    finally:
        cursor.close()
        conn.close()


# ===================================================================
# TASK 4: Cleanup temp staging tables
# ===================================================================

def cleanup_temp_tables(**context: Any) -> str:
    """
    Drop staging temp tables (STG_TEMP_*) older than STAGING_RETENTION_DAYS.
    Calls the STAGING.CLEANUP_OLD_STAGING_TABLES stored procedure.
    """
    sf_hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn, cursor = _get_snowflake_cursor(sf_hook)

    try:
        cursor.execute(
            f"CALL STAGING.CLEANUP_OLD_STAGING_TABLES({STAGING_RETENTION_DAYS})"
        )
        result = cursor.fetchone()
        message = result[0] if result else "No result returned"

        logger.info("Staging cleanup: %s", message)
        context["ti"].xcom_push(key="cleanup_result", value=message)

        return f"Cleanup: {message}"

    except Exception as exc:
        logger.error("Staging cleanup failed: %s", exc)
        raise
    finally:
        cursor.close()
        conn.close()


# ===================================================================
# DAG DEFINITION
# ===================================================================

with DAG(
    dag_id="etl_audit_cleanup",
    default_args=default_args,
    description="Weekly ETL audit archival, statistics computation, SLA monitoring, and staging cleanup",
    schedule_interval="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["audit", "cleanup", "monitoring", "smart-factory"],
    doc_md=__doc__,
) as dag:

    t_archive = PythonOperator(
        task_id="archive_old_audits",
        python_callable=archive_old_audits,
    )

    t_stats = PythonOperator(
        task_id="compute_etl_stats",
        python_callable=compute_etl_stats,
    )

    t_sla = PythonOperator(
        task_id="sla_monitoring",
        python_callable=sla_monitoring,
    )

    t_cleanup = PythonOperator(
        task_id="cleanup_temp_tables",
        python_callable=cleanup_temp_tables,
    )

    t_archive >> t_stats >> t_sla >> t_cleanup
