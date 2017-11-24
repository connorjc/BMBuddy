#!/usr/bin/env python
"""
module docstring
"""

import pymysql
import os
import dotenv
import walmart
import buycott

dotenv.load_dotenv('.env')
db_connect = pymysql.connect(host=os.getenv('HOST'), port=3306, user=os.getenv('USER'), passwd=os.getenv('PASSWORD'), db=os.getenv('DB') )

''' FIXME: Line 29 Have buycott.scrape() return None if no results found
 else:
    result = buycott.scrape(upc)
    if result:
      brandName, name = resul
'''
 
def update_database(cur, upc):
  result = walmart.callAPI(upc)

  name = None

  if result:
    brandName, walmartPrice, name = result

  if name:
    if not brandName:
      brandName = ""
    if not walmartPrice:
      walmartPrice = ""

    cur.execute('INSERT INTO Item (Brand, WalmartPrice, Name, UPC) VALUES (\"' + brandName + '\",\"' + walmartPrice + '\",\"' + name + '\",\"' + upc + "\");");
    db_connect.commit()
    return True
  return False

def query(param, crit):

  if not param:
    return None

  cur = db_connect.cursor()
  if crit == "UPC":
    cur.execute("SELECT * FROM Item WHERE UPC = \"" + param + "\"")
    item_data = cur.fetchall()

    print(item_data)

    if not item_data:
      # Fetch new data and try again
      if update_database(cur, param):
        cur.execute("SELECT * FROM Item WHERE UPC = \"" + param + "\"")
        item_data = cur.fetchall()
  elif crit == "Name":
    cur.execute("SELECT * FROM Item WHERE Name LIKE \"%" + param.strip() + "%\"")
    item_data = cur.fetchall() 
  

  for info in item_data:
    if info[0] == None:
      brandName = "Unknown"
    if info[1] == None:
      walmartPrice = "Unknown"
    if info[2] == None:
      costcoPrice = "Unknown"
    if info[3] == None:
      name = "Unknown"
    if info[4] == None:
      upc = "Unknown"

  cur.close()

  return item_data

if __name__ == "__main__":
    pass
