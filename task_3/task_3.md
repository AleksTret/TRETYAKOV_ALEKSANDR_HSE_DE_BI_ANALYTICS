# Домашнее задание 2 по курсу «BI-аналитика и визуализация данных»

**Выполнил - Третьяков Александр Юрьевич**

# Решение

## Сформулируйте 10 аналитических вопросов, которые будет решать дашборд. Перечислите их ниже:

### Про рейсы и маршруты
1. **Топ-10 самых загруженных маршрутов** по количеству рейсов — куда и откуда летают чаще всего?
2. **Топ-10 аэропортов по количеству вылетов и прилётов** — какие хабы самые загруженные?
3. **Динамика количества рейсов по дням** — как меняется интенсивность полётов в течение месяца?

### Про пунктуальность
4. **Доля задержанных и отменённых рейсов** по дням — какая ситуация с пунктуальностью?
5. **Средняя задержка по аэропортам** — где чаще всего задерживают вылеты?
6. **Распределение отмен по маршрутам** — какие направления страдают больше всего?

### Про загрузку и самолёты
7. **Загрузка рейсов** (число занятых мест / всего мест в самолёте) — какие рейсы заполнены лучше?
8. **Распределение мест по классам** (Economy / Comfort / Business) — какой класс популярнее?

### Про выручку и бронирования
9. **Общая выручка по дням** — как меняется доход?
10. **Топ-10 маршрутов по выручке** — какие направления самые прибыльные?

##	Подготовьте данные для решения поставленных вопросов, не менее 2-х виртуальных датасетов (заранее продумайте общие фильтры). Добавьте SQL-запросы, которые формируют ваши датасеты:


- **flights_analysis — операционные рейсы.**

- **bookings_revenue — коммерческие брони.**

- **load_factor — загрузка и классы.**

###  Датасет 1: `flights_analysis` — для вопросов 1, 2, 3, 4, 5, 6
**Базовая информация о рейсах с расшифровкой:**
- `flight_id`, `flight_no`
- `scheduled_departure`, `scheduled_arrival` (даты)
- `departure_airport`, `departure_city`, `arrival_airport`, `arrival_city`
- `status`, `aircraft_code`
- `actual_departure`, `actual_arrival`
- Вычисляемые поля: `delay_minutes`, `is_delayed`, `is_cancelled`, `flight_date`

```sql
SELECT
    f.flight_id,
    f.flight_no,
    f.scheduled_departure,
    f.scheduled_departure::date                                   AS flight_date,
    f.scheduled_arrival,
    f.departure_airport,
    dep.airport_name                                              AS departure_airport_name,
    dep.city                                                      AS departure_city,
    f.arrival_airport,
    arr.airport_name                                              AS arrival_airport_name,
    arr.city                                                      AS arrival_city,
    f.status,
    f.aircraft_code,
    ac.model                                                      AS aircraft_model,
    f.actual_departure,
    f.actual_arrival,

    -- Задержка вылета в минутах
    CASE
        WHEN f.actual_departure IS NOT NULL
        THEN EXTRACT(EPOCH FROM (f.actual_departure - f.scheduled_departure)) / 60
        ELSE NULL
    END                                                           AS departure_delay_minutes,

    -- Флаг задержки
    CASE
        WHEN f.actual_departure IS NOT NULL
         AND f.actual_departure > f.scheduled_departure
        THEN 1 ELSE 0
    END                                                           AS is_delayed,

    -- Флаг отмены
    CASE WHEN f.status = 'Cancelled' THEN 1 ELSE 0 END            AS is_cancelled,

    -- СИММЕТРИЧНЫЙ маршрут (не зависит от направления)
    LEAST(dep.city, arr.city) || ' ↔ ' || GREATEST(dep.city, arr.city) AS route

FROM bookings.flights f
LEFT JOIN bookings.airports dep ON f.departure_airport = dep.airport_code
LEFT JOIN bookings.airports arr ON f.arrival_airport = arr.airport_code
LEFT JOIN bookings.aircrafts ac ON f.aircraft_code = ac.aircraft_code;
```

