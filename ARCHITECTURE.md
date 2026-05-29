# Architecture Details: Smart Factory IoT Platform

This document provides a detailed breakdown of the architectural layers in the Smart Factory IoT Analytics & Monitoring Platform.

## 1. Data Ingestion Layer

**Goal:** Simulate realistic industrial equipment and reliably transport the telemetry data.

*   **IoT Simulator (`iot-simulator/`)**: A Python application that spawns virtual devices (OPC Controllers, Conveyor Belts, Pumps, Motors, Boilers). It generates realistic telemetry (temperature, vibration, pressure, etc.) with configurable noise, drift, and randomized anomaly injection.
*   **MQTT Broker (`mqtt/`)**: Eclipse Mosquitto serves as the initial ingestion point. MQTT is chosen for its lightweight protocol, ideal for resource-constrained IoT devices.
*   **MQTT-Kafka Bridge (`mqtt-kafka-bridge/`)**: A Python service that subscribes to MQTT topics and reliably publishes the payloads into an Apache Kafka topic (`factory.sensor.raw`).

## 2. Stream Processing Layer

**Goal:** Process high-velocity data in real-time, generate alerts, and persist raw data.

*   **Apache Kafka (`kafka/`)**: Acts as the central nervous system, decoupling the ingestion from processing and ensuring high durability and scalability.
*   **Spark Structured Streaming (`spark-streaming/`)**: Consumes from Kafka, applies schema validation, computes windowed aggregations (e.g., 5-minute averages), evaluates real-time rules to generate alerts, and writes the output to PostgreSQL.

## 3. Storage Layer

**Goal:** Provide durable storage for both operational (raw) data and analytical (transformed) data.

*   **PostgreSQL (`database/`)**: The operational database. It stores device metadata, raw time-series sensor data (partitioned for performance), active alerts, and calculated device health metrics.
*   **Snowflake (`snowflake/`)**: The enterprise data warehouse. It utilizes a dimensional modeling approach (Star Schema) with `DIM_DEVICE` (supporting Slowly Changing Dimensions Type 2), `DIM_DATE`, `FACT_SENSOR_DATA`, and `FACT_ALERTS` to support complex, historical analytical queries.

## 4. Analytics & ETL Layer

**Goal:** Orchestrate the movement and transformation of data from the operational database to the data warehouse.

*   **Apache Airflow (`airflow/`)**: Manages the ETL pipelines.
    *   `sensor_etl_dag`: Extracts data from Postgres, performs necessary transformations (e.g., generating surrogate keys), and loads it into Snowflake.
    *   `data_quality_dag`: Runs automated checks (null checks, range validations) to ensure data integrity.
    *   `audit_dag`: Monitors SLA compliance and logs ETL job statistics.

## 5. Backend API Layer

**Goal:** Securely expose data and business logic to the frontend and other consumers.

*   **FastAPI (`backend/`)**: A high-performance Python web framework.
    *   **Authentication & Authorization**: Implements JWT-based auth and Role-Based Access Control (RBAC - Admin, Operator, Viewer).
    *   **REST Endpoints**: Provides CRUD operations for devices, alerts, and analytical queries (e.g., time-series data for charts).
    *   **WebSockets**: Maintains persistent connections with the frontend to push real-time sensor updates, avoiding polling overhead.

## 6. Frontend Presentation Layer

**Goal:** Provide a rich, interactive, and premium user experience for monitoring the factory.

*   **React Dashboard (`frontend/`)**: Built with React 18, TypeScript, and Vite.
    *   **UI Framework**: Material UI (MUI) v5 configured with a custom, enterprise-grade dark theme (glassmorphism, gradients).
    *   **State Management**: Zustand for global state (auth, device context).
    *   **Visualizations**: Recharts for dynamic time-series charts (temperature, vibration).

## 7. DevOps & Observability Layer

**Goal:** Ensure the system is easily deployable, scalable, and fully monitored.

*   **Containerization**: Docker and Docker Compose for reproducible local environments.
*   **Orchestration**: Complete Kubernetes manifests (`k8s/`) for production deployment (Deployments, Services, ConfigMaps, Secrets, Ingress, HPA).
*   **Monitoring**: Prometheus for metrics scraping, Grafana for visualization (pre-built dashboards), and Loki for log aggregation.
*   **CI/CD**: GitHub Actions workflows for continuous integration (testing, linting) and continuous deployment (Docker image builds, push to GHCR).
