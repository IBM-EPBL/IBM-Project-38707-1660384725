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

    stmt = ibm_db.exec_immediate(conn, "SELECT USERNAME,PASSWORD FROM CREDTABLE WHERE USERNAME='"+uname+"'")
    result = ibm_db.fetch_both(stmt)
    print(result)
    if result and result["PASSWORD"] == password:
        session['user'] = uname
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



@app.route('/logout_sess')
def logout_sess():
    if "user" in session:
        session.pop('s_username',None)

    return redirect(url_for("login_page"))

@app.route('/view_inventory' , methods=['GET','POST'])
def view_inventory():
    if "user" not in session:
        return redirect(url_for("home"))
    
    lt = []
    stmt = ibm_db.exec_immediate(conn, "SELECT * FROM inventory_table where username='"+session['user']+"';")
    while ibm_db.fetch_row(stmt) != False:
        lt.append({"prod_id":ibm_db.result(stmt, 0),"Item":ibm_db.result(stmt, 1),"Quantity":ibm_db.result(stmt, 2),"Unit":ibm_db.result(stmt, 3),"Treshold":ibm_db.result(stmt, 5)})   
    
    return render_template("view_inventory.html",params=lt)



#route to visit app stocks in inventory
@app.route("/add_inventory",methods=["POST","GET"])
def add_inventory():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("add_inv.html")



#api for adding items into inventory which is called from add_inv.html
@app.route("/add_inv_items" , methods=['GET','POST'])
def add_inv_items():
    if "user" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        print(request.json)
        print("INSERT INTO INVENTORY_TABLE VALUES ('"+ request.json["Prod_id"]+"','"+request.json["Item"]+"',"+request.json["Quantity"]+",'"+request.json["Unit"]+"','"+session['user'] +"',"+request.json["Treshold"]+")")
        print(request)
        #myquery = {"Prod_id":request.json["Prod_id"],"Item": request.json["Item"],"Quantity":float( request.json["Quantity"]),"Treshold":float(request.json["Treshold"]),"Unit":request.json["Unit"]}
        #inv.insert_one(myquery)
        #id = inv.find_one(myquery)["_id"]
        #inv_treshold.insert_one({"Item": request.json["Item"],"Treshold":3,"inv_id":id})
        
        stmt = ibm_db.exec_immediate(conn, "INSERT INTO INVENTORY_TABLE VALUES ('"+ request.json["Prod_id"]+"','"+request.json["Item"]+"',"+request.json["Quantity"]+",'"+request.json["Unit"]+"','"+session['user'] +"',"+request.json["Treshold"]+")")

        print(stmt)
        print("After request")
        return "hello"


#route for removing stocks form inventory
@app.route("/remove_inventory",methods=["GET","POST"])
def remove_inventory():
    if "user" not in session:
        return redirect(url_for("home"))
    lt = []
    stmt = ibm_db.exec_immediate(conn, "SELECT * FROM inventory_table where username='"+session['user']+"';")
    while ibm_db.fetch_row(stmt) != False:
        lt.append({"prod_id":ibm_db.result(stmt, 0),"Item":ibm_db.result(stmt, 1)})   
    
    return render_template("remove_inv.html",params=lt)


#api for remove inventory items called from remove_inv.html
@app.route("/remove_inv_items" , methods=['GET','POST'])
def remove_inv_items():
    if "user" not in session:
            return redirect(url_for("home"))
    if request.method == "POST":
        print(request.json)
        print(request)

        stmt = ibm_db.exec_immediate(conn, "delete from inventory_table where prod_name='"+request.json["Item"]+"';")

        
        print("After request")
        return "hello"


#route for change password of inventory login
@app.route('/ivcpass' , methods=["POST", "GET"])
def ivcpass():
    if "user" not in session:
        return redirect(url_for("home"))
    
    return render_template('ivcpass.html')