### Датасет 2: `bookings_revenue` — для вопросов 9, 10
**Бронирования и выручка:**
- `book_ref`, `book_date`, `total_amount`
- `book_date_day`, `book_date_month`
- Связка с маршрутом (через тикеты и перелёты)
- Метрики: `total_revenue`, `avg_booking_amount`

```sql
SELECT
    b.book_ref,
    b.book_date,
    b.book_date::date                                       AS book_date_day,
    DATE_TRUNC('week', b.book_date)::date                   AS book_date_week,
    DATE_TRUNC('month', b.book_date)::date                  AS book_date_month,
    b.total_amount,

    t.ticket_no,
    t.passenger_id,
    t.passenger_name,

    tf.flight_id,
    tf.fare_conditions,
    tf.amount                                               AS ticket_flight_amount,

    f.flight_no,
    f.scheduled_departure,
    f.scheduled_departure::date                             AS flight_date,
    f.departure_airport,
    dep.city                                                AS departure_city,
    f.arrival_airport,
    arr.city                                                AS arrival_city,
    dep.city || ' → ' || arr.city                           AS route

FROM bookings.bookings b
JOIN bookings.tickets t        ON b.book_ref = t.book_ref
JOIN bookings.ticket_flights tf ON t.ticket_no = tf.ticket_no
JOIN bookings.flights f        ON tf.flight_id = f.flight_id
LEFT JOIN bookings.airports dep ON f.departure_airport = dep.airport_code
LEFT JOIN bookings.airports arr ON f.arrival_airport = arr.airport_code;
```


### Датасет 3: `load_factor` — для вопросов 7, 8
**Загрузка рейсов и классы:**
- `flight_id`, `aircraft_code`, `scheduled_departure`
- `seats_total` — всего мест в самолёте
- `seats_sold` — продано мест
- `load_factor` = seats_sold / seats_total
- `fare_conditions` — класс обслуживания
- `seats_by_class` — распределение мест по классам

```sql
WITH seats_total AS (
    -- Всего мест в самолёте по классам
    SELECT
        aircraft_code,
        fare_conditions,
        COUNT(*) AS total_seats
    FROM bookings.seats
    GROUP BY aircraft_code, fare_conditions
),
seats_sold AS (
    -- Продано мест (по посадочным талонам)
    SELECT
        bp.flight_id,
        s.fare_conditions,
        COUNT(*) AS sold_seats
    FROM bookings.boarding_passes bp
    JOIN bookings.seats s
        ON s.aircraft_code = (
            SELECT aircraft_code FROM bookings.flights WHERE flight_id = bp.flight_id
        )
       AND s.seat_no = bp.seat_no
    GROUP BY bp.flight_id, s.fare_conditions
)
SELECT
    f.flight_id,
    f.flight_no,
    f.scheduled_departure,
    f.scheduled_departure::date                AS flight_date,
    f.departure_airport,
    dep.city                                   AS departure_city,
    f.arrival_airport,
    arr.city                                   AS arrival_city,
    dep.city || ' → ' || arr.city              AS route,
    f.aircraft_code,
    ac.model                                   AS aircraft_model,
    f.status,

    st.fare_conditions,
    st.total_seats,
    COALESCE(ss.sold_seats, 0)                 AS sold_seats,
    ROUND(
        COALESCE(ss.sold_seats, 0)::numeric / NULLIF(st.total_seats, 0) * 100,
        2
    )                                          AS load_factor_pct

FROM bookings.flights f
LEFT JOIN bookings.airports dep       ON f.departure_airport = dep.airport_code
LEFT JOIN bookings.airports arr       ON f.arrival_airport = arr.airport_code
LEFT JOIN bookings.aircrafts ac       ON f.aircraft_code = ac.aircraft_code
JOIN seats_total st                   ON st.aircraft_code = f.aircraft_code
LEFT JOIN seats_sold ss               ON ss.flight_id = f.flight_id
                                     AND ss.fare_conditions = st.fare_conditions;
```


##  Metrics для датасетов

### Датасет 1: `flights_analysis`

