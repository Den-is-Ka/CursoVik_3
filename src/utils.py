import psycopg2
from src.config import config
from src.hh_api import HHParser


def create_database(name_db):
    """
    Создаем или пересоздаем БД name_db. Выполняется вне транзакции (autocommit).
    """
    params = config()
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {name_db}')
    cur.execute(f'CREATE DATABASE {name_db}')

    cur.close()
    conn.close()



def create_tables(name_db: str) -> None:
    """
    Создаем таблицы employers и vacancies (если их нет) + полезные индексы.
    """
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            # работодатели
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.employers (
                    id   BIGINT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """)

            # вакансии
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.vacancies (
                    id           BIGINT PRIMARY KEY,
                    employer_id  BIGINT NOT NULL
                                  REFERENCES public.employers(id)
                                  ON DELETE CASCADE,
                    name         VARCHAR(255) NOT NULL,
                    area         VARCHAR(255) NOT NULL,
                    url          TEXT NOT NULL,
                    salary_from  INTEGER NOT NULL DEFAULT 0,
                    salary_to    INTEGER NOT NULL DEFAULT 0,
                    CHECK (salary_from >= 0),
                    CHECK (salary_to   >= 0),
                    CHECK (salary_to = 0 OR salary_to >= salary_from)
                )
            """)
    conn.close()

def insert_table(name_db):
    """
    Парсим HH.ru и заливам данные в employers и vacancies без дублирования.
    """
    hh_parser = HHParser()
    employers = hh_parser.get_employers()
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            # Предприятия
            for emp in employers:
                cur.execute(
                    """
                    INSERT INTO public.employers (id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
                    """,
                    (int(emp["id"]), emp["name"]),
                )

            # Вакансии
            for emp in employers:
                raw_vacs = hh_parser.get_vacancies_by_employer(emp["id"])
                for v in raw_vacs:
                    # разбор зарплаты
                    if v.get("salary"):
                        s_from = v["salary"].get("from") or 0
                        s_to   = v["salary"].get("to") or 0
                    else:
                        s_from = s_to = 0

                    cur.execute(
                        """
                        INSERT INTO public.vacancies
                            (id, employer_id, name, area, url, salary_from, salary_to)
                        VALUES
                            (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (
                            int(v["id"]),
                            int(emp["id"]),
                            v["name"],
                            v["area"]["name"],
                            v["alternate_url"],
                            int(s_from),
                            int(s_to),
                        ),
                    )
    conn.close()
