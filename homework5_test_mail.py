import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from pprint import pprint
from lxml import html
import requests
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

chrome_options = Options()
chrome_options.add_argument('start-maximized')
service = Service("./chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get('https://mail.ru/')

email_name = driver.find_element(By.XPATH, '//input[@class="email-input svelte-1tib0qz"]')
email_name.send_keys('study.ai_172') 

email_domain = driver.find_element(By.XPATH, '//select[@class="domain-select svelte-1tib0qz"]')
email_domain.send_keys('mail.ru')

button_to_password = driver.find_element(By.XPATH, '//button[@class="button svelte-1tib0qz"]')
button_to_password.click()

time.sleep(1)
email_password = driver.find_element(By.XPATH, '//input[@class="password-input svelte-1tib0qz"]')
email_password.send_keys('NextPassword172#')

button_entrance = driver.find_element(By.XPATH, '//button[@class="second-button svelte-1tib0qz"]')
button_entrance.click()

driver.implicitly_wait(10)

messages = driver.find_elements(By.CLASS_NAME, "llc__content")
driver.implicitly_wait(10)

for step in range(10):
    actions=ActionChains(driver)
    actions.move_to_element(messages[-1])
    actions.perform()
    time.sleep(3)

driver.implicitly_wait(10)
messages = driver.find_elements(By.CLASS_NAME, "llc__content")

email_list=[]
for message in messages:
    email_from=message.find_element(By.CLASS_NAME, 'll-crpt').get_attribute('title')
    email_topic=message.find_element(By.CLASS_NAME, 'll-sj__normal').text
    email_date=message.find_element(By.CLASS_NAME, 'llc__item_date').text #llc__item llc__item_date
    email_text=message.find_element(By.CLASS_NAME, 'll-sp__normal').text
    email_from_dic={}
    email_from_dic['email_from']=email_from
    email_from_dic['email_topic']=email_topic
    email_from_dic['email_date']=email_date
    email_from_dic['email_text']=email_text
    email_list.append(email_from_dic)

client = MongoClient('127.0.0.1', 27017)

db=client['mail_db']
mail_db=db.mail_db

##############################################

for n in email_list:
    mail_db.insert_one(n)

driver.quit()