| Metric Key | Label | SQL Expression | Описание |
|---|---|---|---|
| `total_flights` | Всего рейсов | `COUNT(*)` | Общее количество рейсов |
| `delayed_flights` | Задержанных | `SUM(is_delayed)` | Число рейсов с задержкой вылета |
| `cancelled_flights` | Отменённых | `SUM(is_cancelled)` | Число отменённых рейсов |
| `pct_delayed` | % задержанных | `SUM(is_delayed) * 100.0 / NULLIF(COUNT(*), 0)` | Доля задержанных рейсов |
| `avg_delay_minutes` | Средняя задержка (мин) | `AVG(departure_delay_minutes)` | Средняя задержка вылета |

<img src="./assets/2026-09-24 102033.jpg" width="700">

---

### Датасет 2: `bookings_revenue`


| Metric Key | Label | SQL Expression | Описание |
|---|---|---|---|
| `total_revenue` | Выручка | `SUM(total_amount)` | Общая сумма бронирований |
| `bookings_count` | Бронирований | `COUNT(DISTINCT book_ref)` | Число уникальных бронирований |
| `avg_booking_amount` | Средний чек | `AVG(total_amount)` | Средняя стоимость бронирования |
| `tickets_count` | Билетов | `COUNT(DISTINCT ticket_no)` | Число уникальных билетов |
| `ticket_flights_revenue` | Выручка перелётов | `SUM(ticket_flight_amount)` | Сумма по перелётам |

<img src="./assets/2026-09-24 101506.jpg" width="700">

---

### Датасет 3: `load_factor`


| Metric Key | Label | SQL Expression | Описание |
|---|---|---|---|
| `avg_load_factor` | Средняя загрузка (%) | `AVG(load_factor_pct)` | Средний процент загрузки |
| `total_seats` | Всего мест | `SUM(total_seats)` | Общее число мест |
| `sold_seats` | Продано мест | `SUM(sold_seats)` | Общее число проданных мест |
| `flights_count` | Рейсов | `COUNT(DISTINCT flight_id)` | Число рейсов |

<img src="./assets/2026-09-24 101505.jpg" width="700">

---

## Calculated Columns

**Дополнительные Calculated Columns не нужны — всё уже есть в датасетах.**

### Датасет flights_analysis:
Вычисления реализованы на уровне SQL-виртуального датасета:

   - `flight_date = scheduled_departure::date` — дата рейса

   - `departure_delay_minutes = EXTRACT(EPOCH FROM (actual_departure - scheduled_departure)) / 60` — задержка вылета в минутах

   - `is_delayed = CASE WHEN actual_departure > scheduled_departure THEN 1 ELSE 0 END` — флаг задержки

   - `is_cancelled = CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END` — флаг отмены

   - `route = dep.city || ' → ' || arr.city` — маршрут «город → город»

### Датасет bookings_revenue:
   - `book_date_day = book_date::date` — день бронирования
   - `book_date_week = DATE_TRUNC('week', book_date)::date` — неделя
   - `book_date_month = DATE_TRUNC('month', book_date)::date` — месяц

### Датасет load_factor:
   - `load_factor_pct = ROUND(sold_seats::numeric / NULLIF(total_seats, 0) * 100, 2)` — процент загрузки


##	Постройте визуализации необходимые для решения поставленных вопросов (заранее схематически продумайте их расположение на дашборде, чтобы мог получиться связный рассказ на их основе). 
## Из полученных визуализаций создайте дашборд, чтобы мог получиться связный дата-сторителлинг. Продемонстрируйте умение использовать Layout elements, скриншотами приведите примеры:

<img src="./assets/2026-09-24 144544.jpg" width="700">


<img src="./assets/2026-09-24 145057.jpg" width="700">


<img src="./assets/2026-09-24 145137.jpg" width="700">


<img src="./assets/2026-09-24 145212.jpg" width="700">

## Продемонстрируйте умение пользоваться «локальными» фильтрами. Покажите хотя бы 1 визуализацию с локальным фильтром, опишите в формате:

Визуализация: «04. Пунктуальность по дням»

Описание фильтра:
1. flight_date < '2017-08-15' — обрезает график до реальных данных
2. status NOT IN ('Scheduled') — оставляет только завершённые рейсы

<img src="./assets/2026-09-24 153514.jpg" width="700">

Визуализация: «06. Отмены по маршрутам»

