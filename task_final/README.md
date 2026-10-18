# Данные проекта

## Источник
NYC Taxi & Limousine Commission (TLC) — официальный регулятор такси 
и ride-sharing в Нью-Йорке.

- **Официальная страница:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Формат:** Apache Parquet

## Период
Январь, апрель, июль, октябрь 2024 (4 сезона).

## Ссылки на Parquet-файлы

### Yellow Taxi
- https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-04.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-07.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-10.parquet

### Green Taxi
- https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-01.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-04.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-07.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-10.parquet

### FHV
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2024-01.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2024-04.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2024-07.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2024-10.parquet

### High Volume FHV
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2024-01.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2024-04.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2024-07.parquet
- https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2024-10.parquet

## Словари данных
- `Yellow_Taxi_Trip_Data_Data_Dictionary.xlsx`
- `Green_Taxi_Trip_Data_Data_Dictionary.xlsx`
- `FHV_Trip_Data_Data_Dictionary.xlsx`
- `HVFHV_Trip_Data_Data_Dictionary.xlsx`

## Ограничения
- Parquet-файлы (~2 ГБ) **не хранятся в Git** — их нужно скачать отдельно.

## Инструкция по запуску

### Шаг 1. Скачать данные

Скачайте 16 Parquet-файлов и 4 словаря по ссылкам из `data/README.md`.

Поместите их в папку `data/`:
```
data/
├── yellow_tripdata_2024-01.parquet
├── ... (все 16)
└── Yellow_Taxi_Trip_Data_Data_Dictionary.xlsx
```

### Шаг 2. Убедиться, что Superset запущен

Проект использует Docker-сеть `superset_default`, созданную Superset.

### Шаг 3. Запустить Postgres

```bash
cd ..\task_final
docker compose up -d postgres_project
```

**Что произойдёт:**
- Создастся volume `postgres_project_data`.
- Запустится контейнер `postgres_project` на порту **5433**.
- Автоматически выполнится `sql/init/01_create_tables.sql` — создадутся 4 таблицы.

**Проверка:**
```bash
docker exec -it postgres_project psql -U taxi_user -d nyc_taxi -c "\dt"
```

Ожидаемо: 4 таблицы (`yellow_trips`, `green_trips`, `fhv_trips`, `hvfhv_trips`).

### Шаг 4. Собрать Loader

```bash
cd ..\task_final\loader
docker compose build loader
```

**Если таймауты PyPI** — используйте VPN или зеркало.

### Шаг 5. Загрузить данные

```bash
docker compose run --rm loader
```

**Что произойдёт:**
- Loader подключится к `postgres_project`.
- Загрузит 16 Parquet-файлов в 4 таблицы.
- Выведет прогресс: `Loaded X rows. Total: Y`.

**Время:** 40–80 минут (High Volume FHV — самый объёмный).

**Проверка после загрузки:**
```bash
docker exec -it postgres_project psql -U taxi_user -d nyc_taxi -c "
SELECT 'yellow' AS type, COUNT(*) FROM yellow_trips
UNION ALL
SELECT 'green', COUNT(*) FROM green_trips
UNION ALL
SELECT 'fhv', COUNT(*) FROM fhv_trips
UNION ALL
SELECT 'hvfhv', COUNT(*) FROM hvfhv_trips;
"
```

Ожидаемо: ~100 млн строк суммарно.

### Шаг 6. Подключить к Superset

1. Откройте **http://localhost:8088** → логин `admin` / `admin`.
2. **Settings** → **Database Connections** → **+ Database**.
3. Заполните:
   - **Display Name:** `NYC Taxi Project`
   - **Host:** `postgres_project`
   - **Port:** `5432`
   - **Database:** `nyc_taxi`
   - **Username:** `taxi_user`
   - **Password:** `taxi_pass`
4. **Test Connection** → **Connect**.

### Шаг 7. Открыть дашборд

После импорта YAML дашборд появится в разделе **Dashboards**.

## Остановка проекта

```bash
docker compose stop
```

**Не используйте `down`** — потеряете volume с данными.

## Очистка (если нужно пересоздать)

```bash
docker compose down -v
docker compose up -d postgres_project
```

**`-v` удалит volume** — данные придётся загружать заново.

## Структура данных

| Таблица | Строк (примерно) | Поля |
|---|---|---|
| `yellow_trips` | ~13 млн | 20 |
| `green_trips` | ~280k | 22 |
| `fhv_trips` | ~4 млн | 7 |
| `hvfhv_trips` | ~80 млн | 25 |
| **Итого** | **~100 млн** | — |

## SQL-запросы

Исследовательские SQL-запросы — в папке `sql/queries/`:
- `q1_market_share.sql` — распределение рынка
- `q2_seasonal_dynamics.sql` — динамика по сезонам
- `q3_total_trips.sql` — общее число поездок
- `q4_hourly_weekly.sql` — распределение по часам/дням
- `q5_peak_hours.sql` — часы пик по сезонам
- `q6_popular_zones.sql` — популярные зоны
- `q7_geographic_specialization.sql` — география
- `q8_trip_duration.sql` — длительность поездок