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

db_connect = pymysql.connect(host=os.getenv('HOST'), port=3306, user=os.getenv(
    'USER'), passwd=os.getenv('PASSWORD'), db=os.getenv('DB'))

app.secret_key = os.getenv('KEY')


@app.route('/')
def homepage():
    if 'user_data' in session:
        user = session['user_data']
        return render_template("home.html", name=user[0], house=user[2], budget=user[3])
    else:
        return render_template("index.html")


#Name, Username - From Admin | Name, Budget, ID - From House

@app.route('/search', methods=['POST'])
def search():
    print("I am in search")
    print(request.form)
    param = request.form['search_param']
    criteria = request.form['search_crit']

    print(param, criteria)

    results = None

    if param:
        results = searchbar.query(param, criteria)

    if results and len(results) == 1:
        print(results)
        brandName, walmartPrice, costcoPrice, name, upc = results[0]

        image = None

        for file in os.listdir('static/product_images'):
            if fnmatch.fnmatch(file, upc + '.*'):
                image = file
                break

        return render_template("product.html", name=name, brand=brandName, upc=upc, wPrice=walmartPrice, cPrice=costcoPrice, image=image)
    else:
        return render_template("search.html", items=results)


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
                        WHERE House.ID = \"" + str(user[4]) + "\" AND UPC = Item)")
        items = cur.fetchall()
        cur.close()
        budget = user[3] 
        total = 0
        for row in items:
            if row[0] == 'Walmart' and row[3] != None:
                total += row[2] * row[3]
            elif row[4] != None:
                total += row[2] * row[4]
        return render_template("shopping.html", items=items, total=round(total, 2), budget=round(budget, 2))
    else:
        return redirect(url_for('.login'))


@app.route('/update_shopping', methods=['POST'])
def update_shopping():

    user = session['user_data']

    cur = db_connect.cursor()

    cur.execute("SELECT `Shopping List`\
            FROM House \
            WHERE House.ID = \"" + str(user[4]) + "\"")
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


@app.route('/add_shopping', methods=['POST'])
def add_shopping():

    data = request.get_json()

    user = session['user_data']

    cur = db_connect.cursor()

    cur.execute("SELECT `Shopping List`\
            FROM House \
            WHERE House.ID = \"" + str(user[4]) + "\"")
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
        print(user)
        cur = db_connect.cursor()
        cur.execute("SELECT Item.UPC, Votes, Name \
                        FROM `Wish List`, Item \
                        WHERE ID = (\
                                SELECT `Wish List` \
                                FROM House \
                                WHERE House.ID = \"" + str(user[4]) + "\") \
                                AND Item.UPC = `Wish List`.UPC \
                                ")
        row = cur.fetchall()
        cur.execute("SELECT Residents\
                        FROM House\
                        WHERE ID = " + str(user[4]))
        residents = cur.fetchone()

        residents = residents[0].split(",")
        print(residents)
        print(type(residents))
        cur.close()
        return render_template("wish.html", items=row, names=residents)
    else:
        return redirect(url_for('.login'))


@app.route('/update_wish', methods=['POST'])
def update_wish():
    user = session['user_data']
    cur = db_connect.cursor()

    cur.execute("SELECT `Wish List`\
        FROM House \
        WHERE House.ID = \"" + str(user[4]) + "\"")
    result = cur.fetchone()

    if request.form['votes'] != "-1":
        cur.execute("UPDATE `Wish List` \
                SET Votes = " + str(request.form['votes']) +
                    " WHERE UPC = " + str(request.form['upc']) +
                    " AND ID = " + str(result[0]) + ";")
    else:
        cur.execute("DELETE FROM `Wish List`\
                            WHERE UPC = " + str(request.form['upc']) + " AND ID = " + str(result[0]) + ";")
    
    db_connect.commit()
    cur.close()

    return str(0)


@app.route('/add_wish', methods=['POST'])
def add_wish():
    data = request.json()
    user = session['user_data']
    cur = db_connect.cursor()

    cur.execute("SELECT `Wish List`\
        FROM House \
        WHERE House.ID = \"" + str(user[4]) + "\"")
    result = cur.fetchone()

    cur.execute("SELECT UPC \
        FROM `Wish List` \
        WHERE ID = " + str(result[0]) + ";")

    allUPC = cur.fetchall()
    duplicate = 0

    for item in allUPC:
        if data['upc'] == item:
            duplicate = 1
            break

    if duplicate == 0 and reuslt:
        cur.execute("REPLACE INTO `Wish List` (ID, UPC, Votes) \
                VALUES (" + str(result[0]) + "," + str(data['upc']) + "," +
                    str(data['votes']) + ");")

    db_connect.commit()
    cur.close()
    return str(2)


@app.route('/login', methods=['POST', 'GET'])
def login():
    print(request.form)
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        cur = db_connect.cursor()
        if request.form['house_user'] == "Select House":
            cur.execute("SELECT Name, Username FROM Admin WHERE Username=\"" +
                request.form['lg_username'] + "\" AND Password=\"" +
                request.form['lg_password'] + "\";")
            user = cur.fetchone()
            cur.execute("SELECT Name, Budget, ID \
                FROM House \
                WHERE HM=\"" + user[1] + "\" \
                OR BM1=\"" + user[1] + "\" \
                OR BM2=\"" + user[1] + "\"")
            house = cur.fetchone()
            cur.close()
            user_data = user + house 
        else:
            cur.execute("SELECT Name, Username FROM Admin WHERE Username=\"" +
                request.form['house_user'] + "\" AND Password=\"" +
                request.form['house_password'] + "\";")
            user = cur.fetchone()
            cur.execute("SELECT Name, Budget, ID \
                FROM House \
                WHERE House.Name LIKE \"" + user[1] + "%\"")
            house = cur.fetchone()
            user_data = user + house 
            cur.close()

    if user_data:
        print(user_data)
        session['user_data'] = user_data
        return redirect(url_for('.homepage'))
    else:
        return render_template("login.html", error="Invalid username/password. Please try again.")


@app.route('/logout')
def logout():
    if 'user_data' in session:
        session.pop('user_data', None)
        return render_template("index.html")


if __name__ == "__main__":
    app.run('0.0.0.0', 2222)
