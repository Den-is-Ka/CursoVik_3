import requests


class HHParser:
    def __init__(self):
        self.__url_employer = 'https://api.hh.ru/employers'
        self.__url_vacancies = 'https://api.hh.ru/vacancies'


    def get_employers(self):
        params = {'sort_by': 'by_vacancies_open', 'per_page': 10}
        response = requests.get(self.__url_employer, params=params).json()['items']
        return [{'id': employer['id'], 'name': employer['name']} for employer in response]

    def get_vacancies_by_employer(self, employer_id):
        params = {'employer_id': employer_id, 'per_page': 100}
        response = requests.get(self.__url_vacancies, params=params).json()['items']
        return response


    def get_all_vacancies_by_employers(self):
        employers = self.get_employers()
        all_vacancies = []
        for employer in employers:
            vacancies = self.get_vacancies_by_employer(employer['id'])
            all_vacancies.extend([self.filter_vacancy(vacancy) for vacancy in vacancies])
        return all_vacancies


    @staticmethod
    def filter_vacancy(vacancy):
        if vacancy['salary']:
            salary_from = vacancy['salary']['from'] if vacancy['salary']['from'] else 0
            salary_to = vacancy['salary']['to'] if vacancy['salary']['to'] else 0
        else:
            salary_from = 0
            salary_to = 0
        return {'id': vacancy['id'], 'name': vacancy['name'], 'area': vacancy['area']['name'], 'url': vacancy['alternate_url'], 'salary_from': salary_from, 'salary_to': salary_to}
