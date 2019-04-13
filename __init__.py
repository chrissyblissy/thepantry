import os

from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from tempfile import mkdtemp
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import insert
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

# configure application and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://updatepantry:K269210dL1ghtn1ng@localhost/thepantry'
db = SQLAlchemy(app)
engine = create_engine(
    'mysql://updatepantry:K269210dL1ghtn1ng@localhost/thepantry')
connection = engine.connect()
metadata = MetaData(bind=engine)
sqlsession = sessionmaker(bind=engine)()

### Helper functions ###

# inserts a value into an inputted column if it does not already exist
def insertifnot(columnvalue, value):
    itemexists = False
    for item in db.engine.execute("SELECT * FROM " + columnvalue + "s"):
        if value.lower() == item[1].lower():
            itemexists = True
            return item[0]
    if itemexists == False:
        sqlsession.execute(insert(Table(columnvalue + 's', metadata,
                           autoload=True)).values({columnvalue + "_name": value}))
        lastid = sqlsession.execute(
            "SELECT LAST_INSERT_ID() AS " + columnvalue + "id")
        for row in lastid:
            return row[columnvalue + 'id']

# creates decorators for webpages that users must be logged into to be able to see
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


###### initial pages for registering and logging in ######

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for website."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        inputusername = request.form.get("username").lower()
        inputpassword = request.form.get("password")
        # Ensure username was submitted
        if not inputusername:
            return apology("you must provide a username")

        # Ensure password was submitted
        elif not inputpassword:
            return apology("you must provide a password")

        # Ensure password match
        elif inputpassword != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Hashes the users password
        hashpassword = generate_password_hash(inputpassword)

        for row in db.engine.execute("SELECT user_name FROM users"):
            # checks if username has been taken.
            if inputusername.lower() == row[0].lower():
                return apology("That username has been taken")

        # enter username and hashed password into the users database
        sqlsession.execute(insert(Table('users', metadata, autoload=True)).values({
            "user_name": inputusername,
            "user_hash": hashpassword
        }))

        # Remember which user has logged in
        lastid = sqlsession.execute("SELECT LAST_INSERT_ID() AS user_id")
        for row in lastid:
            session["user_id"] = row['user_id']

        # commit changes to the database
        sqlsession.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        inputusername = request.form.get("username").lower()
        inputpassword = request.form.get("password")
        # Ensure username was submitted
        if not inputusername:
            return apology("you must provide a username")

        # Ensure password was submitted
        elif not inputpassword:
            return apology("must provide password")

        result = db.engine.execute("SELECT * FROM users")
        for row in result:
            # Ensure password is correct
            if row['user_name'] == inputusername:

                if not check_password_hash(row["user_hash"], inputpassword):
                    return apology("Invalid password")

                # Remember which user has logged in
                session["user_id"] = row["user_id"]

                # Redirect user to home page
                return redirect("/")
        # if no usernames match then tell the user
        return apology("That username does not exist")

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


###### available pages once users have logged in ######

# shows all the recipes that the user has added
@app.route("/", methods=['GET', 'POST'])
@login_required
def myrecipes():

    userrecipesinput = "(SELECT recipe_id FROM users_recipes WHERE user_id=" + \
                         str(session.get("user_id")) + ")"
    sqlinput = "SELECT recipes.recipe_name, cuisines.cuisine_name, chefs.chef_name, dish_types.dish_type_name, recipes.link_book, recipes.page_number, recipes.time, recipes.complexity FROM recipes INNER JOIN cuisines ON recipes.cuisine_id=cuisines.cuisine_id INNER JOIN chefs ON recipes.chef_id=chefs.chef_id INNER JOIN dish_types ON recipes.dish_type_id=dish_types.dish_type_id WHERE recipe_id IN " + userrecipesinput + " ORDER BY cuisine_name, recipe_name ASC"
    recipesdata = db.engine.execute(sqlinput)

    return render_template("myrecipes.html", datasheet=recipesdata)

# shows all the different ingredients that the user wants in their inventory
@app.route("/mypantry", methods=['GET', 'POST'])
@login_required
def mypantry():
    if request.method == "POST":
        
            # receives an array of data values = ingredient_id from the matching checkboxes
        result = request.form.getlist("ingredient")

        for ingredientid in result:
            # insert data from HTML form
            sqlsession.execute(insert(Table('users_lists', metadata, autoload=True)).values({
                "user_id": session.get("user_id"),
                "ingredient_id": int(ingredientid)
            }))

        # commit changes to the database
        sqlsession.commit()

        return redirect("/mylist")

    else:
        # renders a table of ingredients ordered by type
        useringredientsinput = "(SELECT ingredient_id FROM users_ingredients WHERE user_id=" + \
                                str(session.get("user_id")) + ")"
        sqlinput = "SELECT ingredient_id, ingredient_name, ingredient_type FROM ingredients WHERE ingredient_id IN " + \
            useringredientsinput + " ORDER BY ingredient_type, ingredient_name ASC"
        ingredientsdata = db.engine.execute(sqlinput)
        return render_template("mypantry.html", datasheet=ingredientsdata)

