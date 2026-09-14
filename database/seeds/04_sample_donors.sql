-- ============================================================
-- SAMPLE DONOR PROFILES
-- DEVELOPMENT / TESTING ONLY
-- ============================================================

INSERT INTO donors (
    user_id,
    blood_group,
    date_of_birth,
    location,
    address,
    is_available,
    last_donation_date
)
VALUES

(
    (SELECT id FROM users WHERE email = 'donor1@test.local'),
    'O_POSITIVE',
    '2000-05-15',
    ST_SetSRID(
        ST_MakePoint(77.5946, 12.9716),
        4326
    )::geography,
    'Bengaluru - Central',
    TRUE,
    '2026-05-01'
),

(
    (SELECT id FROM users WHERE email = 'donor2@test.local'),
    'O_POSITIVE',
    '1999-08-20',
    ST_SetSRID(
        ST_MakePoint(77.6101, 12.9352),
        4326
    )::geography,
    'Bengaluru - South',
    TRUE,
    '2026-04-15'
),

(
    (SELECT id FROM users WHERE email = 'donor3@test.local'),
    'A_POSITIVE',
    '2001-02-10',
    ST_SetSRID(
        ST_MakePoint(77.6412, 12.9784),
        4326
    )::geography,
    'Bengaluru - East',
    TRUE,
    '2026-05-20'
)

ON CONFLICT (user_id) DO NOTHING;