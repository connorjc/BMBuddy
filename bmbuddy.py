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

@app.route('/search', methods=['POST'])
def search():
    param = request.form['search_param']
    criteria = request.form['search_crit']

    results = None

    if param:
        results = searchbar.query(param, criteria)

    if results and len(results) == 1:
        brandName, walmartPrice, costcoPrice, name, upc = results[0]

        image = None

        for file in os.listdir('static/product_images'):
            if fnmatch.fnmatch(file, upc + '.*'):
                image = file
                break

        if 'user_data' in session:
            user = session['user_data']
            return render_template("product.html", name=name, brand=brandName, upc=upc, wPrice=walmartPrice, cPrice=costcoPrice, image=image, names=user[5], user=user[0])
        return render_template("product.html", name=name, brand=brandName, upc=upc, wPrice=walmartPrice, cPrice=costcoPrice, image=image, names=False)
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

        cur.execute("SELECT COUNT(Item) FROM `Shopping List` WHERE `Shopping List`.ID = (\
                SELECT `Shopping List` \
                FROM House \
                WHERE House.ID = \"" + str(user[4]) + "\")")

        count = cur.fetchone()
        cur.close()
        budget = user[3] 
        total = 0
        for row in items:
            if row[0] == 'Walmart' and row[3] != None:
                total += row[2] * row[3]
            elif row[4] != None:
                total += row[2] * row[4]  
        
        if "Resident" in user[0]:
            return render_template("home.html", name=user[0], house=user[2], budget=user[3])
        else:
            return render_template("shopping.html", items=items,
                total=round(total, 2), budget=round(budget, 2), count=count[0])
    else:
        return redirect(url_for('.login'))

@app.route('/clear_shopping', methods=['POST'])
def clear_shopping():

    user = session['user_data']

    cur = db_connect.cursor()

    cur.execute("DELETE FROM `Shopping List` WHERE ID = (\
                SELECT `Shopping List` \
                FROM House \
                WHERE House.ID = \"" + str(user[4]) + "\")")

    db_connect.commit()

    cur.close()

    return str(1) 

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

@app.route('/fill_wish', methods=['POST'])
def fill_wish():
    return str(1) 

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
        cur = db_connect.cursor()
    
        cur.execute("SELECT Item.UPC, Votees, Name, WalmartPrice, CostcoPrice, Votes \
                        FROM `Wish List`, Item \
                        WHERE ID = (\
                                SELECT `Wish List` \
                                FROM House \
                                WHERE House.ID = \"" + str(user[4]) + "\") \
                                AND Item.UPC = `Wish List`.UPC \
                                GROUP BY Item.UPC, Votees, Votes \
                                ORDER BY Votes desc")
        items = cur.fetchall()
        cur.close()
        items = list(items)
        for index,row in enumerate(items):
          items[index] = (row[0], row[1], row[2], row[3], row[4], row[5])
        print(items)
        if "Resident" in user[0]:
            flag = False
        else:
            flag = True
        print(user)
        return render_template("wish.html", items=items, names=user[5], flag=flag)
    else:
        return redirect(url_for('.login'))

@app.route('/update_wish', methods=['POST'])
def update_wish():
    user = session['user_data']
    cur = db_connect.cursor()

    data = request.get_json()
    
    cur.execute("SELECT `Wish List`\
        FROM House \
        WHERE House.ID = \"" + str(user[4]) + "\"")
    result = cur.fetchone()

    print(result)

    if data['type'] != "delete": 
        cur.execute("SELECT Votees\
            FROM `Wish List`\
            WHERE UPC = " + str(data['upc']) + " AND ID = " +
            str(result[0]) + ";")
        votees = set(cur.fetchone()[0].split(","))
        print(votees)
        if data['resident'] in votees:
            if data['type'] == "down":
                votees.remove(data['resident'])
                print(votees)
                votee_string = ",".join(votees)
                print(votee_string)
                cur.execute("UPDATE `Wish List` \
                    SET Votees = \"" + votee_string + "\", Votes = " +
                    str(len(votees)) + " WHERE UPC = " + str(data['upc']) +
                    " AND ID = " + str(result[0]) + ";")
            else:
              cur.close()
              return str(0) # Resident already voted for item
        else:
            if data['type'] == "up":
                votees.add(data['resident'])
                print(votees)
                votee_string = ",".join(votees)
                print(votee_string)
                cur.execute("UPDATE `Wish List` \
                    SET Votees = \"" + votee_string + "\", Votes = " +
                    str(len(votees)) + " WHERE UPC = " + str(data['upc']) +
                    " AND ID = " + str(result[0]) + ";")
    else:
        cur.execute("DELETE FROM `Wish List`\
            WHERE UPC = " + str(data['upc']) + " AND ID = " + str(result[0]) + ";")
    
    db_connect.commit()
    cur.close()

    return str(2)

