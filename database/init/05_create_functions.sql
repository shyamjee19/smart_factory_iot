-- Function to update device health score based on recent anomalies
CREATE OR REPLACE FUNCTION update_device_health(p_device_id VARCHAR)
RETURNS void AS $$
DECLARE
    v_anomaly_count INT;
    v_health_score DECIMAL(5,2);
BEGIN
    -- Count anomalies in the last 24 hours
    SELECT COUNT(*)
    INTO v_anomaly_count
    FROM alerts
    WHERE device_id = p_device_id
      AND created_at >= NOW() - INTERVAL '24 hours'
      AND severity IN ('WARNING', 'CRITICAL');

    -- Calculate simple health score (starts at 100, drops for each anomaly)
    -- This is a simplified logic for demonstration
    v_health_score := GREATEST(0, 100 - (v_anomaly_count * 5));

    -- Update the health table
    UPDATE device_health
    SET anomaly_count = v_anomaly_count,
        health_score = v_health_score,
        last_seen = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE device_id = p_device_id;
    
    -- If device didn't exist in health table, insert it
    IF NOT FOUND THEN
        INSERT INTO device_health (device_id, uptime_percentage, anomaly_count, health_score, last_seen)
        VALUES (p_device_id, 100.0, v_anomaly_count, v_health_score, CURRENT_TIMESTAMP);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update health when a new alert is generated
CREATE OR REPLACE FUNCTION trg_update_health_on_alert()
RETURNS trigger AS $$
BEGIN
    PERFORM update_device_health(NEW.device_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_alert_insert
AFTER INSERT ON alerts
FOR EACH ROW
EXECUTE FUNCTION trg_update_health_on_alert();

-- Function to get a summary of a device
CREATE OR REPLACE FUNCTION get_device_summary(p_device_id VARCHAR)
RETURNS TABLE (
    device_name VARCHAR,
    status VARCHAR,
    health_score DECIMAL,
    recent_alerts BIGINT,
    avg_temp_24h DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dm.device_name,
        dm.status,
        dh.health_score,
        (SELECT COUNT(*) FROM alerts a WHERE a.device_id = dm.device_id AND a.created_at >= NOW() - INTERVAL '24 hours'),
        (SELECT AVG(temperature)::DECIMAL(8,2) FROM sensor_data sd WHERE sd.device_id = dm.device_id AND sd.timestamp >= NOW() - INTERVAL '24 hours')
    FROM device_master dm
    LEFT JOIN device_health dh ON dm.device_id = dh.device_id
    WHERE dm.device_id = p_device_id;
END;
$$ LANGUAGE plpgsql;
