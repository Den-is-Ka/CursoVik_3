from src.utils import create_database, create_tables, insert_table

name_db = 'test_course'
create_database(name_db)
create_tables(name_db)
insert_table(name_db)