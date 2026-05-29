from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Define the schema for the incoming JSON messages from MQTT/Kafka
sensor_schema = StructType([
    StructField("device_id", StringType(), True),
    StructField("device_type", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("location", StringType(), True),
    StructField("status", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("pressure", DoubleType(), True),
    StructField("vibration", DoubleType(), True),
    StructField("voltage", DoubleType(), True),
    StructField("current", DoubleType(), True)
])
