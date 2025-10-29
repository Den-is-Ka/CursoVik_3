import psycopg2

from src.config import config


class DBManager:
    def __init__(self, db_name):
        self.__db_name = db_name


    def execute_query(self, query):
        params = config()
        conn = psycopg2.connect(dbname=self.__db_name, **params)
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                res = cur.fetchall()
        conn.close()
        return res

    def get_all_employers(self):
        return self.execute_query('SELECT * FROM employers')

