# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 01:59:51 2021

@author: wanha
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors
import re
#创建Flask实例
app = Flask(__name__)
app.config['SECRET_KEY']='root'
# 写自己mysql的用户名、密码、主机名、端口和数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/pythlogin"
# 动态追踪数据库的修改. 性能不好. 且未来版本中会移除. 目前只是为了解决控制台的提示才写的
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#创建数据库对象
db = SQLAlchemy(app)

class User(db.Model):
    _tablename_='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=TRUE,index=TRUE)
    role_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))
    
    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/')
def index():
    user=User.query.all()
    return render_template('index.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)