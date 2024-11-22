-- Function to get studio rating stats
CREATE OR REPLACE FUNCTION get_studio_rating_stats(p_studio_id uuid)
RETURNS TABLE (
    avg_rating NUMERIC,
    rating_count BIGINT
) SECURITY DEFINER AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(AVG(rating)::NUMERIC, 0) as avg_rating,
        COUNT(*) as rating_count
    FROM studio_ratings
    WHERE studio_id = p_studio_id;
END;
$$ LANGUAGE plpgsql;

-- Create studio_stats table
CREATE TABLE IF NOT EXISTS studio_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    studio_id UUID NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
    views INTEGER DEFAULT 0,
    phone_reveals INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(studio_id)
);

-- Create index on studio_id
CREATE INDEX IF NOT EXISTS idx_studio_stats_studio_id ON studio_stats(studio_id);

-- Function to get all studios with stats and ratings
CREATE OR REPLACE FUNCTION get_studios_with_stats()
RETURNS SETOF json SECURITY DEFINER AS $$
BEGIN
    RETURN QUERY
    SELECT 
        json_build_object(
            'id', s.id,
            'name', s.name,
            'description', s.description,
            'address', s.address,
            'phone_number', s.phone_number,
            'price', s.price,
            'created_at', s.created_at,
            'studio_stats', COALESCE(
                (
                    SELECT json_agg(st.*)
                    FROM studio_stats st
                    WHERE st.studio_id = s.id
                ),
                '[]'::json
            ),
            'avg_rating', COALESCE(AVG(r.rating)::NUMERIC, 0),
            'rating_count', COUNT(DISTINCT r.id)
        )
    FROM studios s
    LEFT JOIN studio_ratings r ON s.id = r.studio_id
    GROUP BY s.id, s.name, s.description, s.address, s.phone_number, s.price, s.created_at
    ORDER BY COALESCE(AVG(r.rating), 0) DESC, COUNT(DISTINCT r.id) DESC;
END;
$$ LANGUAGE plpgsql;
