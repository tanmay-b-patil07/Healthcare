-- ============================================================
-- ADDITIONAL DATA INTEGRITY CONSTRAINTS
-- ============================================================


-- ============================================================
-- DONOR MATCH SCORE VALIDATION
-- Scores must remain between 0 and 100.
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'donor_matches_compatibility_score_range'
    ) THEN
        ALTER TABLE donor_matches
        ADD CONSTRAINT donor_matches_compatibility_score_range
        CHECK (
            compatibility_score >= 0
            AND compatibility_score <= 100
        );
    END IF;
END
$$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'donor_matches_availability_score_range'
    ) THEN
        ALTER TABLE donor_matches
        ADD CONSTRAINT donor_matches_availability_score_range
        CHECK (
            availability_score >= 0
            AND availability_score <= 100
        );
    END IF;
END
$$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'donor_matches_urgency_score_range'
    ) THEN
        ALTER TABLE donor_matches
        ADD CONSTRAINT donor_matches_urgency_score_range
        CHECK (
            urgency_score >= 0
            AND urgency_score <= 100
        );
    END IF;
END
$$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'donor_matches_total_score_range'
    ) THEN
        ALTER TABLE donor_matches
        ADD CONSTRAINT donor_matches_total_score_range
        CHECK (
            total_score >= 0
            AND total_score <= 100
        );
    END IF;
END
$$;


-- ============================================================
-- DISTANCE VALIDATION
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'donor_matches_distance_non_negative'
    ) THEN
        ALTER TABLE donor_matches
        ADD CONSTRAINT donor_matches_distance_non_negative
        CHECK (
            distance_km IS NULL
            OR distance_km >= 0
        );
    END IF;
END
$$;


-- ============================================================
-- BLOOD REQUEST VALIDATION
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'blood_requests_required_units_positive'
    ) THEN
        ALTER TABLE blood_requests
        ADD CONSTRAINT blood_requests_required_units_positive
        CHECK (units_required > 0);
    END IF;
END
$$;


-- ============================================================
-- DONATION VALIDATION
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'donations_units_positive'
    ) THEN
        ALTER TABLE donations
        ADD CONSTRAINT donations_units_positive
        CHECK (units > 0);
    END IF;
END
$$;


-- ============================================================
-- INVENTORY VALIDATION
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'blood_inventory_units_non_negative'
    ) THEN
        ALTER TABLE blood_inventory
        ADD CONSTRAINT blood_inventory_units_non_negative
        CHECK (
            available_units >= 0
            AND reserved_units >= 0
        );
    END IF;
END
$$;