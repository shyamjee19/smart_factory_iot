-- Device Master
CREATE TABLE device_master (
    device_id VARCHAR(50) PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    install_date DATE,
    status VARCHAR(20) DEFAULT 'offline',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sensor Data (partitioned by month)
CREATE TABLE sensor_data (
    id BIGSERIAL,
    device_id VARCHAR(50) REFERENCES device_master(device_id),
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(8,3),
    humidity DECIMAL(8,3),
    pressure DECIMAL(8,3),
    vibration DECIMAL(8,4),
    voltage DECIMAL(8,3),
    current DECIMAL(8,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Default partition for sensor_data
CREATE TABLE sensor_data_default PARTITION OF sensor_data DEFAULT;

-- Alerts
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES device_master(device_id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('INFO','WARNING','CRITICAL')),
    metric VARCHAR(50),
    threshold_value DECIMAL(10,3),
    actual_value DECIMAL(10,3),
    message TEXT,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Device Health
CREATE TABLE device_health (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES device_master(device_id),
    uptime_percentage DECIMAL(5,2),
    anomaly_count INTEGER DEFAULT 0,
    health_score DECIMAL(5,2),
    last_seen TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ETL Audit
CREATE TABLE etl_audit (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    dag_id VARCHAR(100),
    task_id VARCHAR(100),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    rows_extracted INTEGER,
    rows_transformed INTEGER,
    rows_loaded INTEGER,
    status VARCHAR(20) DEFAULT 'RUNNING',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (for auth)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('admin','operator','viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
