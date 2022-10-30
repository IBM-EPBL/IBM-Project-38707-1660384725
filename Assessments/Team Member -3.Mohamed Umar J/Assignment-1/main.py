from flask import Flask,render_template,url_for,request,redirect
import pandas as pd
import numpy as np
import bcrypt
from datetime import datetime
import re


app = Flask(__name__)

@app.route('/')
def home():
    return render_template("/login.html")

@app.route('/login',methods=["POST"])
def login():
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pat,request.form.get("email")):
        print("Valid Email")
    else:
        return "Invalid Email"
    
    hashed_uname = bcrypt.hashpw(bytes(request.form.get('username') , 'utf-8'),bcrypt.gensalt())
    
    html = "The username is : <b>"+request.form.get('username')+"</b><br> The email is : <b>"+request.form.get("email")+"</b><br> The ph no is :<b>"+request.form.get("phno")+"</b> </br> Thre login time is : <b>" + str(datetime.now())+"</b>"
    return html#request.form.get('phno')





if __name__ == '__main__':
    app.run(debug=True)
    
