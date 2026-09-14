-- ============================================================
-- SAMPLE USERS
-- FOR DEVELOPMENT / TESTING ONLY
-- ============================================================

INSERT INTO users (
    name,
    email,
    phone,
    password_hash,
    role,
    is_verified,
    is_active
)
VALUES
(
    'Test Donor 1',
    'donor1@test.local',
    '9000000001',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'DONOR',
    TRUE,
    TRUE
),
(
    'Test Donor 2',
    'donor2@test.local',
    '9000000002',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'DONOR',
    TRUE,
    TRUE
),
(
    'Test Donor 3',
    'donor3@test.local',
    '9000000003',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'DONOR',
    TRUE,
    TRUE
),
(
    'Test Requester',
    'requester@test.local',
    '9000000004',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'REQUESTER',
    TRUE,
    TRUE
),
(
    'Test Hospital',
    'hospital@test.local',
    '9000000005',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'HOSPITAL',
    TRUE,
    TRUE
),
(
    'Test Blood Bank',
    'bloodbank@test.local',
    '9000000006',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'BLOOD_BANK',
    TRUE,
    TRUE
),
(
    'Test Admin',
    'admin@test.local',
    '9000000007',
    'TEST_HASH_NOT_FOR_PRODUCTION',
    'ADMIN',
    TRUE,
    TRUE
)
ON CONFLICT DO NOTHING;