Описание фильтра:
is_cancelled = 1

<img src="./assets/2026-09-24 153726.jpg" width="700">


## Добавьте на дашборд не менее 1 фильтра каждого типа (Value, Numerical range, Time range, Time column, Time grain). 

#### Фильтр 1: «Период рейсов»
- Тип фильтра = Time range
- Поле фильтра = scheduled_departure
- Описание: позволяет выбрать период анализа (Last 7/30/90 days, custom range).
- Дополнительные настройки: Scoping — действует на чарты 03, 04, 09.

<img src="./assets/2026-09-24 165913.jpg" width="700">
<img src="./assets/2026-09-24 170006.jpg" width="700">


#### Фильтр 2: «Город вылета»
- Тип фильтра = Value
- Поле фильтра = departure_city
- Описание: выбор одного или нескольких городов вылета.
- Дополнительные настройки: multiple values ON. Scoping — чарты 01, 02, 05, 06.

<img src="./assets/2026-09-24 170152.jpg" width="700">
<img src="./assets/2026-09-24 170213.jpg" width="700">

#### Фильтр 3: «Средняя задержка»
- Тип фильтра = Numerical range
- Поле фильтра = departure_delay_minutes
- Описание: диапазон средней задержки в минутах (slider + inputs).
- Дополнительные настройки: Scoping — только чарт 05.

<img src="./assets/2026-09-24 170312.jpg" width="700">
<img src="./assets/2026-09-24 170334.jpg" width="700">

#### Фильтр 4: «Гранулярность»
- Тип фильтра = Time grain
- Поле фильтра = flight_date
- Описание: выбор гранулярности времени (Day/Week/Month).
- Дополнительные настройки: Scoping — чарты 03, 04, 09.


<img src="./assets/2026-09-24 170430.jpg" width="700">
<img src="./assets/2026-09-24 170452.jpg" width="700">


#### Фильтр 5: «Временная колонка»
- Тип фильтра = Time column
- Поле фильтра = scheduled_departure
- Описание: выбор временнóй колонки для анализа (scheduled_departure / actual_departure).
- Дополнительные настройки: Scoping — чарты 03, 04.


<img src="./assets/2026-09-24 170513.jpg" width="700">
<img src="./assets/2026-09-24 170534.png" width="700">

## Сделайте не менее 5 «экспериментов» (суммарно) с дополнительными настройками для любых имеющихся фильтров

#### Эксперимент 1. Filter has default value
В фильтре Город вылета → включить Filter has default value.

Что делает: при открытии дашборда фильтр сразу применяет заданное значение.

Полезно: для дашбордов, которые всегда открываются в определённом состоянии.

<img src="./assets/2026-09-26 181615.jpg" width="700">

#### Эксперимент 2. Filter value is required
В фильтре Период рейсов → включить Filter value is required.

Что делает: без выбора значения фильтр не даст применить изменения.

Полезно: для критичных фильтров, где пропуск значения исказит данные.

<img src="./assets/2026-09-26 182054.jpg" width="700">

#### Эксперимент 3. Values are dependent on other filters
В фильтре «Средняя задержка» → Filter Configuration → включить Values are dependent on other filters.

Что делает: значения фильтра пересчитываются в зависимости от значений других фильтров дашборда.

Полезно: когда фильтры взаимосвязаны — например, сначала выбирают регион, а потом диапазон задержек только по этому региону.

<img src="./assets/2026-09-26 182806.jpg" width="700">

#### Эксперимент 4. Pre-filter available values
В фильтре «Город вылета» → Filter Configuration → включить Pre-filter available values.

Что делает: ограничивает список доступных значений фильтра только теми, что реально встречаются в данных после применения других фильтров.

Полезно: убирает из выпадающего списка «мёртвые» значения, которые не дадут результата.

<img src="./assets/2026-09-26 182938.jpg" width="700">

#### Эксперимент 5. Sort filter values
В фильтре «Временная колонка» → Filter Configuration → включить Sort filter values.

Что делает: сортирует список значений фильтра по алфавиту — стабильный порядок вместо «порядка появления» в датасете.

Полезно: когда в фильтре много значений (10+), и пользователю нужно быстро найти нужное.

