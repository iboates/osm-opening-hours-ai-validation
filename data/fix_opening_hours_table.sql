CREATE TABLE if not exists fix_opening_hours (
    id SERIAL PRIMARY KEY,
    node_id BIGINT NOT NULL,
    name TEXT,
    opening_hours TEXT,
    chatgpt_analysis TEXT,
    chatgpt_proposal TEXT,
    chatgpt_extra TEXT,
    chatgpt_proposal_is_valid BOOLEAN,
    geom GEOMETRY(Point, 4326)
);
