#!/usr/bin/env python
'''
module docstring
'''

import re
import requests

url = "https://www.buycott.com/upc/" 

def scrape(upc):
        new_url = url + upc
        r = requests.get(new_url)
        name = re.search(r'<h2>(.*?)</h2>', r.text)

        if name != None:
            name = name.group(1)
            name = check_name(name)
        else:
            name = "Name Not Found"

        brandName = re.search(r'<a href="/brand/.*?">(.*?)</a>', r.text)
        if brandName != None:
            brandName = brandName.group(1)
            brandName = check_name(brandName)
        else:
            brandName = "Brand Name Not Found"

        return (brandName, name)

def check_name(name):
    value = name
    unicodeObj = re.findall(r"&#[xa-fA-F0-9]*?;", name)
    for uni in unicodeObj:
        value = re.sub(uni, chr(check_hex(uni)), name)
        name = value
    return name

def check_hex(num):
    if "&#x" in num:#found hex
        return int(num[3:-1], 16)
    return int(num[2:-1])

if __name__ == "__main__":
    upc = input("Enter a UPC: ")
    while int(upc) != -1:
        print(scrape(str(upc)))
        upc = input("Enter a UPC (-1 to quit): ")
