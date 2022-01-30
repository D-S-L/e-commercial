#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors
import mysql.connector as sql_db
import re
from database import database
import mysql.connector
import datetime


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'root'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dishengl'
app.config['MYSQL_DB'] = 'test'
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
            session['loggedin_admin'] = False
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
   session.pop('loggedin_admin',None)
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        db = database(cursor)
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

            cursor.execute('SELECT id FROM accounts')
            # Fetch one record and return result
            id_set = cursor.fetchall()
            id = id_set[-1]['id']
            cursor.execute('INSERT INTO customer VALUES (%s, NULL, NULL, NULL)', ([id]))
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


        
        cursor.execute('SELECT salesperson_id,salesperson_name FROM salesperson')
        salesperson = cursor.fetchall()
        salesperson = [tuple(i.values()) for i in salesperson ]
        temp = []
        for i in salesperson:
            s = i[1]+'  (worker Id: '+ str(i[0])+")"
            temp.append(s)
        if not temp:
            mydb = sql_db.connect(host=app.config['MYSQL_HOST'], database=app.config['MYSQL_DB'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'])
            mycursor = mydb.cursor()

            sql = "INSERT INTO `salesperson` (`salesperson_id`, `salesperson_name`) VALUES (%s,%s);"
            val = ('1', 'Alis')
            mycursor.execute(sql, val)
            mydb.commit()
            cursor.execute('SELECT salesperson_id,salesperson_name FROM salesperson')
            salesperson = cursor.fetchall()
            salesperson = [tuple(i.values()) for i in salesperson ]
            temp = []
            for i in salesperson:
                s = i[1]+'  (worker Id: '+ str(i[0])+")"
                temp.append(s)


     

        return render_template('home.html', username=session['username'],form = form,products_id=product_id , saleperson = temp)
    # User is not loggedin redirect to login page
    flash('please Login first', 'danger')
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile',methods=['GET', 'POST'])
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        mydb = sql_db.connect(host=app.config['MYSQL_HOST'], database=app.config['MYSQL_DB'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'])
        mycursor = mydb.cursor()
        if request.method == 'POST' :
            address = request.form['address']
            user_name = request.form['user_name']
            if address=='None' and user_name == "None":
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
                account = cursor.fetchone()
                cursor.execute('SELECT name, address FROM customer WHERE id = %s', (session['id'],))
                customer = cursor.fetchall()
                # Show the profile page with account info
                return render_template('profile.html', account=account, customer= customer)

            elif address=='None':
                sql = "UPDATE customer SET name = %s WHERE id = %s;"
                val = (user_name, session['id'])
                mycursor.execute(sql, val)
                mydb.commit()

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
                account = cursor.fetchone()
                cursor.execute('SELECT name, address FROM customer WHERE id = %s', (session['id'],))
                customer = cursor.fetchall()
                dx
                return render_template('profile.html', account=account, customer= customer)


            elif user_name == "None":
                sql = "UPDATE customer SET address = %s WHERE id = %s;"
                val = (address, session['id'])
                mycursor.execute(sql, val)
                mydb.commit()

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
                account = cursor.fetchone()
                cursor.execute('SELECT name, address FROM customer WHERE id = %s', (session['id'],))
                customer = cursor.fetchall()
                return render_template('profile.html', account=account, customer= customer)

            else:
                sql = "UPDATE customer SET name = %s,address = %s WHERE id = %s;"
                val = (user_name,address, session['id'])
                mycursor.execute(sql, val)
                mydb.commit()

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
                account = cursor.fetchone()
                cursor.execute('SELECT name, address FROM customer WHERE id = %s', (session['id'],))
                customer = cursor.fetchall()
                return render_template('profile.html', account=account, customer= customer)



        else:
        # We need all the account info for the user so we can display it on the profile page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
            account = cursor.fetchone()


            cursor.execute('SELECT name, address FROM customer WHERE id = %s', (session['id'],))
            customer = cursor.fetchall()


            # Show the profile page with account info
            return render_template('profile.html', account=account, customer= customer)
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
                cursor.execute(select_stmt, { 'max_v': max_price+1,'min_v': min_price-1, })
                form = cursor.fetchall()
            elif Product_Kind!='':
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s and Kind = %(Product_Kind)s'
                cursor.execute(select_stmt, { 'max_v': max_price+1,'min_v': min_price-1,'Product_Kind':Product_Kind, })
                form = cursor.fetchall()
            elif product_name!='':
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s and name = %(product_name)s'
                cursor.execute(select_stmt, { 'max_v': max_price+1,'min_v': min_price-1,'Product_Kind':Product_Kind,'product_name':product_name })
                form = cursor.fetchall()
            else:
                select_stmt = 'SELECT * FROM products where price<%(max_v)s and price>%(min_v)s and name = %(product_name)s and Kind = %(Product_Kind)s'
                cursor.execute(select_stmt, { 'max_v': max_price+1,'min_v': min_price-1,'Product_Kind':Product_Kind,'product_name':product_name,'Product_Kind':Product_Kind, })
                form = cursor.fetchall()

                ########
            cursor.execute('SELECT salesperson_id,salesperson_name FROM salesperson')
            salesperson = cursor.fetchall()
            salesperson = [tuple(i.values()) for i in salesperson ]
            temp = []
            for i in salesperson:
                s = i[1]+'  (worker Id: '+ str(i[0])+")"
                temp.append(s)

            return render_template('result.html',username=session['username'],form = form,max_price=max_price,min_price=min_price,product_name=product_name,Product_Kind=Product_Kind,saleperson = temp)
    # User is not loggedin redirect to login page
    flash('please Login first', 'danger')
    return redirect(url_for('login'))


def toMysqlDateTime():

    dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return dt


@app.route('/pythonlogin/checkout', methods=['GET', 'POST'])
def checkout():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' :
        # Create variables for easy access
        quantity = int(request.form['quantity'])
        name = request.form['name']

        saleperson = request.form['saleperson']
        
        saleperson_id = int(saleperson[:-1].split()[-1])
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # cursor.execute('SELECT * FROM products WHERE  inventory >= %d and id = 1', ( quantity))
        select_stmt = 'SELECT * FROM products where inventory>=%(quantity)s and name =%(name)s'
        cursor.execute(select_stmt, { 'quantity': quantity,"name":name})
        form = cursor.fetchall()

        if form:   ## update database

            #connect to db
            mydb = sql_db.connect(
                host=app.config['MYSQL_HOST'], database=app.config['MYSQL_DB'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'] )
            

            ## update inventory in products table
            p_id= form[0]['id']
            c_inv = form[0]['inventory']
            up_inv = c_inv-quantity

            mycursor = mydb.cursor()
            sql = "UPDATE products SET inventory = %s WHERE id = %s"
            val = (up_inv, p_id)
            mycursor.execute(sql, val)
            mydb.commit()

            ## insert transaction  record in transaction  table
            select_stmt = 'SELECT order_id FROM transactions '
            cursor.execute(select_stmt)

            id_set = cursor.fetchall()
            if id_set:
                id_c = id_set[-1]['order_id']
                id_up = id_c+1
            else:
                id_up  = 1


            sql = "INSERT INTO transactions (order_id,product_quantity, product_id, date, salesperson_id,customer_id) VALUES (%s,%s, %s,%s, %s,%s)"
            time =toMysqlDateTime()
            val = (id_up,quantity,p_id,time,saleperson_id,session['id'])
            mycursor.execute(sql, val)
            mydb.commit()

        select_stmt = 'SELECT image, price FROM products where name =%(name)s'
        cursor.execute(select_stmt, { "name":name})
        data = cursor.fetchall()
        for i in data:
            price = i['price']
            image = i['image']

        # Fetch one record and return result

        # If account exists in accounts table in out database
        return render_template('checkout.html',form = form,name=name , username=session['username'], quantity= quantity,image=image,price = price)

@app.route('/pythonlogin/complete')
def complete():

    return render_template('success.html', username=session['username'])

#
# http://localhost:5000/pythonlogin/login_admin - this will be the login_admin page, we need to use both GET and POST requests
@app.route('/pythonlogin/login_admin/', methods=['GET', 'POST'])
def login_admin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


        db = database(cursor)
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        admin = cursor.fetchone()
        # If account exists in accounts table in out database
        if admin:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['loggedin_admin'] = True
            session['id'] = admin['id']
            session['username'] = admin['username']
            # Redirect to home page
            return redirect(url_for('a_home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Not Administrative account!'
    return render_template('admin.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/login_admin/a_home/',methods=['GET', 'POST'])
def a_home():
    # Check if user is loggedin
    if 'loggedin_admin' in session:
        # User is loggedin show them the home page
        #########
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id,name,price,inventory,kind,store FROM products WHERE id = (select max(id) from products) ")
        product = cursor.fetchall()
        cursor.execute("SELECT * FROM transactions WHERE order_id = (select max(order_id) from transactions) ")
        transaction = cursor.fetchall()
        return render_template('admin_home.html',product=product,transaction=transaction)
    # User is not loggedin redirect to login page
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/a_manage - this will be the place to edit data by admin
@app.route('/pythonlogin/login_admin/a_manage/',methods=['GET', 'POST'])
def a_manage():
    # Check if user is loggedin
    if 'loggedin_admin' in session:
        tags = ['customer','products','region','salesperson','store','transactions'] 
        ops = ['add', 'edit', 'delete']
        # Show the manage page 
        return render_template('admin_manage.html', tags=tags, ops=ops)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



# http://localhost:5000/pythonlogin/login_admin/a_customer 
@app.route('/pythonlogin/login_admin/a_customer',methods=['GET', 'POST'])
def a_customer():
    msg=''
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        ops = ['add', 'edit', 'delete']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM customer Order BY id")
        customer = cursor.fetchall()
        # Show the manage page 
        return render_template('a_customer.html', customer=customer, ops=ops,msg=msg)
    # admin is not loggedin redirect to login page
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))
    
# http://localhost:5000/pythonlogin/login_admin/a_customer 
@app.route('/pythonlogin/login_admin/a_customer_change',methods=['GET', 'POST'])
def a_customer_change():
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        op_selected = request.form.get('op')
        if op_selected == "add":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM customer Order BY id")
                 customer = cursor.fetchall()
                 return render_template('a_customer_add.html',customer=customer,msg=msg)
        elif op_selected == "edit":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM customer Order BY id")
                 customer = cursor.fetchall()
                 return render_template('a_customer_edit.html',customer=customer,msg=msg)
        elif op_selected == "delete":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM customer Order BY id")
                 customer = cursor.fetchall()
                 return render_template('a_customer_delete.html',customer=customer,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))

@app.route('/pythonlogin/login_admin/a_customer',methods=['GET', 'POST']) 
def a_customer_add():
    msg=''
    if request.method == 'POST' and 'id' in request.form and 'name' in request.form and 'address' in request.form and 'kind' in request.form:
        cid = request.form['id']
        name = request.form['name']
        address = request.form['address']
        kind = request.form['kind']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE id = %s', (cid,))  
        customer = cursor.fetchone()
        # If customer exists show error and validation checks
        if customer:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM customer Order BY id")
            customer = cursor.fetchall()            
            msg = 'Customer already exists!'  
            return render_template('a_customer_add.html',customer=customer,msg=msg)
        elif not re.match(r'[A-Za-z]+',name):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM customer Order BY id")
            customer = cursor.fetchall() 
            msg = 'Invalid name'    
            return render_template('a_customer_add.html',customer=customer,msg=msg)
        elif kind !="business" and kind !="home":
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM customer Order BY id")
            customer = cursor.fetchall() 
            msg = 'Invalid kind'    
            return render_template('a_customer_add.html',customer=customer,msg=msg)
        elif not re.match(r'[0-9]+',cid):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM customer Order BY id")
            customer = cursor.fetchall() 
            msg = 'Invalid ID'  
            return render_template('a_customer_add.html',customer=customer,msg=msg)
        else:
            sql = "INSERT INTO customer (id,name, address, kind) VALUES (%s, %s, %s, %s)"    
            value = (cid, name, address, kind)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully added!')
            return redirect(url_for('a_customer'))
    elif request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM customer Order BY id")
        customer = cursor.fetchall() 
        msg = 'Please fill in！'
        return render_template('a_customer_add.html',msg=msg)


@app.route('/pythonlogin/login_admin/a_customer_edit',methods=['GET', 'POST']) 
def a_customer_edit():
    msg=''
    if request.method == 'POST' and 'id' in request.form:
        cid = request.form['id']
        name = request.form['name']
        address = request.form['address']
        kind = request.form['kind']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE id = %s', (cid,))  
        customer = cursor.fetchone()
        # If customer exists show error and validation checks
        if customer and (kind =="business" or kind =="home"):
            value = (name, address, kind, cid)
            sql= "UPDATE customer SET name = %s, address = %s, kind = %s WHERE id = %s"
            cursor.execute(sql,value)
            mysql.connection.commit()
            flash('You have successfully edited!')
            return redirect(url_for('a_customer'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM customer Order BY id")
            customer = cursor.fetchall() 
            msg = 'Please fill in correct value！'
            return render_template('a_customer_edit.html', customer=customer,msg=msg)
    elif request.method == 'POST':
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM customer Order BY id")
        customer = cursor.fetchall() 
        msg = 'Please fill in！'
        return render_template('a_customer_edit.html', customer=customer, msg=msg)
    

@app.route('/pythonlogin/login_admin/a_customer_delete',methods=['GET', 'POST']) 
def a_customer_delete():
    msg=''
    if request.method == 'POST' and 'id' in request.form:
        cid = request.form['id']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE id = %s', (cid,))  
        customer = cursor.fetchone()
        # If customer exists show error and validation checks
        if customer:
            cursor.execute('DELETE FROM customer WHERE id = %s', (cid,)) 
            mysql.connection.commit()
            flash('You have successfully deleted!')
            return redirect(url_for('a_customer'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM customer Order BY id")
            customer = cursor.fetchall() 
            msg = 'Wrong id！'
            return render_template('a_customer_delete.html', customer=customer, msg=msg)
    elif request.method == 'POST':
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM customer Order BY id")
        customer = cursor.fetchall() 
        msg = 'Please fill in！'
        return render_template('a_customer_delete.html', customer=customer, msg=msg)

# http://localhost:5000/pythonlogin/login_admin/a_product
@app.route('/pythonlogin/login_admin/a_product',methods=['GET', 'POST'])
def a_product():
    msg=''
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        ops = ['add', 'edit', 'delete']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM products Order BY id")
        product = cursor.fetchall()
        # Show the manage page 
        return render_template('a_product.html',product=product, ops=ops,msg=msg)
    # admin is not loggedin redirect to login page
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))
 
@app.route('/pythonlogin/login_admin/a_product_change',methods=['GET', 'POST'])
def a_product_change():
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        op_selected = request.form.get('op')
        if op_selected == "add":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM products Order BY id")
                 product = cursor.fetchall()
                 return render_template('a_products_add.html',product=product,msg=msg)
        elif op_selected == "edit":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM products Order BY id")
                 product = cursor.fetchall()
                 return render_template('a_products_edit.html',product=product,msg=msg)
        elif op_selected == "delete":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM products Order BY id")
                 product = cursor.fetchall()
                 return render_template('a_products_delete.html',product=product,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))

@app.route('/pythonlogin/login_admin/a_products_add',methods=['GET', 'POST']) 
def a_products_add():
    msg=''
    if request.method == 'POST' and 'id' in request.form and 'name' in request.form and 'price' in request.form and 'inventory' in request.form and 'kind' in request.form and 'store' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT store_id FROM store WHERE store_id = %s', (request.form['store'],))  
        store = cursor.fetchone()
        if store:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products Order BY id")
            product = cursor.fetchall() 
            msg = 'No such store!'  
            return render_template('a_products_add.html',product=product,msg=msg)
        cursor.close()
        cid = request.form['id']
        name = request.form['name']
        price = request.form['price']
        inventory = request.form['inventory']
        kind = request.form['kind']
        store = request.form['store']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM products WHERE id = %s', (cid,))  
        product = cursor.fetchone()
        # If customer exists show error and validation checks
        if product:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM productS Order BY id")
            product = cursor.fetchall()  
            msg = 'product already exists!'
            return render_template('a_products_add.html',product=product,msg=msg)
        elif not re.match(r'[0-9]+',cid):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM productS Order BY id")
            product = cursor.fetchall()              
            msg = 'Invalid ID'
            return render_template('a_products_add.html',product=product,msg=msg)
        else:
            sql = "INSERT INTO products (id,name, price, inventory,kind,store) VALUES (%s, %s, %s, %s, %s,%s)"    
            value = (cid, name, price, inventory,kind,store)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully added!')
            return redirect(url_for('a_product'))
    elif request.method == 'POST':
        msg = 'Please fill in！'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM products Order BY id")
        product = cursor.fetchall()  
        return render_template('a_product_add.html',product=product,msg=msg)

@app.route('/pythonlogin/login_admin/a_products_edit',methods=['GET', 'POST']) 
def a_products_edit():
    msg=''
    if request.method == 'POST' and 'id' in request.form and 'store' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT store_id FROM store WHERE store_id = %s', (request.form['store'],))  
        store = cursor.fetchone()
        if store:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products Order BY id")
            product = cursor.fetchall() 
            msg = 'No such store!'  
            return render_template('a_products_edit.html',product=product,msg=msg)
        cursor.close()
        cid = request.form['id']
        name = request.form['name']
        price = request.form['price']
        inventory = request.form['inventory']
        kind = request.form['kind']
        store = request.form['store']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM products WHERE id = %s', (cid,))  
        product = cursor.fetchone()
        # If customer exists show error and validation checks
        if not re.match(r'[A-Za-z0-9]+',name):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products Order BY id")
            product = cursor.fetchall() 
            msg = 'Invalid name'
            return render_template('a_products_edit.html',product=product,msg=msg)
        elif product:
            sql = "UPDATE products SET name = %s, price = %s, inventory = %s, kind = %s, store = %s WHERE id = %s"  
            value = ( name, price, inventory,kind,store,cid)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully edited!')
            return redirect(url_for('a_product'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products Order BY id")
            product = cursor.fetchall() 
            msg = 'Wrong Type'
            return render_template('a_products_edit.html',product=product,msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill in！'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM products Order BY id")
        product = cursor.fetchall() 
        msg = 'No such store!'  
        return render_template('a_products_edit.html',product=product,msg=msg)

@app.route('/pythonlogin/login_admin/a_manage/change/a_products_delete',methods=['GET', 'POST']) 
def a_products_delete():
    msg=''
    if request.method == 'POST' and 'id' in request.form:
        cid = request.form['id']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM products WHERE id = %s', (cid,))  
        product = cursor.fetchone()
        # If customer exists show error and validation checks
        if product:
            cursor.execute('DELETE FROM products WHERE id = %s', (cid,))
            mysql.connection.commit()
            flash('You have successfully deleted!')
            return redirect(url_for('a_product'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products Order BY id")
            product = cursor.fetchall() 
            msg = 'Wrong id！'
            return render_template('a_products_delete.html',product=product,msg=msg)
    elif request.method == 'POST':
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM products Order BY id")
        product = cursor.fetchall() 
        msg = 'Please fill in！'
        return render_template('a_products_delete.html', product=product, msg=msg)

# http://localhost:5000/pythonlogin/login_admin/a_region
@app.route('/pythonlogin/login_admin/a_region',methods=['GET', 'POST'])
def a_region():
    msg=''
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        ops = ['add', 'edit', 'delete']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM region Order BY region_id")
        region = cursor.fetchall()
        # Show the manage page 
        return render_template('a_region.html', region=region, ops=ops,msg=msg)
    # admin is not loggedin redirect to login page
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))
    
@app.route('/pythonlogin/login_admin/a_region_change',methods=['GET', 'POST'])
def a_region_change():
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        op_selected = request.form.get('op')
        if op_selected == "add":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM region Order BY region_id")
                 region = cursor.fetchall()
                 return render_template('a_region_add.html',region=region,msg=msg)
        elif op_selected == "edit":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM region Order BY region_id")
                 region = cursor.fetchall()
                 return render_template('a_region_edit.html',region=region,msg=msg)
        elif op_selected == "delete":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM region Order BY region_id")
                 region = cursor.fetchall()
                 return render_template('a_region_delete.html',region=region,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))


@app.route('/pythonlogin/login_admin/a_region_add',methods=['GET', 'POST']) 
def a_region_add():
    msg=''
    if request.method == 'POST' and 'region_id' in request.form and 'region_name' in request.form and 'region_manager' in request.form:
        cid = request.form['region_id']
        name = request.form['region_name']
        manager = request.form['region_manager']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM region WHERE region_id = %s', (cid,))  
        region = cursor.fetchone()
        if region:
            msg = 'region already exists!'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM region Order BY region_id")
            region = cursor.fetchall()
            return render_template('a_region_add.html',region=region,msg=msg)
        elif not re.match(r'[0-9]+',cid):
            cursor.close()
            msg = 'Invalid ID'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM region Order BY region_id")
            region = cursor.fetchall()
            return render_template('a_region_add.html',region=region,msg=msg)
        else:
            sql = "INSERT INTO region (region_id,region_name, region_manager) VALUES (%s, %s, %s)"    
            value = (cid, name, manager)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully added!')
            return redirect(url_for('a_region'))
    elif request.method == 'POST':
        msg = 'Please fill in！'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM region Order BY region_id")
        region = cursor.fetchall()
        return render_template('a_region_add.html',region=region,msg=msg)

@app.route('/pythonlogin/login_admin/a_region_edit',methods=['GET', 'POST']) 
def a_region_edit():
    msg=''
    if request.method == 'POST' and 'region_id' in request.form:
        cid = request.form['region_id']
        name = request.form['region_name']
        manager = request.form['region_manager']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM region WHERE region_id = %s', (cid,))  
        region = cursor.fetchone()
        if region:
            value = (name, manager,cid)
            sql= "UPDATE region SET region_name = %s, region_manager = %s WHERE region_id = %s"
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully edited!')
            return redirect(url_for('a_region'))
        else:
            cursor.close()
            msg = 'Please fill in correct values！'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM region Order BY region_id")
            region = cursor.fetchall()
            return render_template('a_region_edit.html',region=region,msg=msg)
    elif request.method == 'POST':
            msg = 'Please fill in！'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM region Order BY region_id")
            region = cursor.fetchall()
            return render_template('a_region_edit.html',region=region,msg=msg)

@app.route('/pythonlogin/login_admin/a_region_delete',methods=['GET', 'POST']) 
def a_region_delete():
    if request.method == 'POST' and 'region_id' in request.form:
        cid = request.form['region_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM region WHERE region_id = %s', (cid,))  
        region = cursor.fetchone()
        if region:
            cursor.execute('DELETE FROM region WHERE region_id = %s', (cid,)) 
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully deletedf!')
            return redirect(url_for('a_region'))
        else:
            cursor.close()
            msg = 'Please fill in correct values！'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM region Order BY region_id")
            region = cursor.fetchall()
            return render_template('a_region_delete.html',region=region,msg=msg)
    elif request.method == 'POST':
            msg = 'Please fill in！'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM region Order BY region_id")
            region = cursor.fetchall()
            return render_template('a_region_delete.html',region=region,msg=msg)


# http://localhost:5000/pythonlogin/login_admin/a_salesperson
@app.route('/pythonlogin/login_admin/a_salesperson',methods=['GET', 'POST'])
def a_salesperson():
    msg=''
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        ops = ['add', 'edit', 'delete']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
        salesperson = cursor.fetchall()
        # Show the manage page 
        return render_template('a_salesperson.html',salesperson=salesperson, ops=ops,msg=msg)
    # admin is not loggedin redirect to login page
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))
 
@app.route('/pythonlogin/login_admin/a_salesperson_change',methods=['GET', 'POST'])
def a_salesperson_change():
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        op_selected = request.form.get('op')
        if op_selected == "add":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
                 salesperson = cursor.fetchall()
                 return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        elif op_selected == "edit":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
                 salesperson = cursor.fetchall()
                 return render_template('a_salesperson_edit.html',salesperson=salesperson,msg=msg)
        elif op_selected == "delete":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
                 salesperson = cursor.fetchall()
                 return render_template('a_salesperson_delete.html',salesperson=salesperson,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))


@app.route('/pythonlogin/login_admin/a_salesperson_add',methods=['GET', 'POST']) 
def a_salesperson_add():
    msg=''
    if request.method == 'POST' and 'salesperson_id' in request.form and 'salesperson_name' in request.form and 'address' in request.form and 'email' in request.form and 'title' in request.form and 'store' in request.form and 'salary' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT store_id FROM store WHERE store_id = %s', (request.form['store'],))  
        store = cursor.fetchone()
        if store:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY id")
            salesperson = cursor.fetchall() 
            msg = 'No such store!'  
            return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        cursor.close()
        cid = request.form['salesperson_id']
        name = request.form['salesperson_name']
        address = request.form['address']
        email = request.form['email']
        title = request.form['title']
        store = request.form['store']
        salary = request.form['salary']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM salesperson WHERE salesperson_id = %s', (cid,))  
        salesperson = cursor.fetchone()
        # If customer exists show error and validation checks
        if salesperson:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall()  
            msg = 'Salesperson already exists!'
            return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        elif not re.match(r'[0-9]+',cid):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall()             
            msg = 'Invalid ID'
            return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall()            
            msg = 'Invalid email address!'
            return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        else:
            sql = "INSERT INTO salesperson (salesperson_id,salesperson_name, address, email, title, store, salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"    
            value = (cid, name, address, email, title, store, salary)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully added!')
            return redirect(url_for('a_salesperson'))
    elif request.method == 'POST':
        msg = 'Please fill in！'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM products Order BY salesperson_id")
        salesperson = cursor.fetchall()  
        return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)

@app.route('/pythonlogin/login_admin/a_salesperson_edit',methods=['GET', 'POST'])
def a_salesperson_edit():
    msg=''
    if request.method == 'POST' and 'salesperson_id' in request.form and 'store' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT store_id FROM store WHERE store_id = %s', (request.form['store'],))  
        store = cursor.fetchone()
        if store:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall() 
            msg = 'No such store!'  
            return render_template('a_salesperson_edit.html',salesperson=salesperson,msg=msg)
        cursor.close()
        cid = request.form['salesperson_id']
        name = request.form['salesperson_name']
        address = request.form['address']
        email = request.form['email']
        title = request.form['title']
        store = request.form['store']
        salary = request.form['salary']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM salesperson WHERE salesperson_id = %s', (cid,))  
        salesperson = cursor.fetchone()

        if not re.match(r'[0-9]+',cid):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall()             
            msg = 'Invalid ID'
            return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall()            
            msg = 'Invalid email address!'
            return render_template('a_salesperson_add.html',salesperson=salesperson,msg=msg)
        elif salesperson:
            value = (name, address, email, title, store, salary, cid)
            sql= "UPDATE salesperson SET salesperson_name = %s, address = %s, email = %s, title = %s, store = %s, salary = %s WHERE salesperson_id = %s"
            cursor.execute(sql,value)
            mysql.connection.commit()
            flash('You have successfully edited!')
            return redirect(url_for('a_salesperson'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products salesperson BY salesperson_id")
            salesperson = cursor.fetchall() 
            msg = 'Wrong Type'
            return render_template('a_salesperson_edit.html',salesperson=salesperson,msg=msg)
    elif request.method == 'POST':
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM products salesperson BY salesperson_id")
            salesperson = cursor.fetchall() 
            msg = 'Please Fill in!'
            return render_template('a_salesperson_edit.html',salesperson=salesperson,msg=msg)

@app.route('/pythonlogin/login_admin/a_salesperson_delete',methods=['GET', 'POST'])
def a_salesperson_delete():
    msg=''
    if request.method == 'POST' and 'salesperson_id' in request.form:
        cid = request.form['salesperson_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM salesperson WHERE salesperson_id = %s', (cid,))  
        salesperson = cursor.fetchone()
        if salesperson:
            cursor.execute('DELETE FROM salesperson WHERE salesperson_id = %s', (cid,))
            mysql.connection.commit()
            flash('You have successfully deleted!')
            return redirect(url_for('a_salesperson'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
            salesperson = cursor.fetchall() 
            msg = 'Wrong id！'
            return render_template('a_salesperson_delete.html',salesperson=salesperson,msg=msg)
    elif request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM salesperson Order BY salesperson_id")
        salesperson = cursor.fetchall() 
        msg = 'Please fill in！'
        return render_template('a_salesperson_delete.html', salesperson=salesperson, msg=msg)

# http://localhost:5000/pythonlogin/login_admin/a_store
@app.route('/pythonlogin/login_admin/a_store',methods=['GET', 'POST'])
def a_store():
    msg=''
    if 'loggedin_admin' in session:
        ops = ['add', 'edit', 'delete']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM store Order BY store_id")
        store = cursor.fetchall()
        return render_template('a_store.html', store=store, ops=ops,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))
    
@app.route('/pythonlogin/login_admin/a_store_change',methods=['GET', 'POST'])
def a_store_change():
    if 'loggedin_admin' in session:
        op_selected = request.form.get('op')
        if op_selected == "add":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM store Order BY store_id")
                 store = cursor.fetchall()
                 return render_template('a_store_add.html',store=store,msg=msg)
        elif op_selected == "edit":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM store Order BY store_id")
                 store = cursor.fetchall()
                 return render_template('a_store_edit.html',store=store,msg=msg)
        elif op_selected == "delete":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM store Order BY store_id")
                 store = cursor.fetchall()
                 return render_template('a_store_delete.html',store=store,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))


@app.route('/pythonlogin/login_admin/a_store_add',methods=['GET', 'POST']) 
def a_store_add():
    if request.method == 'POST' and 'store_id' in request.form and 'address' in request.form and 'manager' in request.form and 'num_salesperson' in request.form and 'region' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT region_id FROM region WHERE region_id = %s', (request.form['region'],))  
        region = cursor.fetchone()
        if region:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall() 
            msg = 'No such region!'  
            return render_template('a_store_add.html',store=store,msg=msg)
        cursor.close()
        cid = request.form['store_id']
        address = request.form['address']
        manager = request.form['manager']
        num = request.form['num_salesperson']
        region = request.form['region']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM store WHERE store_id = %s', (cid,))  
        store = cursor.fetchone()

        if store:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall()  
            msg = 'store already exists!'
            return render_template('a_store_add.html',store=store,msg=msg)
        elif not re.match(r'[A-Za-z0-9]+',cid):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall()  
            msg = 'Invalid ID'
            return render_template('a_store_add.html',store=store,msg=msg)
        else:
            sql = "INSERT INTO store (store_id, address, manager, num_salesperson, region) VALUES (%s, %s, %s, %s, %s)"    
            value = (cid, address, manager, num, region)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully added!')
            return redirect(url_for('a_store'))
    elif request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall()  
            msg = 'Please fill in!'
            return render_template('a_store_add.html',store=store,msg=msg)


@app.route('/pythonlogin/login_admin/a_store_edit',methods=['GET', 'POST']) 
def a_store_edit():
    if request.method == 'POST' and 'store_id' in request.form and 'region' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT region_id FROM region WHERE region_id = %s', (request.form['region'],))  
        region = cursor.fetchone()
        if region:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall() 
            msg = 'No such region!'  
            return render_template('a_store_edit.html',store=store,msg=msg)
        cursor.close()
        cid = request.form['store_id']
        address = request.form['address']
        manager = request.form['manager']
        num = request.form['num_salesperson']
        region = request.form['region']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM store WHERE store_id = %s', (cid,))  
        stores = cursor.fetchone()
           
        if not re.match(r'[A-Za-z0-9]+',cid):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall() 
            msg = 'Invalid name'
            return render_template('a_store_edit.html',store=store,msg=msg)
        elif stores:
            sql = "UPDATE store SET address = %s, manager = %s, num_salesperson = %s, region = %s WHERE store_id = %s"  
            value = ( address, manager, num, region, cid)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully edited!')
            return redirect(url_for('a_store'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall() 
            msg = 'Wrong Type'
            return render_template('a_stores_edit.html',store=store,msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill in！'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM store Order BY store_id")
        store = cursor.fetchall() 
        return render_template('a_stores_edit.html',store=store,msg=msg)


@app.route('/pythonlogin/login_admin/a_store_delete',methods=['GET', 'POST']) 
def a_store_delete():
    if request.method == 'POST' and 'store_id' in request.form:
        cid = request.form['store_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM store WHERE store_id = %s', (cid,))  
        store = cursor.fetchone()
        if store:
            cursor.execute('DELETE FROM store WHERE store_id = %s', (cid,)) 
            mysql.connection.commit()
            flash('You have successfully deleted!')
            return redirect(url_for('a_store'))
        else:
            msg = 'Wrong ID！'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM store Order BY store_id")
            store = cursor.fetchall() 
        return render_template('a_stores_edit.html',store=store,msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill in！'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM store Order BY store_id")
        store = cursor.fetchall() 
        return render_template('a_stores_delete.html',store=store,msg=msg)

# http://localhost:5000/pythonlogin/login_admin/a_transactions
@app.route('/pythonlogin/login_admin/a_transactions',methods=['GET', 'POST'])
def a_transactions():
    msg=''
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        ops = ['add', 'edit', 'delete']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM transactions Order BY order_id")
        transaction = cursor.fetchall()
        # Show the manage page 
        return render_template('a_transactions.html',transaction=transaction, ops=ops,msg=msg)
    # admin is not loggedin redirect to login page
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))
 
@app.route('/pythonlogin/login_admin/a_transactions_change',methods=['GET', 'POST'])
def a_transactions_change():
        # Check if admin is loggedin
    if 'loggedin_admin' in session:
        op_selected = request.form.get('op')
        if op_selected == "add":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM transactions Order BY order_id")
                 transaction = cursor.fetchall()
                 return render_template('a_transactions_add.html',transaction=transaction,msg=msg)
        elif op_selected == "edit":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM transactions Order BY order_id")
                 transaction = cursor.fetchall()
                 return render_template('a_transactions_edit.html',transaction=transaction,msg=msg)
        elif op_selected == "delete":
                 msg=''
                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                 cursor.execute("SELECT * FROM transactions Order BY order_id")
                 transaction = cursor.fetchall()
                 return render_template('a_transactions_delete.html',transaction=transaction,msg=msg)
    flash('please Login as Admin', 'danger')
    return redirect(url_for('login'))


@app.route('/pythonlogin/login_admin/a_transactions_add',methods=['GET', 'POST']) 
def a_transactions_add():
    if request.method == 'POST' and 'order_id' in request.form and 'product_id' in request.form and 'product_quantity' in request.form and 'date' in request.form and 'salesperson_id' in request.form and 'customer_id' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id FROM products WHERE id = %s', (request.form['product_id'],))  
        product = cursor.fetchone()
        if product:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'No such product!'  
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT salesperson_id FROM salesperson WHERE salesperson_id = %s', (request.form['salesperson_id'],))  
        salesperson = cursor.fetchone()
        if salesperson:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'No such salesperson!'  
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)       
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id FROM customer WHERE id = %s', (request.form['customer_id'],))  
        customer = cursor.fetchone()
        if customer:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'No such customer!'  
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)  
        
        cursor.close()
        oid = request.form['order_id']
        pid = request.form['product_id']
        pq = request.form['product_quantity']
        date = request.form['date']
        sid = request.form['salesperson_id']
        cid = request.form['customer_id']        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM transactions WHERE order_id = %s ', (oid,))  
        transaction = cursor.fetchone()
        if transaction:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactionS Order BY order_id")
            transaction = cursor.fetchall()  
            msg = 'transaction already exists!'
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)
        elif (not re.match(r'[0-9]+',cid)) or (not re.match(r'[0-9]+',pid)) or (not re.match(r'[0-9]+',sid)):
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactionS Order BY order_id")
            transaction = cursor.fetchall()  
            msg = 'Invalid ID!'
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)
        else:
            sql = "INSERT INTO transactions (order_id, product_id, product_quantity, date, salesperson_id, customer_id) VALUES (%s, %s, %s, %s, %s, %s)"    
            value = (oid, pid, pq, date, sid, cid)
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully added!')
            return redirect(url_for('a_transactions'))
    elif request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactionS Order BY order_id")
            transaction = cursor.fetchall()  
            msg = 'Please fill in!'
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)

@app.route('/pythonlogin/login_admin/a_transactions_edit',methods=['GET', 'POST']) 
def a_transactions_edit():
    if request.method == 'POST' and 'order_id' in request.form and 'product_id' in request.form and 'product_quantity' in request.form and 'date' in request.form and 'salesperson_id' in request.form and 'customer_id' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id FROM products WHERE id = %s', (request.form['product_id'],))  
        product = cursor.fetchone()
        if product:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'No such product!'  
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT salesperson_id FROM salesperson WHERE salesperson_id = %s', (request.form['salesperson_id'],))  
        salesperson = cursor.fetchone()
        if salesperson:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'No such salesperson!'  
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)       
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id FROM customer WHERE id = %s', (request.form['customer_id'],))  
        customer = cursor.fetchone()
        if customer:
            pass
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'No such customer!'  
            return render_template('a_transactions_add.html',transaction=transaction,msg=msg)  
        
        cursor.close()
        oid = request.form['order_id']
        pid = request.form['product_id']
        pq = request.form['product_quantity']
        date = request.form['date']
        sid = request.form['salesperson_id']
        cid = request.form['customer_id']        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM transactions WHERE order_id = %s ', (oid,))  
        transaction = cursor.fetchone()
        if transaction:
            value = (pid, pq, date,sid, cid, oid)
            sql= "UPDATE transactions SET product_id = %s, product_quantity = %s, date = %s, salesperson_id = %s, customer_id = %s WHERE order_id = %s"
            cursor.execute(sql,value)
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully edited!')
            return redirect(url_for('a_transactions'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'Wrong Order'
            return render_template('a_transactions_edit.html',transaction=transaction,msg=msg)
    elif request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'Please fill in!'
            return render_template('a_transactions_edit.html',transaction=transaction,msg=msg)

@app.route('/pythonlogin/login_admin/a_transactions_delete',methods=['GET', 'POST']) 
def a_transactions_delete():
    if request.method == 'POST' and 'order_id' in request.form:
        cid = request.form['order_id']
        #Check if exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM transactions WHERE order_id = %s', (cid,))    
        transaction = cursor.fetchone()
        if transaction:
            cursor.execute('DELETE FROM transactions WHERE order_id = %s ', (cid,))
            mysql.connection.commit()
            flash('You have successfully deleted!')
            return redirect(url_for('a_transactions'))
        else:
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'Wrong Order'
            return render_template('a_transactions_delete.html',transaction=transaction,msg=msg)
    elif request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM transactions Order BY order_id")
            transaction = cursor.fetchall() 
            msg = 'Please fill in!'
            return render_template('a_transactions_delete.html',transaction=transaction,msg=msg)
#
            
# http://localhost:5000/pythinlogin/a_statistics 
@app.route('/pythonlogin/login_admin/a_statistics/',methods=['GET', 'POST'])
def a_statistics():
    # Check if user is loggedin
    if 'loggedin_admin' in session:
        aggregation = ['Sales of Products', 'Top product categories', 'Sales volume among regions', 'Top salesperson'] 
        # Show the manage page 
        return render_template('admin_statistics.html', aggregation=aggregation)
    else:
    # User is not loggedin redirect to login page
        flash('please Login as Admin', 'danger')
        return redirect(url_for('login'))    


@app.route('/pythonlogin/login_admin/a_aggregate/',methods=['GET', 'POST'])
def a_aggregate():
    # Check if user is loggedin
    if 'loggedin_admin' in session:
        selected = request.form.get('aggregate')
        if selected == 'Sales of Products':
                aggregation = ['Sales of Products', 'Top product categories', 'sales volume among regions', 'Top salesperson'] 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("select  t.product_id,p.name,p.price,sum(t.product_quantity) as 'sales_num', (p.price*sum(t.product_quantity)) as 'profits' from transactions t, products p where t.product_id=p.id GROUP BY t.product_id;")
                sales = cursor.fetchall()                  
                return render_template('sales_result.html', aggregation=aggregation, sales=sales)        
        elif  selected == 'Top product categories':
                aggregation = ['Sales of Products', 'Top product categories', 'sales volume among regions', 'Top salesperson'] 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("select  kind,sum(product_quantity) as 'num of sale' from(select * from products p , transactions t where p.id = t.product_id) temp group by kind;")
                products = cursor.fetchall()                      
                return render_template('products_result.html', aggregation=aggregation, products=products)          
        elif  selected == 'Sales volume among regions':  
                aggregation = ['Sales of Products', 'Top product categories', 'sales volume among regions', 'Top salesperson'] 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("select region_id, region_name, sum(product_quantity) as 'volumn of sale', region_manager from region r, store s, transactions t , products p where t.product_id= p.id and p.store=s.store_id and s.region = r.region_id group by region_id;")
                sales = cursor.fetchall()                      
                return render_template('region_sale_result.html', aggregation=aggregation, sales=sales)            
        elif  selected == 'Top salesperson':  
                aggregation = ['Sales of Products', 'Top product categories', 'sales volume among regions', 'Top salesperson'] 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("select salesperson_name,sum(product_quantity) as 'the num of sale' ,address, email, store, salary from transactions t ,salesperson s where t.salesperson_id = s.salesperson_id group by t.salesperson_id order by sum(product_quantity);")
                salesperson = cursor.fetchall()                      
                return render_template('salesperson_result.html', aggregation=aggregation, salesperson=salesperson)  
    else:
        flash('please Login as Admin', 'danger')
        return redirect(url_for('login'))  






if __name__ == '__main__':
    app.run(debug = True)