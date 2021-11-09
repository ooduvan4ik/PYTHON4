import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

url = "https://hh.ru/search/vacancy"  # я видела пример, где поиск по api.hh.ru/vanacies - в чем разница? правильно я понимаю, что там другой подход к парсингу?
salary_from=int(input('Введите зп для поиска: '))
#salary_to=0
city = 'Москва'
key_words = input('Введите ключевые слова для поиска: ')
page = 0
pages = input('Введите количество страниц: ')
per_page = 100
area = 1

my_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.1.684 Yowser/2.5 Safari/537.36'}  # {'HH-User-Agent':  'api-test-agent' } #HH-User-Agent 'MyApp/1.0 (potapych190@mail.ru)'
my_params = {'city': city,
             'text': key_words,
             'salary_from': salary_from,
             #'salary_to': salary_to,
             'area': area,
             'page': page}

vacancy_list = []

while True:

    response = requests.get(url, headers=my_header, params=my_params)
    # page=N&per_page=M

    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all("div", {'class': 'vacancy-serp-item'})

    # print(vacancies)

    # if response.ok and vacs and params['page'] < int(pages):

    if response.ok and vacancies and my_params['page'] < int(pages):
        for vac in vacancies:
            vac_data = {}
            try:
                info = vac.find('a', {'class': 'bloko-link'})
                # print(info)
                name = info.text
                # print(name)
                link = info['href']
                # print(link)
            except:
                info = None

            salary_block = vac.find('div', {'class': 'vacancy-serp-item__sidebar'})
            try:
                salary = salary_block.find('span').text
                salary = salary.replace("\u202f", "")
                if salary.startswith("от", 0, 3):
                    salary_min = int(salary.split()[1])
                    salary_max = "Не указано"
                    salary_zcurrency = ''.join(salary.split()[2:])
                elif "до" in salary:
                    salary_min = "Не указано"
                    salary_max = int(salary.split()[1])
                    salary_zcurrency = ''.join(salary.split()[2:])
                else:
                    salary_min = int(salary.split()[0])
                    salary_max = int(salary.split()[2])
                    salary_zcurrency = ''.join(salary.split()[3:])
            except:
                salary_min = 'Не указано'
                salary_max = 'Не указано'
                salary_zcurrency = 'Не указано'

            web = 'hh.ru'

            vac_data['name'] = name
            vac_data['salary_min'] = salary_min
            vac_data['salary_max'] = salary_max
            vac_data['salary_zcurrency'] = salary_zcurrency
            vac_data['link'] = link
            vac_data['web'] = web

 ##############################################
            def check_zp(salary_to_check):
                try:
                    int(salary_min) and int(salary_max)
                    if int(salary_min) > salary_to_check:
                        vacancy_list.append(vac_data)
                    elif int(salary_min) < salary_to_check and int(salary_max) > salary_to_check:
                        vacancy_list.append(vac_data)
                except ValueError:
                    if salary_max == 'Не указано':
                        vacancy_list.append(vac_data)
                    else:
                        pass

            check_zp(salary_from)
            #vacancy_list.append(vac_data)
            # print(vacancy_list)
            my_params['page'] += 1


    else:
        break

pprint(vacancy_list)
##############################################
client = MongoClient('127.0.0.1', 27017)

db=client['news_db']
hh_collection=db.hh_collection

##############################################

for i in vacancy_list:
    try:
        hh_collection.insert_one(i)
    except dke:
        print(f'документ уже существует в базе')