import psycopg2
from src.config import config
from src.hh_api import HHParser


def create_database(name_db):
    params = config()
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {name_db}')
    cur.execute(f'CREATE DATABASE {name_db}')

    cur.close()
    conn.close()



def create_tables(name_db: str) -> None:
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            cur.execute('CREATE TABLE employers ('
            'id int PRIMARY KEY,'
            'name varchar(255) NOT NULL'            
            ')')

            # СЮДА ПИСАТЬ СКРИПТ ДЛЯ ВАКАНСИИ
    conn.close()

def insert_table(name_db):
    hh_parser = HHParser()
    emloyers = hh_parser.get_employers()
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            for employer in emloyers:
                cur.execute('INSERT INTO employers VALUES (%s, %s)', (employer['id'], employer['name']))
            #СЮДА СКРИПТ НА ДОБАВЛЕНИЕ ДАННЫХ В ТАБЛИЦУ ВАКАНСИЙ
    conn.close()
