from pprint import pprint
from lxml import html
import requests
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.2.169 Yowser/2.5 Safari/537.36'
adress_lenta = 'https://lenta.ru/parts/news/'
response_lenta = requests.get(adress_lenta)

dom_lenta = html.fromstring(response_lenta.text)
# items = dom.xpath("//a[contains(@class,'link')]")
items_lenta = dom_lenta.xpath("//div[contains(@class,'item news')]")

news_lenta = []

for item in items_lenta:
    txt_upd = []
    dt_upd = []
    txt = item.xpath(".//h3/a[@target]//text()")
    for i in txt:
        i = i.replace("\xa0", " ")
        txt_upd.append(i)
    link = item.xpath(".//@data-more-url")
    dt = item.xpath(".//div[@class ='info g-date item__info']//text()")[-1]  #
    dt_upd.append(dt)

    piece_of_news = {}

    piece_of_news['source'] = 'https://lenta.ru/parts/news/'
    piece_of_news['txt_upd'] = txt_upd
    piece_of_news['link'] = link
    piece_of_news['date'] = datetime.today().strftime('%Y-%m-%d')
    piece_of_news['time'] = dt_upd

    news_lenta.append(piece_of_news)
    
 
pprint(news_lenta)
##############################################
adress_mail = 'https://news.mail.ru/'
response_mail = requests.get(adress_mail)

dom_mail = html.fromstring(response_mail.text)
# items = dom.xpath("//a[contains(@class,'link')]")
items_mail = dom_mail.xpath("//li[contains(@class,'list__item')]")

news_mail = []
for item in items_mail:
    txt = item.xpath(".//span[@class ='link__text']//text()")
    link = item.xpath(".//span[@class ='link__text']/../@href")
    dt = item.xpath(".//span[@class ='link__text']/../../span[@class ='newsitem__param js-ago']/@datetime")

    piece_of_news = {}

    piece_of_news['source'] = 'https://news.mail.ru/'
    piece_of_news['txt'] = txt
    piece_of_news['link'] = link
    piece_of_news['dt'] = dt

    news_mail.append(piece_of_news)
##############################################
client = MongoClient('127.0.0.1', 27017)
#db.recent_news.delete_Many()
db=client['news_db']
news_mail_db=db.news_mail
news_lenta_db=db.news_lenta
##############################################

for n in news_lenta:
    news_lenta_db.insert_one(n)

for n in news_mail:
    news_mail_db.insert_one(n)
      
# Вопросы: на Ленте еще относительно нормально распарсилось, не совсем поняла только как сделать нормальный линк: через "|" соединяться не хочет,т.к. один - стринг, а второй элемент "Element a at 0x181f5860900"
# А вот с mail.ru не очень зашло. Не понимаю, как отобрать все новости: часть новостей не высвечивается, но по дргуим тэгам тоже ничего не дает. 
# как получить доступ к дате тоже не поняла... пытаюсь поднять на директорию или две выше, тоже безуспешно.
  