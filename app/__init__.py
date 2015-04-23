# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

import json

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported 
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

# Import a module/component using its blueprint handler variable (mod_auth)
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_restaurant.controllers import mod_restaurant as restaurant_module
from app.mod_menuitem.controllers import mod_menuitem as menuitem_module

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(restaurant_module)
app.register_blueprint(menuitem_module)

# Build the database
# This will create the database file using SQLAlchemy
db.create_all()


APPLICATION_NAME= "Restaurant Menu Application"