# shows the users shopping list, added from their inventory or added separately
@app.route("/mylist", methods=['GET', 'POST'])
@login_required
def mylist():

    if request.method == "POST":

        # receives an array of data values = ingredient_id from the matching checkboxes
        removeresult = request.form.getlist("ingredient")
        addresult = request.form.get("addfood")
        if removeresult:
            for ingredientid in removeresult:
                # insert data from HTML form
                removeingredientsinput = "DELETE FROM users_lists WHERE ingredient_id=" + ingredientid
                # commit changes to the database
                db.engine.execute(removeingredientsinput)

            return redirect("/mylist")

        elif addresult and addresult != "":

            # receives food information from HTML form and capitalises it
            food_item = addresult.title()
            ingredientid = None
            ############ MUST BE SANITISED ##############################
            for item in db.engine.execute("SELECT ingredient_id FROM ingredients WHERE ingredient_name = '" + food_item + "'"):
                ingredientid = item[0]
            ############ MUST BE SANITISED ##############################
            if ingredientid is None:
                session['food_item'] = food_item
                return addtype()

            for item in db.engine.execute("SELECT ingredient_id FROM users_lists WHERE user_id=" + str(session.get("user_id"))):
                if ingredientid == item[0]:
                    return apology("That ingredient is already in your shopping list!")

            # insert data from HTML form
            sqlsession.execute(insert(Table('users_lists', metadata, autoload=True)).values({
                "user_id": session.get("user_id"),
                "ingredient_id": ingredientid
            }))

            # commit changes to the database
            sqlsession.commit()

            return redirect("/mylist")
        else:
            return apology("Please select ingredients for your shopping list")

    else:
        userlistinput = "(SELECT ingredient_id FROM users_lists WHERE user_id=" + \
                          str(session.get("user_id")) + ")"
        sqlinput = "SELECT ingredient_id, ingredient_name, ingredient_type FROM ingredients WHERE ingredient_id IN " + \
            userlistinput + " ORDER BY ingredient_type, ingredient_name ASC"
        ingredientsdata = db.engine.execute(sqlinput)
        return render_template("mylist.html", datasheet=ingredientsdata)

# gives the user an opportunity to add recipes to their recipe book
@app.route("/addrecipes", methods=['GET', 'POST'])
@login_required
def addrecipes():

    if request.method == "POST":
        recipe = request.form.get("recipe").title()
        cuisine = request.form.get("cuisine").title()
        dish_type = request.form.get("dishtype").title()
        chef = request.form.get("chef", None).title()
        link = request.form.get("link", None)
        page = request.form.get("page", None)
        time = request.form.get("time", None)
        complexity = request.form.get("complexity", None).title()

        # making sure that data being inputted to database is defined
        for item in db.engine.execute("SELECT recipe_name FROM recipes"):
            if recipe.lower() == item[0].lower():
                return render_template("apology.html", message="That recipe already exists!")

        # checks if cuisine exists in 'cuisines' table and INSERTS it if not
        cuisineid = insertifnot("cuisine", cuisine)
        dish_typeid = insertifnot("dish_type", dish_type)
        if chef == None:
            chefid = None
        else:
            chefid = insertifnot("chef", chef)


        sqlsession.commit()
        # insert data from HTML form
        sqlsession.execute(insert(Table('recipes', metadata, autoload=True)).values({
            "recipe_name": recipe,
            "cuisine_id": cuisineid,
            "dish_type_id": dish_typeid,
            "chef_id": chefid,
            "link_book": link,
            "page_number": page,
            "time": time,
            "complexity": complexity,
            "recipe_approved": True                                                 ############## MUST BE MADE FALSE BEFORE RELEASE ###########
        }))

        # Find out the recipe_id
        lastid = sqlsession.execute("SELECT LAST_INSERT_ID() AS recipe_id")
        for row in lastid:
            recipeid = row['recipe_id']

        sqlsession.execute(insert(Table('users_recipes', metadata, autoload=True)).values({
            "user_id": session.get("user_id"),
            "recipe_id": recipeid
        }))

        # commit changes to the database
        sqlsession.commit()


        return render_template("addrecipes.html")
    else:
        return render_template("addrecipes.html")

