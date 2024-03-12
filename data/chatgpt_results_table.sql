CREATE TABLE IF NOT EXISTS chatgpt_results (
    id SERIAL PRIMARY KEY,
    node_id BIGINT,
    name TEXT,
    street TEXT,
    number TEXT,
    amenity TEXT,
    opening_hours TEXT,
    website TEXT,
    geom GEOMETRY(Point, 4326),
    region TEXT,
    chatgpt_website_found BOOLEAN,
    chatgpt_website_url TEXT,
    chatgpt_opening_hours_found BOOLEAN,
    chatgpt_opening_hours_string TEXT,
    chatgpt_at_least_one_url_works BOOLEAN,
    chatgpt_response TEXT
);
