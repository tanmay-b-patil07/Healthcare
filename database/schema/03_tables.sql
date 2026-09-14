-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,

    name VARCHAR(150) NOT NULL,

    email VARCHAR(255) UNIQUE,

    phone VARCHAR(20) UNIQUE NOT NULL,

    password_hash TEXT NOT NULL,

    role user_role NOT NULL,

    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- DONORS
-- ============================================================

CREATE TABLE IF NOT EXISTS donors (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL UNIQUE
        REFERENCES users(id) ON DELETE CASCADE,

    blood_group blood_group NOT NULL,

    date_of_birth DATE,

    location GEOGRAPHY(POINT, 4326),

    address TEXT,

    is_available BOOLEAN NOT NULL DEFAULT FALSE,

    last_donation_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- HOSPITALS
-- ============================================================

CREATE TABLE IF NOT EXISTS hospitals (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL UNIQUE
        REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,

    address TEXT NOT NULL,

    location GEOGRAPHY(POINT, 4326),

    verification_status BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- BLOOD BANKS
-- ============================================================

CREATE TABLE IF NOT EXISTS blood_banks (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL UNIQUE
        REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,

    address TEXT NOT NULL,

    location GEOGRAPHY(POINT, 4326),

    verification_status BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- BLOOD INVENTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS blood_inventory (
    id BIGSERIAL PRIMARY KEY,

    blood_bank_id BIGINT NOT NULL
        REFERENCES blood_banks(id) ON DELETE CASCADE,

    blood_group blood_group NOT NULL,

    available_units INTEGER NOT NULL DEFAULT 0,

    reserved_units INTEGER NOT NULL DEFAULT 0,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (blood_bank_id, blood_group),

    CHECK (available_units >= 0),

    CHECK (reserved_units >= 0)
);


-- ============================================================
-- BLOOD REQUESTS
-- ============================================================

CREATE TABLE IF NOT EXISTS blood_requests (
    id BIGSERIAL PRIMARY KEY,

    requester_id BIGINT NOT NULL
        REFERENCES users(id),

    hospital_id BIGINT
        REFERENCES hospitals(id),

    blood_group blood_group NOT NULL,

    units_required INTEGER NOT NULL,

    units_fulfilled INTEGER NOT NULL DEFAULT 0,

    urgency urgency_level NOT NULL,

    status request_status NOT NULL DEFAULT 'REQUESTED',

    location GEOGRAPHY(POINT, 4326),

    address TEXT,

    required_by TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (units_required > 0),

    CHECK (units_fulfilled >= 0),

    CHECK (units_fulfilled <= units_required)
);


-- ============================================================
-- DONOR MATCHES
-- ============================================================

CREATE TABLE IF NOT EXISTS donor_matches (
    id BIGSERIAL PRIMARY KEY,

    request_id BIGINT NOT NULL
        REFERENCES blood_requests(id) ON DELETE CASCADE,

    donor_id BIGINT NOT NULL
        REFERENCES donors(id) ON DELETE CASCADE,

    distance_km NUMERIC(10, 2),

    compatibility_score NUMERIC(5, 2) NOT NULL DEFAULT 0,

    availability_score NUMERIC(5, 2) NOT NULL DEFAULT 0,

    urgency_score NUMERIC(5, 2) NOT NULL DEFAULT 0,

    total_score NUMERIC(6, 2) NOT NULL DEFAULT 0,

    status donor_match_status NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (request_id, donor_id)
);


-- ============================================================
-- DONATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS donations (
    id BIGSERIAL PRIMARY KEY,

    donor_id BIGINT NOT NULL
        REFERENCES donors(id),

    request_id BIGINT
        REFERENCES blood_requests(id),

    blood_bank_id BIGINT
        REFERENCES blood_banks(id),

    blood_group blood_group NOT NULL,

    units INTEGER NOT NULL,

    donated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (units > 0)
);


-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    request_id BIGINT
        REFERENCES blood_requests(id) ON DELETE CASCADE,

    type VARCHAR(50) NOT NULL,

    title VARCHAR(255) NOT NULL,

    message TEXT NOT NULL,

    channel VARCHAR(30) NOT NULL,

    status notification_status NOT NULL DEFAULT 'PENDING',

    sent_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- AUDIT LOGS
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT
        REFERENCES users(id) ON DELETE SET NULL,

    action VARCHAR(100) NOT NULL,

    entity_type VARCHAR(100),

    entity_id BIGINT,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);