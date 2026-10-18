CREATE TABLE IF NOT EXISTS yellow_trips (
    vendorid INTEGER,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count NUMERIC,
    trip_distance NUMERIC,
    ratecodeid NUMERIC,
    store_and_fwd_flag TEXT,
    pulocationid INTEGER,
    dolocationid INTEGER,
    payment_type NUMERIC,
    fare_amount NUMERIC,
    extra NUMERIC,
    mta_tax NUMERIC,
    tip_amount NUMERIC,
    tolls_amount NUMERIC,
    improvement_surcharge NUMERIC,
    total_amount NUMERIC,
    congestion_surcharge NUMERIC,
    airport_fee NUMERIC,
    cbd_congestion_fee NUMERIC,
    request_source TEXT
);

CREATE TABLE IF NOT EXISTS green_trips (
    vendorid INTEGER,
    lpep_pickup_datetime TIMESTAMP,
    lpep_dropoff_datetime TIMESTAMP,
    store_and_fwd_flag TEXT,
    ratecodeid NUMERIC,
    pulocationid INTEGER,
    dolocationid INTEGER,
    passenger_count NUMERIC,
    trip_distance NUMERIC,
    fare_amount NUMERIC,
    extra NUMERIC,
    mta_tax NUMERIC,
    tip_amount NUMERIC,
    tolls_amount NUMERIC,
    ehail_fee NUMERIC,
    improvement_surcharge NUMERIC,
    total_amount NUMERIC,
    payment_type NUMERIC,
    trip_type NUMERIC,
    congestion_surcharge NUMERIC,
    cbd_congestion_fee NUMERIC,
    request_source TEXT
);

CREATE TABLE IF NOT EXISTS fhv_trips (
    dispatching_base_num TEXT,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    pulocationid INTEGER,
    dolocationid INTEGER,
    sr_flag NUMERIC,
    affiliated_base_number TEXT
);

CREATE TABLE IF NOT EXISTS hvfhv_trips (
    hvfhs_license_num TEXT,
    dispatching_base_num TEXT,
    originating_base_num TEXT,
    request_datetime TIMESTAMP,
    on_scene_datetime TIMESTAMP,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    pulocationid INTEGER,
    dolocationid INTEGER,
    trip_miles NUMERIC,
    trip_time NUMERIC,
    base_passenger_fare NUMERIC,
    tolls NUMERIC,
    bcf NUMERIC,
    sales_tax NUMERIC,
    congestion_surcharge NUMERIC,
    airport_fee NUMERIC,
    tips NUMERIC,
    driver_pay NUMERIC,
    shared_request_flag TEXT,
    shared_match_flag TEXT,
    access_a_ride_flag TEXT,
    wav_request_flag TEXT,
    wav_match_flag TEXT,
    cbd_congestion_fee NUMERIC
);

CREATE TABLE IF NOT EXISTS taxi_zones (
    locationid INTEGER PRIMARY KEY,
    borough TEXT,
    zone TEXT,
    service_zone TEXT
);

CREATE INDEX IF NOT EXISTS idx_yellow_pickup ON yellow_trips (tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_green_pickup ON green_trips (lpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_fhv_pickup ON fhv_trips (pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_hvfhv_pickup ON hvfhv_trips (pickup_datetime);

CREATE INDEX IF NOT EXISTS idx_yellow_pu ON yellow_trips (pulocationid);
CREATE INDEX IF NOT EXISTS idx_green_pu ON green_trips (pulocationid);
CREATE INDEX IF NOT EXISTS idx_fhv_pu ON fhv_trips (pulocationid);
CREATE INDEX IF NOT EXISTS idx_hvfhv_pu ON hvfhv_trips (pulocationid);