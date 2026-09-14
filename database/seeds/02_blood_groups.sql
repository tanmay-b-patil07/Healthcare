-- ============================================================
-- VERIFY BLOOD GROUPS
-- ============================================================

SELECT
    enumlabel AS blood_group
FROM pg_enum
WHERE enumtypid = 'blood_group'::regtype
ORDER BY enumsortorder;