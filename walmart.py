#!/usr/bin/env python
'''
module docstring
'''

import requests
import json
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
url = os.getenv('APIKEY')

def callAPI(upc):
        new_url = url + upc
        r = requests.get(new_url)
        if (r.status_code / 100) == 2:
            str_content = r.content.decode('utf-8')
            info = json.loads(str(str_content))
            name = (info['items'][0]['name'])
            print(name)

            if 'salePrice' in info['items'][0]:
                salePrice = ('Price: ' + str(info['items'][0]['salePrice']))
                print(salePrice)
            else:
                salePrice = None

            if 'msrp' in info['items'][0]:
                msrp = ('MSRP: ' + str(info['items'][0]['msrp']))
                print(msrp)
            else:
                msrp = None

            if 'size' in info['items'][0]:
                size = ('SIZE: ' + str(info['items'][0]['size']))
                print(size)
            else:
                size = None
            return name, salePrice, msrp, size
        else:
            print('UPC not found')
            return None

if __name__ == "__main__":
    upc = input("Enter a UPC (-1 to quit): ")
    while int(upc) != -1:
        callAPI(upc)
        upc = input("Enter a UPC (-1 to quit): ")
# The item is stored in info['items'][0]. From there attributes of interest
# are 'shortDescription', 'size', 'brandName', 'salePrice', 'msrp', and
# 'imageEntities', category '
