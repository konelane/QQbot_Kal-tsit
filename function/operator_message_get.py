#! /usr/bin/env python3
# coding:utf-8

import requests
from bs4 import BeautifulSoup

drl = 'https://wiki.biligame.com/arknights/%E5%B9%B2%E5%91%98%E6%95%B0%E6%8D%AE%E8%A1%A8'

page = requests.get(drl)
soup = BeautifulSoup(page.content, 'html.parser')  #解析网页

# print(soup)
Link=soup.find_all("a")
for link in Link:
    hr = link.get('herf')
    print(hr)
# Link=soup.find_all("td",)
# print(Link)

# Link=soup.find_all("td",class_="visible-md visible-sm visible-lg")
# print(Link)
# Link=soup.find_all("a")
# print(Link)

