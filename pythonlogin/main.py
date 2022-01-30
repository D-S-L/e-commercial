#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors
import re
from database import database

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'root'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dishengl'
app.config['MYSQL_DB'] = 'a'

# Intialize MySQL
mysql = MySQL(app)




# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        db = database(cursor)
        #db.establish(cursor)

        # query = "CREATE TABLE IF NOT EXISTS `accounts` (`id` int(11) NOT NULL AUTO_INCREMENT,`username` varchar(50) NOT NULL,`password` varchar(255) NOT NULL,`email` varchar(100) NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"
        # cursor.execute(query)

        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            #flash(msg , 'danger')
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        #flash(msg, 'danger')
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home',methods=['GET', 'POST'])
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        #########
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM products')
        form = cursor.fetchall()
        ########

        cursor.execute('SELECT id FROM products')
        product_id = cursor.fetchall()
     

        return render_template('home.html', username=session['username'],form = form)
    # User is not loggedin redirect to login page
    flash('please Login first', 'danger')
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))





@app.route('/pythonlogin/result',methods=['GET', 'POST'])
def result():
# Check if user is loggedin
    if 'loggedin' in session:
    # User is loggedin show them the home page
    #########
        if request.method == 'POST':
            # Create variables for easy access
            max_price = int(request.form['max_price']) if (request.form['max_price'])!='' else 999999
            product_name = request.form['name']  
            min_price = int(request.form['min_price']) if (request.form['min_price'])!='' else 0
            Product_Kind = request.form['Product Kind'] 

            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            db = database(cursor)
            #db.establish(cursor)

            # query = "CREATE TABLE IF NOT EXISTS `accounts` (`id` int(11) NOT NULL AUTO_INCREMENT,`username` varchar(50) NOT NULL,`password` varchar(255) NOT NULL,`email` varchar(100) NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"
            # cursor.execute(query)


            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if Product_Kind=='' and product_name=='':
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s'
                cursor.execute(select_stmt, { 'max_v': max_price,'min_v': min_price, })
                form = cursor.fetchall()
            elif Product_Kind!='':
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s and Kind = %(Product_Kind)s'
                cursor.execute(select_stmt, { 'max_v': max_price,'min_v': min_price,'Product_Kind':Product_Kind, })
                form = cursor.fetchall()
            elif product_name!='':
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s and name = %(product_name)s'
                cursor.execute(select_stmt, { 'max_v': max_price,'min_v': min_price,'Product_Kind':Product_Kind,'product_name':product_name })
                form = cursor.fetchall()
            else:
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s and name = %(product_name)s and Kind = %(Product_Kind)s'
                cursor.execute(select_stmt, { 'max_v': max_price,'min_v': min_price,'Product_Kind':Product_Kind,'product_name':product_name,'Product_Kind':Product_Kind, })
                form = cursor.fetchall()

                ########

            return render_template('result.html',username=session['username'],form = form)
    # User is not loggedin redirect to login page
    flash('please Login first', 'danger')
    return redirect(url_for('login'))


@app.route('/pythonlogin/checkout', methods=['GET', 'POST'])
def checkout():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' :
        # Create variables for easy access
        quantity = int(request.form['quantity'])
    
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        db = database(cursor)
        #db.establish(cursor)

        # query = "CREATE TABLE IF NOT EXISTS `accounts` (`id` int(11) NOT NULL AUTO_INCREMENT,`username` varchar(50) NOT NULL,`password` varchar(255) NOT NULL,`email` varchar(100) NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"
        # cursor.execute(query)

        # cursor.execute('SELECT * FROM products WHERE  inventory >= %d and id = 1', ( quantity))
        select_stmt = 'SELECT * FROM products where inventory>%(quantity)s'
        cursor.execute(select_stmt, { 'quantity': quantity})
        form = cursor.fetchall()


        # Fetch one record and return result
        form = cursor.fetchall()
        # If account exists in accounts table in out database
        return render_template('checkout.html',form = form)





    

@app.route('/pythonlogin/complete')
def complete():
    return render_template('success.html')


# @app.route('/')
# def test():
#     return render_template('test.html')

if __name__ == '__main__':
    app.run(debug = True)