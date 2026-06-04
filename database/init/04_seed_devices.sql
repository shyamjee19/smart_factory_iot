-- Seed Devices
INSERT INTO device_master (device_id, device_name, device_type, location, install_date, status) VALUES
('DEV-OPC-001', 'OPC Controller Alpha', 'OPC', 'Assembly Line A', '2023-01-15', 'online'),
('DEV-CONV-001', 'Conveyor Belt Beta', 'Conveyor', 'Packaging Zone B', '2023-02-20', 'online'),
('DEV-PUMP-001', 'Coolant Pump Gamma', 'Pump', 'Cooling System C', '2023-03-10', 'online'),
('DEV-MOTOR-001', 'Drive Motor Delta', 'Motor', 'Drive Unit D', '2023-04-05', 'online'),
('DEV-BOILER-001', 'Steam Boiler Epsilon', 'Boiler', 'Boiler Room E', '2023-05-12', 'online')
ON CONFLICT (device_id) DO NOTHING;

-- Seed Device Health Initial Records
INSERT INTO device_health (device_id, uptime_percentage, anomaly_count, health_score, last_seen) VALUES
('DEV-OPC-001', 99.9, 0, 100.0, CURRENT_TIMESTAMP),
('DEV-CONV-001', 99.5, 0, 98.0, CURRENT_TIMESTAMP),
('DEV-PUMP-001', 98.0, 2, 95.0, CURRENT_TIMESTAMP),
('DEV-MOTOR-001', 99.0, 1, 97.0, CURRENT_TIMESTAMP),
('DEV-BOILER-001', 99.9, 0, 100.0, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Seed Admin User
-- Password is 'password123' hashed with bcrypt
INSERT INTO users (username, email, hashed_password, role, is_active) VALUES
('admin', 'admin@smartfactory.local', '$2b$12$A5M5N0Mr4VTd8zHuYRgZqub8V5T6BBK/6FENUyO5OXM9oclf8JqIK', 'admin', true)
ON CONFLICT (username) DO NOTHING;
