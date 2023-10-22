import requests
from bs4 import BeautifulSoup

import db
import products as prod


# получение курса валют
def currency(title: str):
    CURRENCY = f'https://www.banki.ru/products/currency/{title}/'
    headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.123 Safari/537.36'}
    page = requests.get(CURRENCY, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    convert = soup.findAll('div', {'class': 'currency-table__large-text'})
    return convert[0].text.replace(',', '.')


# получение наиболее выгодной стоимости продуктов
def best_prices_products(title: str):
    PRODUCTS = f'https://www.maria-ra.ru/aktsii/{title}/'
    headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.123 Safari/537.36'}
    page = requests.get(PRODUCTS, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.findAll('li', {'class': 'catalog__item'})
    prod = []
    for item in items:
        prod.append(
            {
                'title': item.find('div', {'class': 'discount-item__title'}).get_text(),
                'image': 'https://www.maria-ra.ru' + item.find('img', {'class': 'discount-item__img'}).get('src'),
                'price': '.'.join(item.find('div', {'class': 'discount-item__price'}).get_text().split(' '))
            }
        )
    return prod[:3]


# получение наиболее выгодной стоимости футболок
def clothes():
    CLOTHES = 'https://www.oodji.com/mens_collection/futbolki/'
    headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.123 Safari/537.36'}
    page = requests.get(CLOTHES, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.findAll('div', {'class': 'listItem addToSortTable js-google-analytics-product-section'})
    tshirt = []
    for item in items:
        tshirt.append(
            {
                'title': item.find('div', {'class': 'name'}).get_text().rstrip('\n').lstrip('\n'),
                'price': item.find('div', {'class': 'price'}).get_text().split('\n')[1].rstrip(' o'),
                'image': item.find('img').get('src')
            }
        )
    return tshirt[:3]


# получение наиболее выгодной стоимости платья
def clothes1():
    CLOTHES = 'https://www.oodji.com/womens_collection/platya/'
    headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.123 Safari/537.36'}
    page = requests.get(CLOTHES, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.findAll('div', {'class': 'listItem addToSortTable js-google-analytics-product-section'})
    tshirt = []
    for item in items:
        tshirt.append(
            {
                'title': item.find('div', {'class': 'name'}).get_text().rstrip('\n').lstrip('\n'),
                'price': item.find('div', {'class': 'price'}).get_text().split('\n')[1].rstrip(' o'),
                'image': item.find('img').get('src')
            }
        )
    return tshirt[:3]


# объединение полученных результатов одежды
def all_clothes():
    cl1 = clothes()
    cl2 = clothes1()
    cl_all = cl1 + cl2
    return cl_all


# получение наиболее выгодных цен на услуги такси
def best_taxi():
    TAXI = 'https://taksitop.ru/barnaul'
    headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.123 Safari/537.36'}
    page = requests.get(TAXI, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.findAll('div', {'class': 'postard'})
    del items[0]
    taxi = []
    for item in items:
        taxi.append(
            {
                'title': item.find('h3', {'class': 'postard__title'}).find('a').get_text(),
                'price': item.find('div', {'class': 'taxi-content'}).find('span', {'class': 'entry-author'}).get_text()[4:],
                'time': item.find('div', {'class': 'taxi-content'}).find('span', {'class': 'entry-time'}).get_text()[12:],
                'phone': item.find('div', {'class': 'taxi-icon-inl'}).get_text(),
                'pay': item.find('div', {'class': 'taxi-content'}).find('span', {'class': 'entry-date'}).get_text()[6:]
            }
        )
    return taxi


# сортировка цен на такси по возрастанию
def sort_taxi():
    taxi = best_taxi()
    taxi1 = sorted(taxi, key=lambda x: int(x['price'].split(' ')[1]))
    taxi2 = taxi1[:3]
    return taxi2


# объединение полученных результатов продуктов
def all_prod():
    prod1 = best_prices_products(prod.MEAT)
    prod2 = best_prices_products(prod.MILK)
    prod3 = best_prices_products(prod.FRUITS)
    prod_all = prod1 + prod2 + prod3
    return prod_all


# вычисление ежемесячных выплат и общей суммы выплат по ануитетному платежу
def credit_ann(summ, period, proc):
    count_months = period * 12
    i = proc / 1200.0
    K = (i * (1 + i) ** count_months) / (((1 + i) ** count_months) - 1)
    mp = summ * K
    total = mp * count_months
    return round(mp, 2), round(total, 2)


# вычисление ежемесячных выплат и общей суммы выплат по диференцированному платежу
def credit_dif(summ, period, proc):
    months = []
    count_months = period * 12
    debt = summ
    t = summ / (period * 12)
    while count_months != 0:
        mp = t + (debt * proc / 1200)
        months.append(round(mp, 2))
        debt = debt - t
        count_months = count_months - 1
    return months, round(sum(months), 2)


def get_price_most_expensive(days_count: int):
    price = []
    max_cost = 0
    most_expensive = ''
    costs = db.expenses_stat(days_count)
    for i in costs:
        price.append(i[1])
        if i[1] > max_cost:
            max_cost = i[1]
            most_expensive = f'Самой большой вашей тратой оказалось - {i[0]}, на которую вы потратили {i[1]} руб.'
    return price, most_expensive


# получение статистики расходов
def analytic_of_day():
    price, most_expensive = get_price_most_expensive(1)
    costs_of_day = sum(price)
    costs_of_week = costs_of_day * 7
    costs_of_month = costs_of_day * 30
    return most_expensive, costs_of_day, costs_of_week, costs_of_month


# получение статистики расходов за неделю
def analytic_of_week():
    price, most_expensive = get_price_most_expensive(7)
    costs_of_week = sum(price)
    costs_of_month = costs_of_week * 4.5
    return most_expensive, costs_of_week, costs_of_month


# получение статистики расходов за месяц
def analytic_of_month():
    price, most_expensive = get_price_most_expensive(30)
    costs_of_month = sum(price)
    costs_of_year = costs_of_month * 12
    return most_expensive, costs_of_month, costs_of_year