<img src="./assets/2026-09-26 183055.jpg" width="700">

## Продемонстрируйте умение пользоваться разделом Scoping. Сделайте 2 скриншота действия разных фильтров, где будет видно, что часть визуализаций принимает данный фильтр, а часть нет. 

#### Пример 1: Фильтр «Средняя задержка» (вкладка «Пунктуальность»)

Описание действия фильтра:
Фильтр Numerical range по departure_delay_minutes.
В Scoping оставлен только чарт «05. Средняя задержка по аэропортам».
При изменении диапазона этот чарт перестраивается (в списке остаются
только аэропорты с задержкой в выбранном диапазоне).
Чарты «04. Пунктуальность по дням» и «06. Отмены по маршрутам»
не принимают этот фильтр и продолжают показывать полные данные.

<img src="./assets/2026-09-26 183950.jpg" width="700">

<img src="./assets/2026-09-26 184016.jpg" width="700">

#### Пример 2: Фильтр «Город вылета» (вкладка «Обзор рейсов»)

Описание действия фильтра:
Фильтр Value по departure_city = 'Москва'.
В Scoping включены чарты «01. Топ-10 маршрутов по рейсам»
и «02. Топ-10 аэропортов по вылетам», но НЕ включён
«03. Динамика рейсов по дням».
Чарты 01 и 02 перестраиваются (показывают только московские рейсы).
Чарт 03 продолжает показывать все рейсы за весь период.

<img src="./assets/2026-09-26 184232.jpg" width="700">

<img src="./assets/2026-09-26 184315.jpg" width="700">



## Продемонстрируйте на 1 визуализации умение пользоваться drill to detail с помощью 2-х примеров. 

#### Пример 1: «02. Топ-10 аэропортов по вылетам»

Описание: вызов Drill to detail через меню «...» чарта. Открылась
таблица с сырыми данными: каждая строка — один рейс. Видны колонки
flight_date, departure_airport, departure_city, arrival_airport.
Глобальные фильтры сброшены — данные за весь период.

<img src="./assets/2026-09-26 185749.jpg" width="700">

#### Пример 2: «02. Топ-10 аэропортов по вылетам»

Применённый фильтр: «Город вылета = Архангельск»
Описание: тот же Drill to detail, но таблица отфильтрована —
показаны только рейсы с вылетом из Москвы.

<img src="./assets/2026-09-26 185956.jpg" width="700">

##	 Продемонстрируйте на 1 визуализации умение пользоваться drill by в виде 3-х скриншотов.

#### Пример 1: «02. Топ-10 аэропортов по вылетам»
Описание: исходная визуализация до drill by.

<img src="./assets/2026-09-26 190234.jpg" width="700">

#### Пример 2: «02. Топ-10 аэропортов по вылетам»

Сегмент для исследования: «Домодедово → города прилёта»
Описание: правый клик на «Домодедово», Drill by → arrival_city.
Чарт  показывает топ городов, куда летают из Домодедово.

<img src="./assets/2026-09-26 190310.jpg" width="700">


#### Пример 3: «02. Топ-10 аэропортов по вылетам»

Сегмент для исследования: «Шереметьево → модели самолётов»
Описание: правый клик на «Шереметьево», Drill by → aircraft_model.
Чарт показывает модели самолётов, летающих в Шереметьево.

<img src="./assets/2026-09-26 190539.jpg" width="700">

## Вернитесь к поставленным аналитическим вопросам в пункте 3 и продемонстрируйте элементы дашборда для нахождения ответа на них. 


#### Вопрос 1. Топ-10 самых загруженных маршрутов по количеству рейсов

<img src="./assets/2026-09-26 191109.jpg" width="700">

- Dataset: flights_analysis
- Метрики: Всего рейсов (COUNT(*))
- Измерения: route (симметричный маршрут «город ↔ город»)
- Локальные фильтры: нет
- Глобальные фильтры: «Город вылета», «Период рейсов» (при необходимости)

---

#### Вопрос 2. Топ-10 аэропортов по количеству вылетов

<img src="./assets/2026-09-26 191158.jpg" width="700">

