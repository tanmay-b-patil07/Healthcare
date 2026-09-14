-- ============================================================
-- GENERATE SAMPLE DONOR MATCHES
-- DEVELOPMENT / TESTING ONLY
-- ============================================================

INSERT INTO donor_matches (
    request_id,
    donor_id,
    distance_km,
    compatibility_score,
    availability_score,
    urgency_score,
    total_score,
    status
)
SELECT
    br.id AS request_id,

    nearby.donor_id,

    nearby.distance_km,

    -- Blood-group compatibility
    100.00 AS compatibility_score,

    -- Donor is available
    100.00 AS availability_score,

    -- Critical request
    100.00 AS urgency_score,

    -- Initial simple score
    100.00 AS total_score,

    'NOTIFIED' AS status

FROM blood_requests br

CROSS JOIN LATERAL find_nearby_donors(
    ST_Y(br.location::geometry),
    ST_X(br.location::geometry),
    10,
    br.blood_group
) nearby

WHERE br.status = 'REQUESTED'

ON CONFLICT (request_id, donor_id)
DO UPDATE SET
    distance_km = EXCLUDED.distance_km,
    compatibility_score = EXCLUDED.compatibility_score,
    availability_score = EXCLUDED.availability_score,
    urgency_score = EXCLUDED.urgency_score,
    total_score = EXCLUDED.total_score,
    status = EXCLUDED.status;