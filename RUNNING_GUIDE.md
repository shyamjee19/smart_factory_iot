# Running Guide: Zero-Mock IoT Telemetry Pipeline 🏭📈

This guide details the exact procedures required to configure, test, and run the **Smart Factory IoT Analytics & Monitoring Platform** locally in a strict, zero-mock environment. Every metric, chart, and alert in this deployment comes directly from actual records flowing through the pipeline.

---

## 1. Project Setup Checklist

Follow these 10 steps in sequence to bring up the pipeline and verify the live telemetry flow:

| Step | Action | Description |
|---|---|---|
| **Step 1** | **Configure PostgreSQL** | Set up the target database host, port, DB name, credentials, and verification tools. |
| **Step 2** | **Configure Snowflake** | Set up the data warehouse credentials, warehouse name, and integration target. |
| **Step 3** | **Configure MQTT** | Set up Mosquitto broker properties for ingestion routing. |
| **Step 4** | **Configure Kafka** | Establish the Kafka cluster bootstrap brokers for stream buffering. |
| **Step 5** | **Start Docker Services** | Spin up the infrastructure core (Zookeeper, Kafka, Mosquitto, Postgres, Bridge, FastAPI, React). |
| **Step 6** | **Run Simulator** | Initiate the virtual devices to start publishing realistic industrial telemetry. |
| **Step 7** | **Verify PostgreSQL Ingestion** | Query the local raw database layer to verify telemetry inserts. |
| **Step 8** | **Verify Airflow ETL** | Monitor the data synchronization and schema merge operations into the staging layer. |
| **Step 9** | **Verify Snowflake Warehouse** | Query Snowflake fact tables to verify Slowly Changing Dimension (SCD) mapping. |
| **Step 10** | **Open Dashboard** | Access the frontend React UI and monitor live WebSocket-backed chart ticks. |

---

## 2. Database Connection Documentation

### A. PostgreSQL Ingestion Configuration

#### Exact File Paths:
1. **[`.env`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/.env)**: The master configuration file.
2. **[`backend/app/config.py`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/backend/app/config.py)**: Loads database URL parameters into Pydantic BaseSettings.
3. **[`backend/app/database.py`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/backend/app/database.py)**: Configures the SQLAlchemy asynchronous engine and session maker using:
   `DATABASE_URL = postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>`
4. **[`spark-streaming/stream_processor.py`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/spark-streaming/stream_processor.py)**: Constructs the JDBC connection string `jdbc:postgresql://<host>:<port>/<db>` used to append micro-batches directly.
5. **[`airflow/dags/sensor_etl_dag.py`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/airflow/dags/sensor_etl_dag.py)**: Declares the connection profile `postgres_default` used to extract transactional telemetry.

#### Config Variables to Change:
In the root [`.env`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/.env) file:
```ini
POSTGRES_HOST=postgres       # Change to your remote IP if DB is hosted externally
POSTGRES_PORT=5432           # Change if using a non-standard port
POSTGRES_DB=iot_db           # Change to your target schema/database name
POSTGRES_USER=admin          # Change to your target username
POSTGRES_PASSWORD=admin123  # CHANGE THIS VALUE BEFORE RUNNING
```

#### How to Test the Connection:
Run a manual check using `pg_isready` inside the container or using `psql` locally:
```bash
# Test using docker container healthchecks
docker exec -it sf-postgres pg_isready -U admin -d iot_db
```

---

### B. Snowflake Data Warehouse Configuration

#### Exact File Paths:
1. **[`.env`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/.env)**: The master configuration file.
2. **[`airflow/plugins/operators/snowflake_load.py`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/airflow/plugins/operators/snowflake_load.py)**: Uses snowflake hooks to merge incremental loads into DWH staging.
3. **[`airflow/dags/sensor_etl_dag.py`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/airflow/dags/sensor_etl_dag.py)**: Uses the custom loader task referencing connection profile `snowflake_default`.

