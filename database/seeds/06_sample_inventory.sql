-- ============================================================
-- SAMPLE BLOOD BANK INVENTORY
-- DEVELOPMENT / TESTING ONLY
-- ============================================================

INSERT INTO blood_inventory (
    blood_bank_id,
    blood_group,
    available_units,
    reserved_units
)
VALUES
(
    (
        SELECT id
        FROM blood_banks
        WHERE name = 'Test Blood Bank'
    ),
    'O_POSITIVE',
    10,
    0
),
(
    (
        SELECT id
        FROM blood_banks
        WHERE name = 'Test Blood Bank'
    ),
    'O_NEGATIVE',
    5,
    0
),
(
    (
        SELECT id
        FROM blood_banks
        WHERE name = 'Test Blood Bank'
    ),
    'A_POSITIVE',
    8,
    0
),
(
    (
        SELECT id
        FROM blood_banks
        WHERE name = 'Test Blood Bank'
    ),
    'B_POSITIVE',
    6,
    0
)
ON CONFLICT (blood_bank_id, blood_group)
DO UPDATE SET
    available_units = EXCLUDED.available_units,
    reserved_units = EXCLUDED.reserved_units,
    updated_at = NOW();