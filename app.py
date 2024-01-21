from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology
from cs50 import SQL
import datetime

app = Flask(__name__)

# db = SQLAlchemy(app)
db = SQL("sqlite:///meals.db")


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    if request.method == "POST":
        mealId = request.form.get("mealId")
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        today_order = db.execute("SELECT * FROM meal_records JOIN shops ON meal_records.shop_id = shops.id WHERE time = (?)", today)
        user_meal_records = db.execute("SELECT * FROM user_meal_records JOIN meals ON user_meal_records.meal_id = meals.id WHERE user_id = (?) AND meal_record_id = (?)", user_id, today_order[0]['id'])
        if (len(user_meal_records) > 0):
          db.execute("UPDATE user_meal_records SET meal_id = (?) WHERE user_id = (?) AND meal_record_id = (?)", mealId, user_id, today_order[0]['id'])
        else:
          db.execute("INSERT INTO user_meal_records (user_id, meal_record_id, meal_id) VALUES (?, ?, ?)", user_id, today_order[0]['id'], mealId)
        user_meal_records = db.execute("SELECT * FROM user_meal_records JOIN meals ON user_meal_records.meal_id = meals.id WHERE user_id = (?) AND meal_record_id = (?)", user_id, today_order[0]['id'])
        meals = db.execute("SELECT meals.id, meals.name, meals.price FROM meals WHERE meals.shop_id = (?)", today_order[0]['shop_id'])

        return render_template("index.html", meals=meals, today_order=today_order[0], user_meal_records=user_meal_records)
    else:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        today_order = db.execute("SELECT * FROM meal_records JOIN shops ON meal_records.shop_id = shops.id WHERE time = (?)", today)
        if today_order.__len__() == 0:
            return render_template("index.html", meals=[], today_order=[], user_meal_records=[])
        meals = db.execute("SELECT meals.id, meals.name, meals.price FROM meals WHERE meals.shop_id = (?)", today_order[0]['shop_id'])
        user_meal_records = db.execute("SELECT * FROM user_meal_records JOIN meals ON user_meal_records.meal_id = meals.id WHERE user_id = (?) AND meal_record_id = (?)", user_id, today_order[0]['id'])

    return render_template("index.html", meals=meals, today_order=today_order[0], user_meal_records=user_meal_records)

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
      mealdate = request.form.get("mealdate")
      order = db.execute("SELECT * FROM meal_records JOIN shops ON meal_records.shop_id = shops.id WHERE time = (?)", mealdate)
      if order.__len__() == 0:
        return render_template("order.html", today_order=[], user_meal_records=[], total_price=0)
      user_meal_records = db.execute("SELECT * FROM user_meal_records JOIN meal_records ON user_meal_records.meal_record_id = meal_records.id JOIN meals ON user_meal_records.meal_id = meals.id JOIN users ON user_meal_records.user_id = users.id WHERE time = (?)", mealdate)
      total_price = 0
      for record in user_meal_records:
        total_price += record['price']
      return render_template("order.html", today_order=order[0], user_meal_records=user_meal_records, total_price=total_price)
    else:
      today = datetime.date.today()
      yesterday = today - datetime.timedelta(days=1)
      today_order = db.execute("SELECT * FROM meal_records JOIN shops ON meal_records.shop_id = shops.id WHERE time = (?)", today)
      if today_order.__len__() == 0:
        return render_template("order.html", today_order=[], user_meal_records=[], total_price=0)
          
      user_meal_records = db.execute("SELECT * FROM user_meal_records JOIN meals ON user_meal_records.meal_id = meals.id JOIN users ON user_meal_records.user_id = users.id WHERE meal_record_id = (?)", today_order[0]['id'])
      total_price = 0
      for record in user_meal_records:
        total_price += record['price']
      return render_template("order.html", today_order=today_order[0], user_meal_records=user_meal_records, total_price=total_price)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Access form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must Give Username")

        if not password:
            return apology("Must Give Password")

        if not confirmation:
            return apology("Must Give Confirmation")

        if password != confirmation:
            return apology("Password Do Not Match")
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        except:
            return apology("Username already exists")

        # Remember which user has logged in
        session["user_id"] = new_user
        return redirect("/")
    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        # "SELECT * FROM users WHERE username = ?", request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/new-shop", methods=["GET", "POST"])
def newShop():
    if request.method == "POST":
        # Ensure username was submitted
        shopname = request.form.get("shopname")
        if not shopname:
            return apology("must provide shop name", 403)
        try:
            db.execute("INSERT INTO shops (name) VALUES (?)", shopname)
            shops = db.execute("SELECT * FROM shops")
        except:
            return apology("Shop already exists")
        
        return render_template("new-shop.html", shops=shops)
    else:
      # Redirect user to new-shop form
      shops = db.execute("SELECT * FROM shops")

      return render_template("new-shop.html", shops=shops)

@app.route("/new-meal", methods=["GET", "POST"])
def newMeal():
    if request.method == "POST":
        # Ensure username was submitted
        mealname = request.form.get("mealname")
        mealprice = request.form.get("mealprice")
        shopid = request.form.get("shopid")
        if not mealname:
            return apology("must provide meal name", 403)
        if not mealprice:
            return apology("must provide meal price", 403)

        try:
            db.execute("INSERT INTO meals (name, price, shop_id) VALUES (?, ?, ?)", mealname, int(mealprice), shopid)
            # CREATE TABLE meals (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, price NUMBER NO NULL, shop_id INTEGER,FOREIGN KEY(shop_id) REFERENCES shop(id));
            meals = db.execute("SELECT * FROM meals JOIN shops ON meals.shop_id = shops.id")
        except:
            return apology("Shop already exists")
        meals = db.execute("SELECT meals.id, meals.name, meals.price, meals.shop_id, shops.name AS shop_name FROM meals INNER JOIN shops ON meals.shop_id = shops.id")

        shops = db.execute("SELECT * FROM shops")
        return render_template("new-meal.html", shops=shops, meals=meals)
    else:
    # Redirect user to new-meal form
      # meals = db.execute("SELECT * FROM meals INNER JOIN shops ON meals.shop_id = shops.id")
      # chang column name
      meals = db.execute("SELECT meals.id, meals.name, meals.price, meals.shop_id, shops.name AS shop_name FROM meals INNER JOIN shops ON meals.shop_id = shops.id")
      shops = db.execute("SELECT * FROM shops")
      return render_template("new-meal.html", shops=shops, meals=meals)


@app.route("/group", methods=["GET", "POST"])
def group():
    if request.method == "POST":
        # Ensure username was submitted
        mealdate = request.form.get("mealdate")
        shopid = request.form.get("shopid")
        if not mealdate:
            return apology("must provide meal date", 403)
        if not shopid:
            return apology("must provide shop id", 403)
        try:
            db.execute("INSERT INTO meal_records (time, shop_id) VALUES (?, ?)", mealdate, shopid)
            meal_records = db.execute("SELECT * FROM meal_records JOIN shops ON meal_records.shop_id = shops.id")
        except:
            return apology("Group already exists")
        
        return render_template("group.html", records=meal_records)
    else:
      # Redirect user to new-shop form
      shops = db.execute("SELECT * FROM shops")
      meal_records = db.execute("SELECT * FROM meal_records JOIN shops ON meal_records.shop_id = shops.id")
      return render_template("group.html", shops=shops, records=meal_records)


if __name__ =="__main__":
    app.run(debug=True)