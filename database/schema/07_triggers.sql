-- ============================================================
-- AUTOMATIC UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


-- USERS
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- DONORS
DROP TRIGGER IF EXISTS trg_donors_updated_at ON donors;

CREATE TRIGGER trg_donors_updated_at
BEFORE UPDATE ON donors
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- HOSPITALS
DROP TRIGGER IF EXISTS trg_hospitals_updated_at ON hospitals;

CREATE TRIGGER trg_hospitals_updated_at
BEFORE UPDATE ON hospitals
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- BLOOD BANKS
DROP TRIGGER IF EXISTS trg_blood_banks_updated_at ON blood_banks;

CREATE TRIGGER trg_blood_banks_updated_at
BEFORE UPDATE ON blood_banks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- BLOOD INVENTORY
DROP TRIGGER IF EXISTS trg_blood_inventory_updated_at ON blood_inventory;

CREATE TRIGGER trg_blood_inventory_updated_at
BEFORE UPDATE ON blood_inventory
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- BLOOD REQUESTS
DROP TRIGGER IF EXISTS trg_blood_requests_updated_at ON blood_requests;

CREATE TRIGGER trg_blood_requests_updated_at
BEFORE UPDATE ON blood_requests
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- AUDIT LOGGING
-- ============================================================

CREATE OR REPLACE FUNCTION create_audit_log()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
DECLARE
    current_user_id BIGINT;
    affected_entity_id BIGINT;
BEGIN

    BEGIN
        current_user_id :=
            NULLIF(current_setting('app.current_user_id', true), '')::BIGINT;
    EXCEPTION
        WHEN OTHERS THEN
            current_user_id := NULL;
    END;

    IF TG_OP = 'DELETE' THEN
        affected_entity_id := OLD.id;
    ELSE
        affected_entity_id := NEW.id;
    END IF;

    INSERT INTO audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        metadata
    )
    VALUES (
        current_user_id,
        TG_OP,
        TG_TABLE_NAME,
        affected_entity_id,
        jsonb_build_object(
            'timestamp', NOW()
        )
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

-- ============================================================
-- AUDIT TRIGGERS
-- ============================================================

-- BLOOD REQUESTS
DROP TRIGGER IF EXISTS trg_blood_requests_audit
ON blood_requests;

CREATE TRIGGER trg_blood_requests_audit
AFTER INSERT OR UPDATE OR DELETE
ON blood_requests
FOR EACH ROW
EXECUTE FUNCTION create_audit_log();


-- DONOR MATCHES
DROP TRIGGER IF EXISTS trg_donor_matches_audit
ON donor_matches;

CREATE TRIGGER trg_donor_matches_audit
AFTER INSERT OR UPDATE OR DELETE
ON donor_matches
FOR EACH ROW
EXECUTE FUNCTION create_audit_log();


-- DONATIONS
DROP TRIGGER IF EXISTS trg_donations_audit
ON donations;

CREATE TRIGGER trg_donations_audit
AFTER INSERT OR UPDATE OR DELETE
ON donations
FOR EACH ROW
EXECUTE FUNCTION create_audit_log();


-- BLOOD INVENTORY
DROP TRIGGER IF EXISTS trg_blood_inventory_audit
ON blood_inventory;

CREATE TRIGGER trg_blood_inventory_audit
AFTER INSERT OR UPDATE OR DELETE
ON blood_inventory
FOR EACH ROW
EXECUTE FUNCTION create_audit_log();