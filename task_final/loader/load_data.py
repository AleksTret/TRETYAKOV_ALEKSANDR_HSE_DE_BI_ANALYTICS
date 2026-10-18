import os
import glob
import time
import io
import psycopg2
import pyarrow.parquet as pq

DB_HOST = os.getenv("POSTGRES_HOST", "postgres_project")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "nyc_taxi")
DB_USER = os.getenv("POSTGRES_USER", "taxi_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "taxi_pass")

TAXI_TYPES = {
    "yellow": "yellow_trips",
    "green": "green_trips",
    "fhv": "fhv_trips",
    "fhvhv": "hvfhv_trips",
}
MONTHS = ["2024-01", "2024-04", "2024-07", "2024-10"]


def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


def is_table_empty(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT EXISTS (SELECT 1 FROM {table_name} LIMIT 1)")
        return not cur.fetchone()[0]


def get_db_columns(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position", (table_name,)
        )
        return [r[0] for r in cur.fetchall()]


def load_parquet_append(filepath, table_name, conn, chunk_size=200_000):
    pf = pq.ParquetFile(filepath)
    total = pf.metadata.num_rows
    loaded = 0
    db_cols = get_db_columns(conn, table_name)

    for batch in pf.iter_batches(batch_size=chunk_size):
        df = batch.to_pandas()
        df.columns = [c.lower() for c in df.columns]
        keep = [c for c in df.columns if c in db_cols]
        df = df[keep]

        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False, na_rep='')
        buf.seek(0)

        cols_str = ",".join(f'"{c}"' for c in keep)
        with conn.cursor() as cur:
            cur.copy_expert(
                f"COPY {table_name} ({cols_str}) FROM STDIN "
                f"WITH (FORMAT CSV, NULL '')", buf
            )
        conn.commit()
        loaded += len(df)
        print(f"    {table_name}: {loaded:,}/{total:,}", flush=True)


def main():
    print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME}", flush=True)
    conn = None
    
    # 1. Подключение
    for attempt in range(30):
        try:
            conn = get_conn()
            print("Postgres is ready!", flush=True)
            break
        except Exception as e:
            print(f"Waiting for Postgres... ({attempt + 1}/30): {e}", flush=True)
            time.sleep(2)
    if conn is None:
        raise RuntimeError("Postgres did not become ready in time")

    # 2. Загрузка справочника зон
    if is_table_empty(conn, "taxi_zones"):
        print("Processing taxi_zones...", flush=True)
        with open("/data/taxi_zone_lookup.csv", "r", encoding="utf-8") as f:
            with conn.cursor() as cur:
                cur.copy_expert("COPY taxi_zones FROM STDIN WITH CSV HEADER", f)
        conn.commit()
        print("  Finished taxi_zones", flush=True)
    else:
        print("Skipping taxi_zones: already has data", flush=True)

    # 3. Загрузка поездок
    for taxi_type, table_name in TAXI_TYPES.items():
        if not is_table_empty(conn, table_name):
            print(f"Skipping {table_name}: already has data", flush=True)
            continue

        print(f"Processing {table_name}...", flush=True)
        for month in MONTHS:
            pattern = f"/data/{taxi_type}_tripdata_{month}.parquet"
            files = glob.glob(pattern)
            if not files:
                print(f"  WARNING: no file for {pattern}", flush=True)
                continue
            filepath = files[0]
            print(f"  Loading {filepath} -> {table_name}...", flush=True)
            load_parquet_append(filepath, table_name, conn)
            print(f"  Finished {filepath}", flush=True)

    print("\n=== Final check ===", flush=True)
    for table_name in TAXI_TYPES.values():
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            print(f"{table_name}: {cur.fetchone()[0]:,} rows", flush=True)

    conn.close()
    print("\nDONE.", flush=True)


if __name__ == "__main__":
    main()