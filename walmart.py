#!/usr/bin/env python
'''
module docstring
'''

import requests
import json
import os
import dotenv
import pymysql

dotenv.load_dotenv('.env')
url = os.getenv('APIKEY')
db_connect = pymysql.connect(host=os.getenv('HOST'), port=3306, user='bmbuddy', passwd='clars', db=os.getenv('DB') )

def callAPI(upc):
  new_url = url + upc
  r = requests.get(new_url)
  if (r.status_code / 100) == 2:
    str_content = r.content.decode('utf-8')
    info = json.loads(str(str_content))
    name = (info['items'][0]['name'])
    if 'salePrice' in info['items'][0]:
      salePrice = str(info['items'][0]['salePrice'])
    else:
      salePrice = None
    if 'brandName' in info['items'][0]:
      brandName = str(info['items'][0]['brandName'])
    else:
      brandName = None
    if 'msrp' in info['items'][0]:
      msrp = str(info['items'][0]['msrp'])
    else:
      msrp = None
    return brandName, salePrice, name, msrp
  else:
    return None

if __name__ == "__main__":
  print("Walmart Module")
  choice = int(input("Select an option:\n\t1) UPC Search\n\t2) UPC Search from file\n\t3) Exit\nChoice: "))

  while choice < 1 or choice > 3:
    print("Not a valid option.\n")
    choice = int(input("Select an option:\n\t1) UPC Search\n\t2) UPC Search from file\n\t3) Exit\nChoice: "))

  while choice != 3:
    if choice == 1:
      upc = input("Enter UPC (-1 to quit): ")
      while int(upc) != -1:
        result = callAPI(upc)
        if result:
          print(result)
          print("Name: " + result[0])
          print("SalePrice: " + result[1])
          print("MSRP: " + result[2])
          print("Size: " + result[3])
        else:
          print("UPC Information Not Found")
        upc = input("Enter UPC (-1 to quit): ")
    elif choice == 2:
      filename = input("Enter UPC filename: ")
      file = open(filename)
      
      while not file:
        print("Cannot open file.")
        filename = input("Enter UPC filename: ")
        file = open(filename)

      cur = db_connect.cursor()
      for line in file:
        cur.execute('SELECT * FROM Item WHERE UPC = ' + line.rstrip())
        rv = cur.fetchall()
        print("UPC: " + line)
        if not rv:
          info = callAPI(line.rstrip())
          if info:
            print("Adding: ")
            for x in info:
              print(x)
            query = 'INSERT INTO Item (Brand, Price, Name, UPC, Store_Name) VALUES (\"' + str(info[0]) + '\",\"'
            if info[1]:
              query += info[1]
            elif info[3]:
              query += info[3]
            else:
              query += '0.00'
            query += '\",\"' + str(info[2]) + '\",\"' + line.rstrip() + '\",\"Walmart\");'
            print("Query: " + query)
            cur.execute(query)
            db_connect.commit()
      file.close()
      cur.close() 
    print("Walmart Module")
    choice = int(input("Select an option:\n\t1) UPC Search\n\t2) UPC Search from file\n\t3) Exit\nChoice: "))

# The item is stored in info['items'][0]. From there attributes of interest
# are 'shortDescription', 'size', 'brandName', 'salePrice', 'msrp', and
# 'imageEntities', category '
