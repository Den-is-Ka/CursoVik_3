from src.utils import create_database, create_tables, insert_table
from src.manager import DBManager

name_db = 'test_course'
create_database(name_db)
create_tables(name_db)
insert_table(name_db)

manager = DBManager(name_db)


while True:
    print('1 вывод всех вакансий')
    print('2 вывод всех компаний')
    print('3 вывод топ зарплат')
    answer = input()
    if answer == '1':
        print(manager.get_all_employers())
    elif answer == '2':
        print(manager.
    elif answer == '3':
        print(manager.
    elif answer == '4':
        print(manager.
    elif answer == '5':
        print(manager.
    elif answer == '6':
        break
