from crypt import methods
from xmlrpc.client import Boolean
from flask import render_template,Flask, redirect, url_for, request, g, flash, make_response
import sqlite3

app = Flask(__name__)
app.secret_key = 'some_secret'

class FirstPage:
    name = "",
    status = "",
    def __init__(self,name, status):
        self.name = name,
        self.status = status


def connect_db():
    DATABASE = "database/hac.sql"
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def is_correct(login, passw):
    cur = connect_db()
    post = cur.execute('SELECT * FROM user').fetchall()
    for i in post:
        print(i)
        print(login)
        print(passw)
        if (login == i[6]) & (passw == i[7]):
            print("Ok")
            return True
    return False

def get_task(level):
    cur = connect_db()
    post = cur.execute("SELECT * FROM task WHERE access = " + str(level) + ";").fetchall()
    return post

def get_sur_access_level(login):
    cur = connect_db();
    usr = cur.execute("SELECT access FROM user WHERE login LIKE '" + str(login) + "';").fetchall()
    return usr[0][0]


@app.teardown_appcontext
def close_connection(exception):
    """Закрывает соединение c БД"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/",methods =["GET"] )
def welcome_page():
    return redirect(url_for("login"))

@app.route("/login", methods = ["GET"])
def login():
    return render_template("login.html")

@app.route("/login", methods = ["POST"])
def login_odi():
    login = request.form.get("logg")
    password = request.form.get("password")
    if is_correct(login= login, passw = password) == True:
        redi = redirect(url_for("main"))
        redi.set_cookie("login",login)
        return redi
    else:
        flash("Hеправильный логин/пароль")
        return redirect(url_for("login"))


@app.route("/main", methods = ["GET"])
def main():
    stri = request.cookies.get('access')
    lev = 0
    if stri != None:
        lev = stri
    else:
        login = request.cookies.get('login')
        if login != None:
            lev = get_sur_access_level(login)
    ak = get_task(lev)
    ar = []
    for i in ak:
        a = i[0]
        b = i[9]
        f = FirstPage(a,b)
        ar.append(f)
    rend = make_response(render_template("main.html", datas = ar))
    rend.set_cookie('access',str(lev))
    return rend

@app.route("/main", methods = ["POST"])
def main_post():
    stri = request.cookies.get('access')
    lev = get_sur_access_level(stri)
    lev += 1
    rend = redirect(url_for("main"))
    rend.set_cookie('access', str(lev))
    return rend

@app.route("/back/", methods= ["POST"])
def back():
    stri = request.cookies.get('login')
    lev = get_sur_access_level(stri)
    if lev != 0:
        lev -= 1
    redi = redirect(url_for("main"))
    redi.set_cookie("access",str(lev))
    return redi

if __name__ == "__main__":
    app.run()