# shows a list of all recipes that have been added by users that have also been approved by admin
@app.route("/allrecipes", methods=['GET', 'POST'])
@login_required
def allrecipes():

    if request.method == "POST":

        # receives an array of data values = ingredient_id from the matching checkboxes
        result = request.form.getlist("recipe")

        for recipeid in result:
            # insert data from HTML form
            sqlsession.execute(insert(Table('users_recipes', metadata, autoload=True)).values({
                "user_id": session.get("user_id"),
                "recipe_id": int(recipeid)
            }))

        # commit changes to the database
        sqlsession.commit()

        return redirect("/")

    else:

        recipesdata = db.engine.execute("SELECT recipes.recipe_id, recipes.recipe_name, cuisines.cuisine_name, chefs.chef_name, dish_types.dish_type_name, recipes.link_book, recipes.page_number, recipes.time, recipes.complexity FROM recipes INNER JOIN cuisines ON recipes.cuisine_id=cuisines.cuisine_id INNER JOIN chefs ON recipes.chef_id=chefs.chef_id INNER JOIN dish_types ON recipes.dish_type_id=dish_types.dish_type_id ORDER BY cuisine_name, recipe_name ASC")
        return render_template("allrecipes.html", datasheet=recipesdata)

# gives the user an opportunity to add ingredients to their inventory
@app.route("/addingredients", methods=['GET', 'POST'])
@login_required
def addingredients():

    if request.method == "POST":
        # receives food information from HTML form and capitalises it
        food_item = request.form.get("fooditem").title()
        food_type = request.form.get("foodtype").title()

        for item in db.engine.execute("SELECT ingredient_name FROM ingredients"):
            if food_item.lower() == item[0].lower():
                return apology("That ingredient already exists!")

        # insert data from HTML form
        sqlsession.execute(insert(Table('ingredients', metadata, autoload=True)).values({
            "ingredient_name": food_item,
            "ingredient_type": food_type,
            "ingredient_approved": True                                                 ############## MUST BE MADE FALSE BEFORE RELEASE ###########
        }))

        # commit changes to the database
        sqlsession.commit()

        return render_template("addingredients.html")
    else:
        return render_template("addingredients.html")

# shows a list of all ingredients that have been added by users that have also been approved by admin
@app.route("/allingredients", methods=['GET', 'POST'])
@login_required
def allingredients():

    if request.method == "POST":

        # receives an array of data values = ingredient_id from the matching checkboxes
        result = request.form.getlist("ingredient")

        for ingredientid in result:
            # insert data from HTML form
            sqlsession.execute(insert(Table('users_ingredients', metadata, autoload=True)).values({
                "user_id": session.get("user_id"),
                "ingredient_id": int(ingredientid)
            }))

        # commit changes to the database
        sqlsession.commit()

        return redirect("/mypantry")

    else:

        fooddata = db.engine.execute(
            "SELECT * FROM ingredients ORDER BY ingredient_type, ingredient_name ASC")
        return render_template("allingredients.html", datasheet=fooddata)

# shows an error message if the user does something that is incorrect
@app.route("/apology")
def apology(errormessage):

    return render_template("apology.html", message=errormessage)


# if the user tries to add an unknown ingredient to their list it renders a page asking them to tell them what type of food it is
@app.route("/addtype", methods=['GET', 'POST'])
def addtype():
    return render_template("addtype.html")
# this send the data from addtype() to allingredients() and to the user's shopping list
@app.route("/sendtype", methods=['GET', 'POST'])
def sendtype():
        
        # receives food information from HTML form and capitalises it
        food_item = session.get('food_item', None)
        food_type = request.form.get("foodtype").title()

        # insert data from HTML form
        sqlsession.execute(insert(Table('ingredients', metadata, autoload=True)).values({
            "ingredient_name": food_item,
            "ingredient_type": food_type,
            "ingredient_approved": True                                                 ############## MUST BE MADE FALSE BEFORE RELEASE ###########
        }))

        # Find out the recipe_id
        lastid = sqlsession.execute("SELECT LAST_INSERT_ID() AS recipe_id")
        for row in lastid:
            ingredientid = row['recipe_id']

        # insert data from HTML form
        sqlsession.execute(insert(Table('users_lists', metadata, autoload=True)).values({
            "user_id": session.get("user_id"),
            "ingredient_id": ingredientid
        }))
        # commit changes to the database
        sqlsession.commit()

        return redirect("/mylist")


# runs the Flask app
if __name__ == "__main__":
    app.run()
