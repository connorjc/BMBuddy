#!/usr/bin/env python
"""
module docstring
"""

from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import os
import dotenv
import walmart

app = Flask(__name__)
Bootstrap(app)

dotenv.load_dotenv(dotenv.find_dotenv())

app.config['MYSQL_HOST'] = os.getenv('HOST')
app.config['MYSQL_USER'] = os.getenv('USER')
app.config['MYSQL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB')

@app.route('/search', methods = ['POST'])
def search():
    upc = request.form['upc']
    try:
        name, salePrice, msrp, size, = walmart.callAPI(upc)
        budget = name
    except TypeError:
        budget = "UPC Not Found"
    return render_template("index.html", house="ECA", budget=budget)

@app.route('/')
def homepage():
    house = "ECA"
    budget = "505"
    return render_template("index.html", house=house, budget=budget)

if __name__ == "__main__":
    '''
        port >= 1024 allows for non-root execution
        ssl is required for https
            * fix persmissions for ssl_context
            * or remove bmbuddy.ddns.net from letsencryt
    '''
    app.run('0.0.0.0', 2222, ssl_context=("/etc/letsencrypt/live/bmbuddy.ddns.net/fullchain.pem","/etc/letsencrypt/live/bmbuddy.ddns.net/privkey.pem"))