#### Config Variables to Change:
In the root [`.env`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/.env) file:
```ini
SNOWFLAKE_ACCOUNT=ITSWWZI-UJ44877  # CHANGE THIS VALUE BEFORE RUNNING (Snowflake account locator)
SNOWFLAKE_USER=SHYAM123             # CHANGE THIS VALUE BEFORE RUNNING (Snowflake login user)
SNOWFLAKE_PASSWORD=Z5AcE7D9C3R8Eem  # CHANGE THIS VALUE BEFORE RUNNING (Snowflake password)
SNOWFLAKE_WAREHOUSE=COMPUTE_WH      # CHANGE THIS VALUE BEFORE RUNNING (Snowflake query warehouse)
SNOWFLAKE_DATABASE=IOT_DB           # CHANGE THIS VALUE BEFORE RUNNING (Snowflake target database)
SNOWFLAKE_SCHEMA=PUBLIC             # CHANGE THIS VALUE BEFORE RUNNING (Snowflake target schema)
SNOWFLAKE_ROLE=SYSADMIN             # CHANGE THIS VALUE BEFORE RUNNING (Snowflake access role)
SNOWFLAKE_ENABLED=false             # Toggle to true to active Snowflake DWH synchronization
```

#### How to Test the Connection:
Using Snowflake's command-line tool `snowsql` or through a python check script in `scratch/`:
```bash
# Verify Snowflake credentials locally using snowsql
snowsql -a ITSWWZI-UJ44877 -u SHYAM123
```

---

## 3. Pipeline Connection & Verification Manual

### A. Ingestion Configuration

#### Mosquitto MQTT:
In [`.env`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/.env):
```ini
MQTT_HOST=mqtt   # Change to public broker IP if MQTT is hosted externally
MQTT_PORT=1883   # Default Mosquitto port
```

#### Apache Kafka:
In [`.env`](file:///c:/Users/ASUS/OneDrive/Desktop/Full%20stack%20project/smart-factory-iot/.env):
```ini
KAFKA_BOOTSTRAP_SERVERS=kafka:9092 # Change to your external broker IP if hosted externally
```

---

## 4. Stage-by-Stage SQL Verification Queries

Connect to the respective database terminals and execute the following verification queries to ensure the pipeline is running successfully:

### 1. PostgreSQL (Transactional / Raw Ingestion)
Verifies that telemetry data has successfully flowed:
`MQTT Broker ➡️ MQTT-Kafka Bridge ➡️ Kafka Topic ➡️ Spark Structured Streaming ➡️ Postgres`

*   **Query 1: Row Count Verification**
    Ensure telemetry rows are increasing continuously:
    ```sql
    SELECT COUNT(*) FROM sensor_data;
    ```
*   **Query 2: Timestamp & Payload Audit**
    Check the last 10 raw entries to verify realistic values (temperature, pressure, vibration) are logged:
    ```sql
    SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;
    ```
*   **Query 3: Anomalous Alert Ingestion**
    Check the alert rules triggered by Spark Streaming:
    ```sql
    SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5;
    ```

---

### 2. Snowflake (Analytical Data Warehouse)
Verifies that the transactional records have successfully synced:
`PostgreSQL Raw DB ➡️ Airflow ETL Extraction ➡️ Snowflake Staging ➡️ Dimension Merge (SCD Type 2) ➡️ Fact Load`

*   **Query 1: Fact Ingestion Verification**
    Check the total loaded sensor facts in the DWH:
    ```sql
    SELECT COUNT(*) FROM FACT_SENSOR_DATA;
    ```
*   **Query 2: Dimensional SCD Type 2 Audit**
    Check if device keys, date keys, and sensor columns maps correctly:
    ```sql
    SELECT * FROM FACT_SENSOR_DATA LIMIT 10;
    ```
*   **Query 3: Date Key Lookup Validation**
    Confirm that date keys map correctly to analytical aggregates:
    ```sql
    SELECT D.LOCATION, AVG(F.TEMPERATURE) AS AVG_TEMP 
    FROM FACT_SENSOR_DATA F
    JOIN DIM_DEVICE D ON F.DEVICE_KEY = D.DEVICE_KEY
    WHERE D.IS_CURRENT = TRUE
    GROUP BY D.LOCATION;
    ```