#api for changing password for inventory which is called form ivcpass.html
@app.route('/ivcpassword',methods=['GET','POST'])
def ivcpassword():
    if "user" not in session:
        return redirect(url_for("home"))
    msg=""
    if request.method=="POST":
        details=request.form
        name=session['user']
        passw=details['icpassw']
        passw1=details['inpassw']
        npass=details['irnpassw']
        if passw1 != npass:
            return render_template('ivcpass.html')
        stmt = ibm_db.exec_immediate(conn, "SELECT USERNAME,PASSWORD FROM CREDTABLE WHERE USERNAME='"+name+"'")
        result = ibm_db.fetch_both(stmt)
        upass=result["PASSWORD"]
        uname=session['user']
        #search for password and name if name and password in collection allow them to change password
        if upass==passw:
            myquery = "UPDATE CREDTABLE SET PASSWORD='"+passw1+"' WHERE USERNAME='"+uname+"';"
            stmt = ibm_db.exec_immediate(conn, myquery)
            msg="Password Updated Sucessfully!!!"
            return render_template('login.html',msg=msg)
        else:
            msg="Invalid Credentials !! Try Again"
            return render_template('ivcpass.html',msg=msg)

#route for editing the inventory in inventory dashboard
@app.route("/edit_inventory", methods=['GET','POST'])
def edit_inventory():
    if "user" not in session:
        return redirect(url_for("home"))
    lt = []
    stmt = ibm_db.exec_immediate(conn, "SELECT * FROM inventory_table where username='"+session['user']+"';")
    while ibm_db.fetch_row(stmt) != False:
        lt.append({"_id":ibm_db.result(stmt, 0),"Item":ibm_db.result(stmt, 1),"Quantity":ibm_db.result(stmt, 2),"Unit":ibm_db.result(stmt, 3),"Treshold":ibm_db.result(stmt, 5)})   
    
    return render_template("edit_inventory.html",params=lt)


#api for editing inventory item values called from edit_inventory.html
@app.route("/edit_inv_items", methods=['GET','POST'])
def edit_inv_items():
    if "user" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        
        myquery = "UPDATE INVENTORY_TABLE SET PROD_NAME='"+request.json["Item"]+"',QTY="+request.json["Quantity"]+",PROD_UNIT='"+request.json["Unit"]+"' WHERE PROD_ID='"+request.json["_id"]+"';"
        stmt = ibm_db.exec_immediate(conn, myquery)

        #myquery = {"_id": ObjectId(request.json["_id"])}
        #newvalues = { "$set": { "Item":request.json["Item"] , "Quantity":float(request.json["Quantity"]),"Unit":request.json["Unit"]}}
        #inv.update_one(myquery, newvalues)
        
        return "Succes"


#route for set treshold
@app.route("/set_treshold", methods=["POST", "GET"])
def set_treshold():
    if "user" not in session:
        return redirect(url_for("home"))
    
    lt = []
    stmt = ibm_db.exec_immediate(conn, "SELECT * FROM inventory_table where username='"+session['user']+"';")
    while ibm_db.fetch_row(stmt) != False:
        lt.append({"_id":ibm_db.result(stmt, 0),"Item":ibm_db.result(stmt, 1),"Quantity":ibm_db.result(stmt, 2),"Unit":ibm_db.result(stmt, 3),"Treshold":ibm_db.result(stmt, 5)})   

    return render_template("set_treshold.html",params=lt)

#api for set Threshold called form set_treshold.html
@app.route("/change_set_treshold" , methods=["POST","GET"])
def change_set_treshold():
    if "user" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        print("surasdf")
        print("UPDATE INVENTORY_TABLE SET THRESHOLD="+request.json["Treshold"]+" WHERE PROD_ID='"+request.json["_id"]+"';")
        myquery = "UPDATE INVENTORY_TABLE SET THRESHOLD="+request.json["Treshold"]+" WHERE PROD_ID='"+request.json["_id"]+"';"
        stmt = ibm_db.exec_immediate(conn, myquery)
        return "hello"


if __name__ == '__main__':
    app.run(debug=True,port=5002)
    
