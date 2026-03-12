from src.utils import create_database, create_tables, insert_table
from src.manager import DBManager


def main() -> None:
    """
    Запускаем сбор данных и текстовое меню для запросов к БД вакансий.
    """
    print("Подождите идет сбор данных ...")

    name_db = "test_course"
    create_database(name_db)
    print("Подождите ещё чуть-чуть...")
    create_tables(name_db)
    print("Осталось немного...")
    insert_table(name_db)

    manager = DBManager(name_db)

    while True:
        print("\n Какую информацию вы хотите получить?")
        print("1. Список компаний")
        print("2. Список всех вакансий с указанием названия компании")
        print("3. Средняя зарплата по вакансиям")
        print("4. Список вакансий, зарплата которых выше средней по всем вакансиям")
        print("5. Получить список всех вакансий, в названии которых содержится слово из вашего запроса")
        print("6. Выход")
        answer = input().strip()
        print("Подождите идет обработка запроса...")

        if answer == "1":
            # List[Tuple[str, int]]
            for company, vac_count in manager.get_companies_and_vacancies_count():
                print(
                    f"Название компании: {company}\n"
                    f"Количество вакансий: {vac_count}\n"
                )

        elif answer == "2":
            # List[Tuple[str, str, int, int, str]]
            for company, title, s_from, s_to, url in manager.get_all_vacancies():
                print(
                    f"Название компании: {company}\n"
                    f"Название вакансии: {title}\n"
                    f"Зарплата от {s_from} руб. до {s_to} руб.\n"
                    f"Ссылка на вакансию: {url}\n"
                )

        elif answer == "3":
            # List[Tuple[str, int]]
            for title, avg_salary in manager.get_avg_salary():
                print(
                    f"Название вакансии: {title}\n"
                    f"Средняя зарплата {avg_salary} руб.\n"
                )

        elif answer == "4":
            # List[Tuple[str, int]]
            for title, avg_salary in manager.get_vacancies_with_higher_salary():
                print(
                    f"Название вакансии: {title}\n"
                    f"Средняя зарплата {avg_salary} руб.\n"
                )

        elif answer == "5":
            query_word = input("Введите название вакансии: ").strip()
            # List[Tuple[str, int, int, str]]
            results = manager.get_vacancies_with_keyword(query_word)
            for title, s_from, s_to, url in results:
                print(
                    f"Название вакансии: {title}\n"
                    f"Зарплата от {s_from} руб. до {s_to} руб.\n"
                    f"Ссылка на вакансию: {url}\n"
                )
            print(f"Найдено вакансий - {len(results)}")

        elif answer == "6":
            break


if __name__ == "__main__":
    main()
