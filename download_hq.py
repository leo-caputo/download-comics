import requests
import os
from selenium import webdriver
from selenium.common import WebDriverException

dir_path = f'{os.path.expanduser("~")}/Pictures/Invincible/'
url = 'https://readcomiconline.li/Comic/Invincible/'


def find_name_path(url):
    r = requests.get(url)
    response = r.text.split('\n')
    hqs_path = []
    for line in response:
        if '/Comic/Invincible/TPB' in line:
            start = line.find('/')
            end = line.find('">')
            hqs_path.append(line[start:end])

    return hqs_path


def download_pages(path):

    url_base = f'https://readcomiconline.li{path}&s=&quality=hq'
    cookie = {'name': 'rco_readType',
              'value': '1',
              'domain': 'readcomiconline.li'
              }

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.add_cookie(cookie)
    driver.get(url)

    html_content = driver.page_source.split('\n')

    driver.quit()

    urls = []

    for line in html_content:
        if "https://2.bp.blogspot.com" in line:
            start = line.find('https')
            end = line.find('" onerror')
            urls.append(line[start:end])

    for i in range(len(urls)):
        response = requests.get(urls[i])
        end = path.find('?')
        file_path = f'{dir_path}/{path[23:end]}/tpb-{i}.png'

        with open(file_path, 'wb') as file:
            file.write(response.content)
