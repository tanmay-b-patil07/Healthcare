-- ============================================================
-- FIND NEARBY AVAILABLE DONORS
-- ============================================================

CREATE OR REPLACE FUNCTION find_nearby_donors(
    request_latitude DOUBLE PRECISION,
    request_longitude DOUBLE PRECISION,
    search_radius_km DOUBLE PRECISION,
    required_blood_group blood_group
)
RETURNS TABLE (
    donor_id BIGINT,
    user_id BIGINT,
    donor_blood_group blood_group,
    distance_km DOUBLE PRECISION
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        d.id AS donor_id,
        d.user_id,
        d.blood_group AS donor_blood_group,

        ST_Distance(
            d.location,
            ST_SetSRID(
                ST_MakePoint(
                    request_longitude,
                    request_latitude
                ),
                4326
            )::geography
        ) / 1000.0 AS distance_km

    FROM donors d

    WHERE d.is_available = TRUE

      AND d.blood_group = required_blood_group

      AND d.location IS NOT NULL

      AND ST_DWithin(
          d.location,
          ST_SetSRID(
              ST_MakePoint(
                  request_longitude,
                  request_latitude
              ),
              4326
          )::geography,
          search_radius_km * 1000
      )

    ORDER BY distance_km;
$$;