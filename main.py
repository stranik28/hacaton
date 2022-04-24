from unicodedata import category
from simplecrypt import encrypt
from flask import render_template,Flask, redirect, url_for, request, g, flash, make_response
import sqlite3


passkey = 'hahaton'
app = Flask(__name__)
app.secret_key = 'some_secret'

class FirstPage:
    id = "",
    name = "",
    status = "",
    descript = "",
    start_time = "",
    end_time = "",
    creator = "",
    category = "",
    executor = "",
    def __init__(self,id, name, status,descript,start_time,end_time,creator,category,executor):
        self.name = name,
        self.status = status,
        self.descript = descript,
        self.start_time = start_time,
        self.end_time = end_time,
        self.creator = creator,
        self.category = category,
        self.executor = executor,
        self.id = id


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
        if (login == i[6]) & (encrypt(passw,passkey) == i[7]):
            return True
    return False

def get_task(level):
    cur = connect_db()
    post = cur.execute("SELECT * FROM task WHERE access = " + str(level)+";").fetchall()
    # print(post)
    return post

def get_sur_access_level(login):
    cur = connect_db();
    usr = cur.execute("SELECT access FROM user WHERE login LIKE '" + str(login) + "';").fetchall()
    if len(usr) == 0:
        return 0
    return usr[0][0]


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/",methods =["GET"] )
def welcome_page():
    return redirect(url_for("ctag"))


@app.route("/login", methods = ["GET"])
def login():
    return render_template("login.html")

@app.route("/categories", methods = ["GET"])
def ctag():
    return render_template("categories.html")

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
        name = i[0]
        id = i[2]
        excecutor = i[3]
        creator = i[4]
        descript = i[5]
        start_time = i[6]
        end_time = i[7]
        status = i[8]
        categor = i[9]
        f = FirstPage(id = id,name = name, status=status, descript=descript, start_time=start_time,end_time=end_time,creator=creator,category=categor,executor=excecutor)
        ar.append(f)
    print(len(ar))
    rend = make_response(render_template("main.html", i = ar))
    rend.set_cookie('access',str(lev))
    return rend

@app.route("/main", methods = ["POST"])
def main_post():
    stri = request.cookies.get('access')
    lev = get_sur_access_level(stri)
    lev += 1
    rend = redirect(url_for("main/0"))
    rend.set_cookie('access', str(lev))
    return rend

@app.route("/form_update", methods = ["POST"])
def form_update():
    descript = request.form.get('description')
    start_date = request.form.get('task_start_date1')
    end_date = request.form.get('task_end_date1')
    ategory = request.form.get('task_category')
    access = request.form.get('access_level')
    executor = request.form.get('executor')
    id = request.form.get('idshka')
    con = connect_db();
    f = "UPDATE task SET descript = '"+ str(descript)+  "', start_date = '" + str(start_date) + "', end_date = '"+ str(end_date)  +  "', category = " + str(ategory) +", access = "+ str(access) + ", executor = "+ str(executor) + " WHERE task_id = " + str(id)+  ";"
    print(f)
    con.execute(f)
    return redirect(url_for("main"))


@app.route("/back/", methods= ["POST"])
def back():
    stri = request.cookies.get('login')
    lev = get_sur_access_level(stri)
    if lev != 0:
        lev -= 1
    redi = redirect(url_for("main/0"))
    redi.set_cookie("access",str(lev))
    return redi


@app.route("/add_user", methods = ["POST"])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    photos = request.form.get('phone')
    access = request.form.get('access_level')
    log = request.form.get('login')
    pas = request.form.get('password')
    access = request.form.get('access')
    passek = encrypt(passkey,pas)
    cur = connect_db();
    cur.execute('''INSERT INTO users (name,email,phone,category,access,login,password) VALUES ''' + str(name) + str(email) + str(photos) + str(access) + str(category) + str(access) + str(login) + str(passek) + ";")

if __name__ == "__main__":
    app.run()