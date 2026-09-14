-- ============================================================
-- SAMPLE BLOOD BANK
-- DEVELOPMENT / TESTING ONLY
-- ============================================================

INSERT INTO blood_banks (
    user_id,
    name,
    address,
    location,
    verification_status
)
VALUES (
    (SELECT id
     FROM users
     WHERE email = 'bloodbank@test.local'),

    'Test Blood Bank',

    'Bengaluru Central',

    ST_SetSRID(
        ST_MakePoint(77.5946, 12.9716),
        4326
    )::geography,

    TRUE
)
ON CONFLICT (user_id) DO NOTHING;