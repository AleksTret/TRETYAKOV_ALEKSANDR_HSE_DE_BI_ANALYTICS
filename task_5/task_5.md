# Домашнее задание 5 по курсу «BI-аналитика и визуализация данных»

**Выполнил - Третьяков Александр Юрьевич**

# Решение

## Блок 1

### 1)	Создайте нового пользователя с ролью Gamma, залогиньтесь под новым пользователем.

<img src="./assets/2026-10-12 151939.jpg" width="700">

<img src="./assets/2026-10-12 152203.jpg" width="700">

<img src="./assets/2026-10-12 152315.jpg" width="700">

<img src="./assets/2026-10-12 152340.jpg" width="700">

```text
login = test_gamma
pass = test_gamma_pass
```

### 2)	Создайте новую роль, в которой один из properties откроет доступ к тестовой БД examples. Добавьте эту роль второй (основная остается Gamma) для созданного ранее пользователя и залогиньтесь.

<img src="./assets/2026-10-12 152633.jpg" width="700">

<img src="./assets/2026-10-12 153527.jpg" width="700">

<img src="./assets/2026-10-12 153618.jpg" width="700">

<img src="./assets/2026-10-12 153730.jpg" width="700">

<img src="./assets/2026-10-12 153755.jpg" width="700">

### 3)	Создайте правило RLS в формате «поле»=’значение’. 
«скриншот заполненного окна с правилом»
«скриншот view query любого элемента дашборда, в котором оно применяется»

<img src="./assets/2026-10-12 160749.jpg" width="700">

<img src="./assets/2026-10-12 160618.jpg" width="700">

### 4)	Создайте второе правило RLS к тому же датасету в любом формате. Пусть оно объединяется с первым правилом RLS через AND.

<img src="./assets/2026-10-12 161022.jpg" width="700">

<img src="./assets/2026-10-12 162611.jpg" width="700">

<img src="./assets/2026-10-12 162706.jpg" width="700">

### 5)	Сделайте так, чтобы созданные ранее правила RLS, объединялись через OR. 

<img src="./assets/2026-10-12 162950.jpg" width="700">

<img src="./assets/2026-10-12 163107.jpg" width="700">

<img src="./assets/2026-10-12 163147.jpg" width="700">

### 6)	Создайте правило RLS, чтобы для всех ролей, кроме Alpha, действовало ваше правило (любого формата).

<img src="./assets/2026-10-12 164626.jpg" width="700">

<img src="./assets/2026-10-12 164802.jpg" width="700">

<img src="./assets/2026-10-12 164740.jpg" width="700">

```text
login = test_gamma
pass = test_gamma_pass
```

### 7)	В SQL-запросе вашего датасета добавьте шаблон Jinja, который бы полностью заменял функционал предыдущего пункта.

<img src="./assets/2026-10-12 165925.jpg" width="700">

<img src="./assets/2026-10-12 170234.jpg" width="700">

<img src="./assets/2026-10-12 170146.jpg" width="700">

### 8)	В SQL-запросе вашего датасета добавьте шаблон Jinja: если пользователь имеет роль Admin, в результирующий набор должно попадать реальное значение столбца <column_name> (любой столбец). Для всех остальных пользователей этот столбец также должен присутствовать в результате, но его значение должно быть NULL.

<img src="./assets/2026-10-12 171833.jpg" width="700">

<img src="./assets/2026-10-12 171936.jpg" width="700">

<img src="./assets/2026-10-12 172033.jpg" width="700">

### 9)	Реализуйте в Apache Superset на любом наборе данных одну визуализацию из списка: funnel chart, heatmap, waterfall chart, radar, treemap, scatter plot, tree chart, sankey chart.

<img src="./assets/2026-10-12 174130.jpg" width="700">

### 10)	Реализуйте в Apache Superset на любом наборе данных одну визуализацию из списка (без повторения п.9): funnel chart, heatmap, waterfall chart, radar, treemap, scatter plot, tree chart, sankey chart.

<img src="./assets/2026-10-12 181926.jpg" width="700">

<img src="./assets/2026-10-12 181953.jpg" width="700">

<img src="./assets/2026-10-12 181857.jpg" width="700">
