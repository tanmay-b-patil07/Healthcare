-- USERS

CREATE INDEX IF NOT EXISTS idx_users_role
ON users(role);

CREATE INDEX IF NOT EXISTS idx_users_phone
ON users(phone);

CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);


-- DONORS

CREATE INDEX IF NOT EXISTS idx_donors_blood_group
ON donors(blood_group);

CREATE INDEX IF NOT EXISTS idx_donors_available
ON donors(is_available);

CREATE INDEX IF NOT EXISTS idx_donors_location
ON donors USING GIST(location);


-- HOSPITALS

CREATE INDEX IF NOT EXISTS idx_hospitals_location
ON hospitals USING GIST(location);


-- BLOOD BANKS

CREATE INDEX IF NOT EXISTS idx_blood_banks_location
ON blood_banks USING GIST(location);


-- BLOOD INVENTORY

CREATE INDEX IF NOT EXISTS idx_inventory_blood_group
ON blood_inventory(blood_group);


-- BLOOD REQUESTS

CREATE INDEX IF NOT EXISTS idx_requests_status
ON blood_requests(status);

CREATE INDEX IF NOT EXISTS idx_requests_blood_group
ON blood_requests(blood_group);

CREATE INDEX IF NOT EXISTS idx_requests_urgency
ON blood_requests(urgency);

CREATE INDEX IF NOT EXISTS idx_requests_location
ON blood_requests USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_requests_created_at
ON blood_requests(created_at);


-- DONOR MATCHES

CREATE INDEX IF NOT EXISTS idx_matches_request
ON donor_matches(request_id);

CREATE INDEX IF NOT EXISTS idx_matches_donor
ON donor_matches(donor_id);

CREATE INDEX IF NOT EXISTS idx_matches_score
ON donor_matches(total_score DESC);


-- NOTIFICATIONS

CREATE INDEX IF NOT EXISTS idx_notifications_user
ON notifications(user_id);

CREATE INDEX IF NOT EXISTS idx_notifications_status
ON notifications(status);


-- AUDIT LOGS

CREATE INDEX IF NOT EXISTS idx_audit_logs_user
ON audit_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
ON audit_logs(created_at);