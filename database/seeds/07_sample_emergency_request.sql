-- ============================================================
-- SAMPLE EMERGENCY BLOOD REQUEST
-- DEVELOPMENT / TESTING ONLY
-- ============================================================

INSERT INTO blood_requests (
    requester_id,
    hospital_id,
    blood_group,
    units_required,
    units_fulfilled,
    urgency,
    status,
    location,
    address,
    required_by
)
VALUES (
    (
        SELECT id
        FROM users
        WHERE email = 'requester@test.local'
    ),

    (
        SELECT id
        FROM hospitals
        WHERE user_id = (
            SELECT id
            FROM users
            WHERE email = 'hospital@test.local'
        )
    ),

    'O_POSITIVE',

    2,

    0,

    'CRITICAL',

    'REQUESTED',

    ST_SetSRID(
        ST_MakePoint(77.5946, 12.9716),
        4326
    )::geography,

    'Bengaluru Central',

    NOW() + INTERVAL '2 hours'
);