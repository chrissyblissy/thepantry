from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://updatepantry:K269210dL1ghtn1ng@localhost/thepantry'
db = SQLAlchemy(app)

class chefs(db.Model):
    __tablename__ = 'chefs'
    chef_id = db.Column(db.Integer, primary_key=True)
    chef_name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return '<chefs %r>' % self.chef_name

class cuisines(db.Model):
    __tablename__ = 'cuisines'
    cuisine_id = db.Column(db.Integer, primary_key=True)
    cuisine_name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return '<cuisines %r>' % self.cuisine_name

class dish_types(db.Model):
    __tablename__ = 'dish_types'
    dish_type_id = db.Column(db.Integer, primary_key=True)
    dish_type_name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return '<dish_types %r>' % self.dish_type_name

class ingredients(db.Model):
    __tablename__ = 'ingredients'
    ingredient_id = db.Column(db.Integer, primary_key=True)
    ingredient_name = db.Column(db.String(40), unique=True, nullable=False)
    ingredient_type = db.Column(db.String(40), nullable=False)
    ingredient_approved = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<ingredients %r>' % (self.ingredient_name)

class recipes(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(60), unique=True, nullable=False)
    cuisine_id = db.Column(db.Integer, db.ForeignKey("cuisines.cuisine_id"), nullable=False)
    chef_id = db.Column(db.Integer, db.ForeignKey("chefs.chef_id"))
    dish_type_id = db.Column(db.Integer, db.ForeignKey("dish_types.dish_type_id"), nullable=False)
    link_book = db.Column(db.String(200))
    page_number = db.Column(db.Integer)
    time = db.Column(db.Integer)
    complexity = db.Column(db.String(20))
    recipe_approved = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<recipes %r>' % self.recipe_name

class recipes_ingredients(db.Model):
    __tablename__ = 'recipes_ingredients'
    recipe_ingredient_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.ingredient_id"), nullable=False)
    ingredient_amount = db.Column(db.String(50))
    
    def __repr__(self):
        return '<recipes_ingredients %r>' % self.recipe_ingredient_id

class users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<users %r>' % self.user_name

class users_recipes(db.Model):
    __tablename__ = 'users_recipes'
    user_recipe_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"), nullable=False)

    def __repr__(self):
        return '<users_recipes %r>' % self.user_recipe_id

class users_ingredients(db.Model):
    __tablename__ = 'users_ingredients'
    user_ingredient_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.ingredient_id"), nullable=False)
    user_ingredient_amount = db.Column(db.String(50))

    def __repr__(self):
        return '<users_ingredients %r>' % self.user_ingredient_id

class users_lists(db.Model):
    __tablename = 'users_lists'
    user_list_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.ingredient_id"), nullable=False)
    list_amount = db.Column(db.String(50))
    
    def __repr__(self):
        return '<users_lists %r>' % self.user_list_id