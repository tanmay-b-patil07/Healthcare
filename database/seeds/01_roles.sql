-- ============================================================
-- VERIFY USER ROLES
-- ============================================================

SELECT
    enumlabel AS role
FROM pg_enum
WHERE enumtypid = 'user_role'::regtype
ORDER BY enumsortorder;