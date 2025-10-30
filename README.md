#                            Курсовой проект:
    Загрузка вакансий с hh.ru в PostgreSQL и консольный поиск.
  Проект собирает актуальные вакансии с платформы hh.ru, сохраняет их в базу данных PostgreSQL и предоставляет консольное 
меню для выборок: список компаний, вакансии с зарплатами и ссылками, «средние» зарплаты, вакансии выше среднего и поиск
по ключевому слову.

# Возможности
### Получение ТОР-работодателей (по количеству открытых вакансий).
### Загрузка всех их вакансий через публичное API hh.ru.
### Очистка/создание базы данных и таблиц (employers, vacancies).
### Идемпотентная запись (без дублей по id, с ON CONFLICT).
## Консольное меню:
##### Список компаний и количество их вакансий
##### Все вакансии (компания, название, зарплата, ссылка)
##### «Средняя» зарплата по вакансиям
##### Вакансии выше общей средней
##### Поиск по ключевому слову в названии вакансии
### Архитектура и файлы
##### .
##### ├─ main.py                    # Точка входа (CLI-меню)
##### ├─ database.ini               # Настройки подключения к PostgreSQL
##### └─ src/
#####    ├─ __init__.py
#####    ├─ config.py               # Парсер database.ini
#####    ├─ hh_api.py               # HHParser: работа с API hh.ru (requests)
#####    ├─ utils.py                # Создание БД/таблиц + загрузка данных
#####    └─ manager.py              # DBManager: SQL-запросы к БД

## Схема БД
### employers
##### ├─ id BIGINT PRIMARY KEY
##### ├─ name VARCHAR(255) NOT NULL

### vacancies
##### ├─ id BIGINT PRIMARY KEY
##### ├─ employer_id BIGINT NOT NULL REFERENCES employers(id) ON DELETE CASCADE
##### ├─ name VARCHAR(255) NOT NULL
##### ├─ area VARCHAR(255) NOT NULL
##### ├─ url TEXT NOT NULL
##### ├─ salary_from INTEGER NOT NULL DEFAULT 0
##### ├─ salary_to INTEGER NOT NULL DEFAULT 0
##### ├─ CHECK-ограничения на неотрицательные зарплаты и корректный диапазон
   
## Требования
##### ├─ Python 3.11+ (подходит 3.13)
##### ├─ PostgreSQL 13+ (локально, порт 5432)
##### ├─ Доступ в интернет к https://api.hh.ru
##### ├─ Библиотеки: requests, psycopg2 (или psycopg2-binary)

### Установка
1. Вариант A — Poetry (рекомендуется)
##### В корне проекта
#### poetry init -n
#### poetry add requests psycopg2-binary
#### poetry run python main.py
2. Вариант B — venv + pip
#### python -m venv .venv
#### .venv\Scripts\activate


#### pip install requests psycopg2-binary
#### python main.py


### Настройка PostgreSQL
#### Создайте файл database.ini в корне:

#### [postgresql]
#### user=postgres
#### password=ВАШ_ПАРОЛЬ
#### host=localhost
#### port=5432

## ⚠️ Пользователь должен иметь права на CREATE DATABASE.
## Если сервер не запущен — на Windows проверь «Службы» → PostgreSQL → «Запустить».

### Запуск
#### python main.py
### Сценарий выполнит:
 1. Создание БД test_course (если была — дропнет).
 2. Создание таблиц.
 3. Загрузку работодателей и их вакансий с hh.ru.
 4. Откроет консольное меню.

### Пример меню:

##### Какую информацию вы хотите получить?
1. Список компаний
2. Список всех вакансий с указанием названия компании
3. Средняя зарплата по вакансиям
4. Список вакансий, зарплата которых выше средней по всем вакансиям
5. Получить список всех вакансий, в названии которых содержится слово из вашего запроса
6. Выход

### Где что в коде

### src/hh_api.py — класс HHParser:
#### get_employers() — топ работодателей (per_page=10, sort_by=by_vacancies_open).
#### get_vacancies_by_employer(employer_id) — вакансии работодателя.
#### filter_vacancy() — нормализует поля (зарплата, ссылки, локация и т.д.).
### src/utils.py:
#### create_database(name_db) — дроп/создание БД.
#### create_tables(name_db) — создание таблиц со всеми ограничениями.
#### insert_table(name_db) — загрузка работодателей и всех их вакансий в БД.
### src/manager.py — класс DBManager с готовыми запросами:
#### get_companies_and_vacancies_count()
#### get_all_vacancies()
#### get_avg_salary()
#### get_vacancies_with_higher_salary()
#### get_vacancies_with_keyword(word)
### src/config.py — функция config() читает database.ini.
### main.py — собирает всё вместе и даёт консольное меню.

## Лицензия

Для учебных целей. API hh.ru — публичное, но просьба соблюдать их правила и не злоупотреблять частотой запросов.


