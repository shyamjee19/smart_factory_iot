# Interview Guide: Smart Factory IoT Platform

This guide will help you prepare to present this project in technical interviews. It covers the key design decisions, architecture components, and typical interview questions you might face.

## Project Overview
The "Smart Factory IoT Analytics & Monitoring Platform" is an end-to-end data pipeline and web application designed to demonstrate enterprise-grade skills in Data Engineering, Full Stack Development, Cloud Architecture, and DevOps.

## Key Architecture Decisions (The "Why")

### 1. Decoupling with Kafka
*   **Why:** IoT devices generate high-volume, high-velocity data. If the database or processing engine goes down, data is lost.
*   **Role:** Kafka acts as a shock absorber (buffer). It decouples the data producers (MQTT broker) from the consumers (Spark Streaming), ensuring resilience and scalability.

### 2. Spark Structured Streaming
*   **Why:** We need near real-time processing to detect anomalies (e.g., a boiler overheating). Batch processing (like Airflow alone) is too slow for critical alerts.
*   **Role:** Consumes data from Kafka, applies aggregations (windowing), evaluates alert rules, and writes results to PostgreSQL.

### 3. PostgreSQL (Raw Layer) vs. Snowflake (Analytics Layer)
*   **Why:** PostgreSQL is excellent for transactional workloads (OLTP), handling the fast, constant inserts from Spark and serving the live dashboard backend efficiently. Snowflake is a columnar Data Warehouse (OLAP) optimized for complex analytical queries across massive datasets.
*   **Role:** Postgres handles the "live" state and raw ingestion. Snowflake handles historical reporting, trend analysis, and BI integration. Airflow orchestrates the ETL process moving data from Postgres to Snowflake.

### 4. FastAPI & React
*   **Why FastAPI:** High performance (async support), automatic Swagger documentation, built-in validation (Pydantic), making it ideal for a modern data-driven API.
*   **Why React:** Component-based, vast ecosystem, perfect for building a responsive, interactive dashboard to visualize the data.

## Typical Interview Questions

**Q: How does your system handle sudden spikes in sensor data?**
> A: The MQTT broker quickly passes data to Kafka. Kafka partitions the topics, allowing us to buffer the spike. We can then scale out our Spark Streaming consumers horizontally to process the backlog without losing data.

**Q: How do you ensure data quality in the pipeline?**
> A: I implemented a multi-layered approach. Spark applies schema validation upon ingestion. Before loading data into Snowflake, Airflow runs a Data Quality Check DAG (e.g., verifying row counts, range constraints, and referential integrity).

**Q: Why use SCD Type 2 in Snowflake?**
> A: Slowly Changing Dimension (SCD) Type 2 allows us to track historical changes to device metadata. If a device is moved from "Assembly Line A" to "Line B", we preserve the old record with an expiry date and create a new active record. This ensures historical reports are accurate based on where the device was *at the time*.

**Q: How do you handle database migrations?**
> A: While initial scripts are provided in `database/init`, a production environment would use a tool like Alembic (for SQLAlchemy) to manage schema versions and apply incremental migrations safely.

## Areas to Highlight
*   **Resilience:** Emphasize the MQTT -> Kafka -> Spark flow for fault tolerance.
*   **Scalability:** Mention that the architecture supports scaling individual components (e.g., more Spark executors, more backend API pods in Kubernetes).
*   **Analytics:** Highlight the Airflow orchestration and Snowflake dimensional modeling.
*   **Full Stack:** Discuss the integration of the React frontend with the FastAPI backend using JWT authentication.
