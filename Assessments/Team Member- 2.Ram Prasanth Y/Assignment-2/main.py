from flask import Flask,render_template,url_for,request,redirect,session
import pandas as pd
import numpy as np
import re
from flask_session import Session
import ibm_db



app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#initializing session
Session(app)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b70af05b-76e4-4bca-a1f5-23dbb4c6a74e.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32716;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=nld81217;PWD=xQrgrKIM3oCr2bVd","","")



@app.route('/')
def home():
    return render_template("/register.html")


@app.route('/user_home')
def user_home():
    return render_template("/inv_index.html")


@app.route('/login_val',methods=["POST"])
def login_val():

    uname = request.form.get("username")
    password = request.form.get("password")

    stmt = ibm_db.exec_immediate(conn, "SELECT * FROM CREDTABLE WHERE USERNAME='"+uname+"'")
    result = ibm_db.fetch_both(stmt)
    print(result)
    if result and result["PASSWORD"] == password:
        session['user'] = uname
        session['email'] = result["EMAIL"]
        return redirect(url_for('user_home'))
    
    return redirect(url_for('login'))


@app.route('/register',methods=["POST","GET"])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    phno = request.form.get('phno')

    ##write to db
    stmt = ibm_db.exec_immediate(conn, "INSERT INTO CREDTABLE VALUES ('"+ username+"','"+password+"','"+email+"','"+phno +"')")


    return redirect(url_for('login_page'))


@app.route('/login_page',methods=["POST","GET"])
def login_page():

    return render_template("login.html")




if __name__ == '__main__':
    app.run(debug=True)
    