@app.route('/add_wish', methods=['POST'])
def add_wish():
    data = request.get_json()
    user = session['user_data']
    cur = db_connect.cursor()

    cur.execute("SELECT `Wish List`\
        FROM House \
        WHERE ID = \"" + str(user[4]) + "\"")
    result = cur.fetchone()

    cur.execute("SELECT UPC \
        FROM `Wish List` \
        WHERE ID = " + str(result[0]) + ";")

    allUPC = cur.fetchall()

    allUPC = (x[0] for x in allUPC)
    print(allUPC)

    if data['upc'] in allUPC:
      cur.execute("SELECT Votees\
            FROM `Wish List`\
            WHERE UPC = \"" + str(data['upc']) + "\" AND ID = " +
            str(result[0]) + ";")
      votees = set(cur.fetchone()[0].split(","))
      print(votees)
      if data['resident'] in votees:
          cur.close()
          return str(1) # Resident already voted for item
      else:
          votees.add(data['resident'])
          print(votees)
          votee_string = ",".join(votees)
          print(votee_string)
          cur.execute("UPDATE `Wish List` \
              SET Votees = \"" + votee_string + "\", Votes = " + 
              str(len(votees)) + " WHERE UPC = " + str(data['upc']) +
              " AND ID = " + str(result[0]) + ";")
    else:
        print(data['upc'])
        cur.execute("INSERT INTO `Wish List` (ID, UPC, Votees, Votes) VALUES (" +
            str(result[0]) + ", \"" + str(data['upc']) + "\", \"" +
            data['resident'] + "\", 1);")
    db_connect.commit()
    cur.close()
    return str(0)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        cur = db_connect.cursor()
        if request.form['house_user'] == "Select House":
            cur.execute("SELECT Name, Username FROM Admin WHERE Username=\"" +
                request.form['lg_username'] + "\" AND Password=\"" +
                request.form['lg_password'] + "\";")
            user = cur.fetchone()
            if user is None:
                return render_template("login.html", error="Invalid username/password. Please try again.")
            cur.execute("SELECT Name, Budget, ID, Residents \
                FROM House \
                WHERE HM=\"" + user[1] + "\" \
                OR BM1=\"" + user[1] + "\" \
                OR BM2=\"" + user[1] + "\"")
            house = cur.fetchone()
            print("PRINTING HOUSE: " + str(house))
            cur.close()
            house = list(house)
            residents = house[3].split(",")
            res = []
            for r in residents: 
                res.append(r.strip())
            res.sort()
            house[3] = res
            user_data = user + tuple(house)
        else:
            cur.execute("SELECT Name, Username FROM Admin WHERE Username=\"" +
                request.form['house_user'] + "\" AND Password=\"" +
                request.form['house_password'] + "\";")
            user = cur.fetchone()
            if user is None:
                return render_template("login.html", error="Invalid username/password. Please try again.")
            cur.execute("SELECT Name, Budget, ID, Residents \
                FROM House \
                WHERE House.Name LIKE \"" + user[1] + "%\"")
            house = cur.fetchone()
            cur.close()
            house = list(house)
            residents = house[3].split(",")
            res = []
            for r in residents: 
                res.append(r.strip())
            res.sort()
            house[3] = res
            user_data = user + tuple(house)
    session['user_data'] = user_data
    print("LOGGING IN:")
    print(user_data)
    return redirect(url_for('.homepage'))

@app.route('/logout')
def logout():
    if 'user_data' in session:
        session.pop('user_data', None)
    return render_template("index.html")

if __name__ == "__main__":
    app.run('0.0.0.0', 2222)
