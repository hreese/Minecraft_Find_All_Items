#!/usr/bin/env python3

from lxml import html
import requests
from operator import itemgetter
from pprint import pprint

urls = {
        "blockids": "http://minecraft.gamepedia.com/Data_values/Block_IDs",
        "itemids" : "http://minecraft.gamepedia.com/Data_values/Item_IDs",
        }

items = []
for url in urls.values():
    page = requests.get(url)
    tree = html.fromstring(page.content)
    rows = tree.xpath('//table//tr')
    for row in rows:
        if row[0].tag == 'th':
            continue
        try:
            v = {
                    'id':   row[1].xpath('./span/text()|./text()')[0],
                    'name': row[3].xpath('./span/text()|./text()')[0],
                    'desc': row[4].xpath('./a/text()|./text()')[0],
            }
        except:
            continue
        items.append(v)

for i in items:
    print(','.join((i['desc'], i['name'], '')))
