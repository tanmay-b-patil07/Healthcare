DO $$
BEGIN

    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'user_role'
    ) THEN
        CREATE TYPE user_role AS ENUM (
            'DONOR',
            'HOSPITAL',
            'BLOOD_BANK',
            'REQUESTER',
            'ADMIN'
        );
    END IF;


    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'blood_group'
    ) THEN
        CREATE TYPE blood_group AS ENUM (
            'A_POSITIVE',
            'A_NEGATIVE',
            'B_POSITIVE',
            'B_NEGATIVE',
            'AB_POSITIVE',
            'AB_NEGATIVE',
            'O_POSITIVE',
            'O_NEGATIVE'
        );
    END IF;


    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'urgency_level'
    ) THEN
        CREATE TYPE urgency_level AS ENUM (
            'LOW',
            'MEDIUM',
            'HIGH',
            'CRITICAL'
        );
    END IF;


    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'request_status'
    ) THEN
        CREATE TYPE request_status AS ENUM (
            'REQUESTED',
            'DONORS_NOTIFIED',
            'DONOR_RESPONDED',
            'PARTIALLY_FULFILLED',
            'FULFILLED',
            'CANCELLED'
        );
    END IF;


    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'donor_match_status'
    ) THEN
        CREATE TYPE donor_match_status AS ENUM (
            'PENDING',
            'NOTIFIED',
            'ACCEPTED',
            'DECLINED',
            'EXPIRED'
        );
    END IF;


    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'notification_status'
    ) THEN
        CREATE TYPE notification_status AS ENUM (
            'PENDING',
            'SENT',
            'DELIVERED',
            'FAILED',
            'READ'
        );
    END IF;

END
$$;