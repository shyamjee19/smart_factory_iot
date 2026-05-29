CREATE INDEX idx_sensor_data_device_id_timestamp ON sensor_data (device_id, timestamp DESC);
CREATE INDEX idx_alerts_device_id ON alerts (device_id);
CREATE INDEX idx_alerts_created_at ON alerts (created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts (severity);
CREATE INDEX idx_device_health_device_id ON device_health (device_id);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_email ON users (email);
