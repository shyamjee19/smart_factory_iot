import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, current_timestamp, expr, when
from schemas.sensor_schema import sensor_schema
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Spark-Streaming")

# Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_SENSOR", "factory.sensor.raw")

# Postgres Config
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "smart_factory")
PG_USER = os.getenv("POSTGRES_USER", "factory_admin")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "change_me_in_production")
JDBC_URL = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}"
JDBC_DRIVER = "org.postgresql.Driver"

CHECKPOINT_DIR = os.getenv("SPARK_CHECKPOINT_DIR", "/tmp/spark-checkpoints")

def write_to_postgres(df, epoch_id, table_name, mode="append"):
    """ForeachBatch function to write to PostgreSQL."""
    try:
        df.write \
            .format("jdbc") \
            .option("url", JDBC_URL) \
            .option("dbtable", table_name) \
            .option("user", PG_USER) \
            .option("password", PG_PASS) \
            .option("driver", JDBC_DRIVER) \
            .mode(mode) \
            .save()
    except Exception as e:
        logger.error(f"Error writing to Postgres table {table_name}: {e}")

def create_spark_session():
    """Initialize SparkSession with necessary packages."""
    return SparkSession.builder \
        .appName("SmartFactoryStreaming") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark Session Initialized.")

    # Read from Kafka
    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    # Parse JSON payload
    df_parsed = df_kafka.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), sensor_schema).alias("data")) \
        .select("data.*") \
        .withColumn("timestamp", col("timestamp").cast("timestamp")) \
        .withColumn("created_at", current_timestamp())

    # 1. Write Raw Data to PostgreSQL
    # In production, you might write to a data lake first, then batch to DB.
    # We use foreachBatch here for simplicity with JDBC.
    query_raw = df_parsed.writeStream \
        .foreachBatch(lambda df, epoch_id: write_to_postgres(df, epoch_id, "sensor_data")) \
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/raw") \
        .trigger(processingTime='10 seconds') \
        .start()

    # 2. Alert Generation Rules
    # Example rules:
    # - Temperature > 85 -> CRITICAL
    # - Vibration > 5.0 -> WARNING
    
    df_alerts = df_parsed.withColumn("alert_type", 
            when(col("temperature") > 85, "High Temperature")
            .when(col("vibration") > 5.0, "High Vibration")
            .when(col("pressure") > 10.0, "High Pressure")
            .otherwise(None)
        ) \
        .filter(col("alert_type").isNotNull()) \
        .select(
            col("device_id"),
            col("alert_type"),
            when(col("temperature") > 85, "CRITICAL")
                .when(col("pressure") > 10.0, "CRITICAL")
                .otherwise("WARNING").alias("severity"),
            when(col("temperature") > 85, "temperature")
                .when(col("vibration") > 5.0, "vibration")
                .when(col("pressure") > 10.0, "pressure").alias("metric"),
            # Threshold values for demo purposes
            when(col("temperature") > 85, 85.0)
                .when(col("vibration") > 5.0, 5.0)
                .when(col("pressure") > 10.0, 10.0).alias("threshold_value"),
            # Actual values
            when(col("temperature") > 85, col("temperature"))
                .when(col("vibration") > 5.0, col("vibration"))
                .when(col("pressure") > 10.0, col("pressure")).alias("actual_value"),
            current_timestamp().alias("created_at")
        ) \
        .withColumn("message", expr("concat(alert_type, ' detected on device ', device_id, '. Value: ', actual_value)")) \
        .withColumn("is_acknowledged", expr("false"))

    query_alerts = df_alerts.writeStream \
        .foreachBatch(lambda df, epoch_id: write_to_postgres(df, epoch_id, "alerts")) \
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/alerts") \
        .trigger(processingTime='10 seconds') \
        .start()

    # Wait for termination
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()
