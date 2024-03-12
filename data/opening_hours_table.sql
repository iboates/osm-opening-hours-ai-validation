DROP TABLE IF EXISTS opening_hours;
CREATE TABLE opening_hours (
    id SERIAL PRIMARY KEY,
    node_id BIGINT NOT NULL,
    name TEXT,
    day_of_week INTEGER NOT NULL, -- 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    open_time TIME NOT NULL, -- Store only the time component
    close_time TIME NOT NULL, -- Store only the time component, can be after midnight
    geom GEOMETRY(Point, 4326) NOT NULL,
    CONSTRAINT chk_day_of_week CHECK (day_of_week >= 0 AND day_of_week <= 6)
);