- Dataset: flights_analysis
- Метрики: Всего рейсов (COUNT(*))
- Измерения: departure_airport_name
- Локальные фильтры: нет
- Глобальные фильтры: «Город вылета»

---

#### Вопрос 3. Динамика количества рейсов по дням

<img src="./assets/2026-09-26 191324.jpg" width="700">

- Dataset: flights_analysis
- Метрики: Всего рейсов (COUNT(*))
- Измерения: flight_date (Time Grain = Day)
- Локальные фильтры: нет
- Глобальные фильтры: «Период рейсов», «Гранулярность»

---

#### Вопрос 4. Доля задержанных и отменённых рейсов по дням

<img src="./assets/2026-09-26 191402.jpg" width="700">

- Dataset: flights_analysis
- Метрики: % задержанных (SUM(is_delayed) * 100.0 / COUNT(*))
- Измерения: flight_date
- Локальные фильтры: status NOT IN ('Scheduled'), flight_date < '2017-08-15'
- Глобальные фильтры: «Период рейсов»

---

#### Вопрос 5. Средняя задержка по аэропортам

<img src="./assets/2026-09-26 191418.jpg" width="700">

- Dataset: flights_analysis
- Метрики: Средняя задержка (мин) (AVG(departure_delay_minutes))
- Измерения: departure_airport_name
- Локальные фильтры: status NOT IN ('Scheduled')
- Глобальные фильтры: «Средняя задержка» (Numerical range)

---

#### Вопрос 6. Распределение отмен по маршрутам

<img src="./assets/2026-09-26 191435.jpg" width="700">

- Dataset: flights_analysis
- Метрики: Отменённых (SUM(is_cancelled))
- Измерения: route
- Локальные фильтры: is_cancelled = 1
- Глобальные фильтры: нет (в Scoping не участвует)

---

#### Вопрос 7. Загрузка рейсов по маршрутам

<img src="./assets/2026-09-26 191604.jpg" width="700">

- Dataset: load_factor
- Метрики: Средняя загрузка (%) (AVG(load_factor_pct))
- Измерения: route
- Локальные фильтры: нет
- Глобальные фильтры: нет (в Scoping не участвует)

---

#### Вопрос 8. Распределение мест по классам

<img src="./assets/2026-09-26 191620.jpg" width="700">

- Dataset: load_factor
- Метрики: Продано мест (SUM(sold_seats))
- Измерения: fare_conditions
- Локальные фильтры: нет
- Глобальные фильтры: нет

---

#### Вопрос 9. Общая выручка по дням

<img src="./assets/2026-09-26 191709.jpg" width="700">

- Dataset: bookings_revenue
- Метрики: Выручка (SUM(total_amount))
- Измерения: book_date_day
- Локальные фильтры: book_date < '2017-08-15'
- Глобальные фильтры: «Период рейсов»

---

#### Вопрос 10. Топ-10 маршрутов по выручке

<img src="./assets/2026-09-26 191724.jpg" width="700">

- Dataset: bookings_revenue
- Метрики: Выручка перелётов (SUM(ticket_flight_amount))
- Измерения: route
- Локальные фильтры: book_date < '2017-08-15'
- Глобальные фильтры: нет

## Опишите 2-3 интересные закономерности/ инсайта на основе проведенного исследования.

#### Закономерность 1: Длинные маршруты приносят основную выручку.
Топ-10 по выручке — все длинные рейсы (Москва ↔ Новосибирск,
Хабаровск, Южно-Сахалинск). По количеству рейсов они не в топ-10.
Вывод: длина маршрута влияет на выручку сильнее, чем частота.

#### Закономерность 2: 96% рейсов отклоняются от расписания,
но только 2.4% — существенно (> 15 минут).
Средняя задержка — 12 минут.
Вывод: данные фиксируют любое отклонение, реальная проблема
пунктуальности — у 2.4% рейсов.

#### Закономерность 3: региональные аэропорты задерживают больше
московских. Топ-10 по средней задержке — Ульяновск-Восточный,
Игнатьево, Липецк, Чульман — все региональные.
Московские хабы в топ-10 не попали.
Вывод: мелкие аэропорты хуже справляются с пунктуальностью.