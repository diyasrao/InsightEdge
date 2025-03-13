from flask import Flask, render_template, request, redirect
from pathlib import Path
from randomisedString import RandomisedString
from pooledMySQL import PooledMySQL
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder=Path('template'))


sql_pool = PooledMySQL("root", "1505", "insight_edge")
str_gen = RandomisedString()


def create_session(identifier):
    sess_id = str_gen.AlphaNumeric(10, 10)
    sql_pool.execute("INSERT INTO sessions values (?, ?)", [sess_id, identifier])
    return sess_id


@app.get("/")
def _root():
    sess_id = request.cookies.get("sess_id", "")
    if not sql_pool.execute("SELECT user_id from sessions where sess_id = ? LIMIT 1", [sess_id]):
        return render_template("index.html")
    return redirect("/dashboard")



@app.get("/upload")
def _upload_get():
    sess_id = request.cookies.get("sess_id", "")
    if not sql_pool.execute("SELECT user_id from sessions where sess_id = ? LIMIT 1", [sess_id]):
        return redirect("/")
    return render_template("upload.html")


@app.get("/signup")
def _signup_page():
    sess_id = request.cookies.get("sess_id", "")
    if not sql_pool.execute("SELECT user_id from sessions where sess_id = ? LIMIT 1", [sess_id]):
        return render_template("signup.html")
    return redirect("/upload")


@app.get("/login")
def _login_page():
    sess_id = request.cookies.get("sess_id", "")
    if not sql_pool.execute("SELECT user_id from sessions where sess_id = ? LIMIT 1", [sess_id]):
        return render_template("login.html")
    return redirect("/upload")


@app.get("/logout")
def _logout():
    sess_id = request.cookies.get("sess_id", "")
    sql_pool.execute("DELETE FROM sessions where sess_id=?", [sess_id])
    return redirect("/")


@app.post("/signup")
def _signup_post():
    form = request.form.to_dict()
    email = form["email"]
    password = form["password"]
    if not sql_pool.execute("SELECT user_id from auth where email=? LIMIT 1", [email]):
        user_id = str_gen.AlphaNumeric(10,10)
        sql_pool.execute("INSERT INTO auth values (?, ?, ?)", [user_id, email, generate_password_hash(password)])
        sess_id = create_session(user_id)
        response = redirect("/upload")
        response.set_cookie("sess_id", sess_id, max_age=36000,)
        return response
    return render_template("signup.html", error="Invalid credentials")


@app.post("/login")
def _login_post():
    form = request.form.to_dict()
    print(form)
    email = form["email"]
    password = form["password"]
    r = sql_pool.execute("SELECT user_id, pw_hash from auth where email=? LIMIT 1", [email])
    if r:
        r = r[0]
        if check_password_hash(r["pw_hash"], password):
            sess_id = create_session(r["user_id"])
            response = redirect("/upload")
            response.set_cookie("sess_id", sess_id)
            return response
    return render_template("login.html", error="Email already taken")


@app.get("/dashboard")
def _dashboard():
    sess_id = request.cookies.get("sess_id")
    sess = sql_pool.execute("SELECT user_id from sessions where sess_id = ? LIMIT 1", [sess_id])
    if not sess:
        return redirect("/login")
    user_id = sess[0]["user_id"]
    result = sql_pool.execute("SELECT * FROM uploads WHERE user_id=?", [user_id])
    if not result:
        return redirect("/upload")
    result = result[0]
    income = result["income"]
    size = result["size"]
    monthly_expenses = size * 1200 if income < 10000 else size * 3500 if income < 30000 else size * 5000
    remaining = income - monthly_expenses

    if remaining < 5000:
        govt_plan_1 = "< 5000 1"
        govt_plan_2 = "< 5000 2"
        govt_plan_3 = "< 5000 3"
        invst_plan_1 = ""
        invst_plan_2 = ""
        invst_plan_3 = ""
    elif remaining < 15000:
        govt_plan_1 = "< 15000 1"
        govt_plan_2 = "< 15000 2"
        govt_plan_3 = "< 15000 3"
        invst_plan_1 = ""
        invst_plan_2 = ""
        invst_plan_3 = ""
    else:
        govt_plan_1 = "< 5000 1"
        govt_plan_2 = "< 5000 2"
        govt_plan_3 = "< 5000 3"
        invst_plan_1 = ""
        invst_plan_2 = ""
        invst_plan_3 = ""

    return render_template("dashboard.html",
                           income=income,
                           monthly_expenses=monthly_expenses,
                           remaining=remaining,
                           govt_plan_1=govt_plan_1,
                           govt_plan_2=govt_plan_2,
                           govt_plan_3=govt_plan_3,
                           invst_plan_1=invst_plan_1,
                           invst_plan_2=invst_plan_2,
                           invst_plan_3=invst_plan_3)


@app.post("/upload")
def _upload():
    sess_id = request.cookies.get("sess_id")
    sess = sql_pool.execute("SELECT user_id from sessions where sess_id = ? LIMIT 1", [sess_id])
    if not sess:
        return redirect("/login")
    user_id = sess[0]["user_id"]

    form = request.form.to_dict()
    income = int(form["income"])
    size = int(form["size"])
    age = int(form["age"])
    occupation = form["occupation"]
    education = form["education"]
    sql_pool.execute("DELETE FROM uploads WHERE user_id=?", [user_id])
    sql_pool.execute("INSERT INTO uploads values (?, ?, ?, ?, ?, ?)", [user_id, income, size, age, occupation, education])
    return redirect("/dashboard")


@app.errorhandler(404)
def _error_404(e):
    return "Looks like you reached a dead end"

app.run("0.0.0.0", 5000)