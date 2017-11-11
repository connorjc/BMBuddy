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
import buycott
import walmart

dotenv.load_dotenv('.env')

app = Flask(__name__)
Bootstrap(app)

db_connect = pymysql.connect(host=os.getenv('HOST'), port=3306, user=os.getenv('USER'), passwd=os.getenv('PASSWORD'), db=os.getenv('DB') )

app.secret_key = os.getenv('KEY')

def check_hex(num):
    if "&#x" in num:#found hex
        return int(num[3:-1], 16)
    return int(num[2:-1])

@app.route('/search', methods = ['POST'])
def search():
  upc = request.form['upc']
  store = request.form['store']
  if store == "Walmart":
    try:
      brandName, salePrice, name, msrp = walmart.callAPI(upc)
      budget = name
    except TypeError:
      budget = "UPC Not Found"
  else:
    brandName, name = buycott.scrape(upc)
    unicodeObj = re.findall(r"&#[xa-fA-F0-9]*?;", brandName)
    value = brandName
    for uni in unicodeObj:
      value = re.sub(uni, chr(check_hex(uni)), brandName)
    brandName = value

    value = name
    unicodeObj = re.findall(r"&#[xa-fA-F0-9]*?;", name)
    for uni in unicodeObj:
      value = re.sub(uni, chr(check_hex(uni)), name)
      name = value
        
    budget = name
  return render_template("search.html", product_name = name)

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/home')
def homepage():
  if 'user_data' in session:
    user = session['user_data']
    
    cur = db_connect.cursor()

    cur.execute("SELECT Name, Budget FROM House WHERE HM=\"" + user[2] + "\" OR BM1=\"" + user[2] + "\" OR BM2=\"" + user[2] + "\";")

    house = cur.fetchone()

    cur.close()

    return render_template("home.html", name = user[0], house = house[0], budget = house[1])
  else:
    return redirect(url_for('.index'))

@app.route('/login', methods = ['POST','GET'])
def login():
  if request.method == 'GET':
    return render_template("login.html")
  elif request.method == 'POST':
    
    cur = db_connect.cursor()

    cur.execute("SELECT * FROM Admin WHERE Username=\"" +
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
  return redirect(url_for('.index'))

if __name__ == "__main__":
    '''
        port >= 1024 allows for non-root execution
        ssl is required for https
            * fix persmissions for ssl_context
            * or remove bmbuddy.ddns.net from letsencryt
    '''
    app.run('0.0.0.0', 2222)
#ssl_context=("/etc/letsencrypt/live/bmbuddy.ddns.net/fullchain.pem","/etc/letsencrypt/live/bmbuddy.ddns.net/privkey.pem"))
