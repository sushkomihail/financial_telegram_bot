import requests
from bs4 import BeautifulSoup


CURRENCY = 'https://quote.rbc.ru/ticker/72413'
headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.123 Safari/537.36'}
page = requests.get(CURRENCY, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
convert = soup.findAll("span", {'class': 'chart__info__sum'})
print(convert[0].text.replace(',', '.'))
