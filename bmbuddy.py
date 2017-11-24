#!/usr/bin/env python
"""
module docstring
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap

import pymysql
import os
import dotenv
import re
import fnmatch

import searchbar
import buycott
import walmart

dotenv.load_dotenv('.env')

app = Flask(__name__)
Bootstrap(app)

db_connect = pymysql.connect(host=os.getenv('HOST'), port=3306, user=os.getenv('USER'), passwd=os.getenv('PASSWORD'), db=os.getenv('DB') )

app.secret_key = os.getenv('KEY')

@app.route('/')
def homepage():
    if 'user_data' in session:
        user = session['user_data']
        cur = db_connect.cursor()
        cur.execute("SELECT Name, Budget \
            FROM House \
            WHERE HM=\"" + user[1] + "\" \
            OR BM1=\"" + user[1] + "\" \
            OR BM2=\"" + user[1] + "\"")
        house = cur.fetchone()
        cur.close()
        return render_template("home.html", name = user[0], house = house[0], budget = house[1])
    else:
        return render_template("index.html")

@app.route('/search', methods = ['POST'])
def search():
  print("I am in search")
  print(request.form)
  param = request.form['search_param']
  criteria = request.form['search_crit']

  print(param,criteria)

  results = None

  if param:
    results = searchbar.query(param,criteria)

  if results and len(results) == 1:
    print(results)
    brandName, walmartPrice, costcoPrice, name, upc = results[0]

    image = None; 

    for file in os.listdir('static/product_images'):
      if fnmatch.fnmatch(file, upc + '.*'):
        image = file
        break

    return render_template("product.html", name = name, brand = brandName, upc = upc, wPrice = walmartPrice, cPrice = costcoPrice, image = image)
  else:
    return render_template("search.html",items = results)

@app.route('/shopping')
def shopping_list():
  if 'user_data' in session:
    user = session['user_data']
    cur = db_connect.cursor()
    cur.execute("SELECT Store, Name, Quantity, WalmartPrice, CostcoPrice, UPC \
        FROM `Shopping List`, Item \
        WHERE ID = (\
            SELECT `Shopping List` \
            FROM House \
            WHERE HM=\"" + user[1] + "\" \
            OR BM1=\"" + user[1] + "\" \
            OR BM2=\"" + user[1] + "\" \
        ) AND UPC = Item")
    items = cur.fetchall()
    cur.execute("SELECT Budget \
        FROM House \
        WHERE HM=\"" + user[1] + "\" \
        OR BM1=\"" + user[1] + "\" \
        OR BM2=\"" + user[1] + "\"")
    budget = cur.fetchone()
    cur.close()
    total = 0
    for row in items:
      if row[0] == 'Walmart' and row[3] != None:
        total += row[2]*row[3]
      elif row[4] != None:
        total += row[2]*row[4]
    return render_template("shopping.html", items = items, total = round(total,2), budget = round(budget[0],2))
  else:
    return redirect(url_for('.login'))

@app.route('/update_shopping', methods = ['POST'])
def update_shopping():

  user = session['user_data']

  cur = db_connect.cursor()

  cur.execute("SELECT `Shopping List`\
      FROM House\
      WHERE HM = \"" + user[1] + "\"\
      OR BM1=\"" + user[1] + "\"\
      OR BM2=\"" + user[1] + "\"") 

  result = cur.fetchone()

  if request.form['quantity'] != "-1":
    cur.execute("UPDATE `Shopping List`\
              SET Quantity = " + str(request.form['quantity']) + 
              " WHERE Item = " + str(request.form['upc']) + " AND STORE=\"" +
              str(request.form['store']) + "\" AND ID = " + str(result[0]) + ";")
  else:
    cur.execute("DELETE FROM `Shopping List`\
              WHERE Item = " + str(request.form['upc']) + " AND Store = \"" +
              str(request.form['store']) + "\" AND ID = " + str(result[0]) + ";")

  db_connect.commit()

  cur.close()

  return str(0)

@app.route('/add_shopping', methods = ['POST'])
def add_shopping():
  
  data = request.get_json()

  user = session['user_data']

  cur = db_connect.cursor()

  cur.execute("SELECT `Shopping List`\
      FROM House\
      WHERE HM = \"" + user[1] + "\"\
      OR BM1=\"" + user[1] + "\"\
      OR BM2=\"" + user[1] + "\"") 

  result = cur.fetchone()

  if result and int(data['walmartQuantity']) > 0:
    cur.execute("REPLACE INTO `Shopping List`(ID, Quantity, Item, Store)\
        VALUES(" + str(result[0]) + "," + str(data['walmartQuantity']) + ",\"" +
        str(data['upc']) + "\",\"Walmart\");")

  if result and int(data['costcoQuantity']) > 0:
    cur.execute("REPLACE INTO `Shopping List`(ID, Quantity, Item, Store)\
        VALUES(" + str(result[0]) + "," + str(data['costcoQuantity']) + ",\"" +
        str(data['upc']) + "\",\"Costco\");")

  db_connect.commit()

  cur.close()
  return str(2)

@app.route('/wish')
def wish_list():
  if 'user_data' in session:
    user = session['user_data']

    return render_template("wish.html")#, items = items, total = total)
  else:
    return redirect(url_for('.login'))

@app.route('/login', methods = ['POST','GET'])
def login():
  if request.method == 'GET':
    return render_template("login.html")
  elif request.method == 'POST':
    cur = db_connect.cursor()
    cur.execute("SELECT Name, Username FROM Admin WHERE Username=\"" +
        request.form['lg_username'] + "\" AND Password=\"" +
        request.form['lg_password'] + "\";");
    user_data = cur.fetchone()
    cur.close()
  if user_data:
    session['user_data'] = user_data
    return redirect(url_for('.homepage'))
  else:
    return render_template("login.html", error = "Invalid username/password. Please try again.")

@app.route('/logout')
def logout():
  if 'user_data' in session:
    session.pop('user_data',None)
    return render_template("index.html")

if __name__ == "__main__":
    app.run('0.0.0.0', 2222)
