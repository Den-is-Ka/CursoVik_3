import psycopg2  # type: ignore[import-untyped]
from typing import List, Tuple
from .config import config


def _eff_salary_expr() -> str:
    """
    Возвращаем SQL-выражение «средней» зарплаты по вакансии:
    если указаны оба значения -> среднее, иначе берём большее из from/to (или 0).
    """
    return (
        "CASE "
        "WHEN COALESCE(v.salary_from,0) > 0 AND COALESCE(v.salary_to,0) > 0 "
        "THEN (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0)) / 2.0 "
        "ELSE GREATEST(COALESCE(v.salary_from,0), COALESCE(v.salary_to,0)) "
        "END"
    )


class DBManager:
    """
    Доступ к данным работодателей и вакансий.
    """
    def __init__(self, dbname: str) -> None:
        """
        Сохраняем имя БД и параметры подключения из config().
        """
        self.dbname = dbname
        self.params = config()  # {'user': ..., 'password': ..., 'host': ..., 'port': ...}

    def _conn(self):
        """
        Открываем подключение к PostgreSQL (используй в контекст-менеджере).
        """
        return psycopg2.connect(dbname=self.dbname, **self.params)

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Возвращаем список (компания, количество вакансий).
        """
        sql = """
            SELECT e.name AS company, COUNT(v.id) AS vac_cnt
            FROM public.employers e
            LEFT JOIN public.vacancies v ON v.employer_id = e.id
            GROUP BY e.name
            ORDER BY e.name;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [(r[0], int(r[1])) for r in rows]

    def get_all_vacancies(self) -> List[Tuple[str, str, int, int, str]]:
        """
        Возвращаем (компания, вакансия, salary_from, salary_to, url).
        """
        sql = """
            SELECT e.name AS company, v.name AS title,
                   COALESCE(v.salary_from,0) AS s_from,
                   COALESCE(v.salary_to,0)   AS s_to,
                   v.url
            FROM public.vacancies v
            JOIN public.employers e ON e.id = v.employer_id
            ORDER BY (COALESCE(v.salary_to,0) + COALESCE(v.salary_from,0)) DESC, v.name;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [(r[0], r[1], int(r[2]), int(r[3]), r[4]) for r in rows]

    def get_avg_salary(self) -> List[Tuple[str, int]]:
        """
        Возвращаем (название вакансии, «средняя» зарплата).
        """
        eff = _eff_salary_expr()
        sql = f"""
            SELECT v.name,
                   CAST({eff} AS INTEGER) AS avg_salary
            FROM public.vacancies v
            ORDER BY avg_salary DESC, v.name;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [(r[0], int(r[1])) for r in rows]

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, int]]:
        """
        Вакансии, у которых «средняя» выше средней по всем вакансиям.
        """
        eff = _eff_salary_expr()
        sql = f"""
            WITH global_avg AS (
                SELECT AVG({eff}) AS gavg
                FROM public.vacancies v
            )
            SELECT v.name, CAST({eff} AS INTEGER) AS avg_salary
            FROM public.vacancies v, global_avg
            WHERE {eff} > global_avg.gavg
            ORDER BY avg_salary DESC, v.name;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [(r[0], int(r[1])) for r in rows]

    def get_vacancies_with_keyword(self, word: str) -> List[Tuple[str, int, int, str]]:
        """
        Фильтр по подстроке в названии вакансии (без учёта регистра).
        """
        pattern = f"%{word.strip().lower()}%"
        sql = """
            SELECT v.name,
                   COALESCE(v.salary_from,0) AS s_from,
                   COALESCE(v.salary_to,0)   AS s_to,
                   v.url
            FROM public.vacancies v
            WHERE LOWER(v.name) LIKE %s
            ORDER BY (COALESCE(v.salary_to,0) + COALESCE(v.salary_from,0)) DESC, v.name;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (pattern,))
            rows = cur.fetchall()
        return [(r[0], int(r[1]), int(r[2]), r[3]) for r in rows]
