# from config import BASE_DIR, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
# Import flask and template operators
from flask import Flask, render_template, request, send_from_directory

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

import json
import os

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config.DebugConfiguration')

# Define the database object which is imported 
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

# Import a module/component using its blueprint handler variable (mod_auth)
from app.mod_restaurant.controllers import mod_restaurant as restaurant_module
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_menuitem.controllers import mod_menuitem as menuitem_module

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(restaurant_module)
app.register_blueprint(menuitem_module)

# Build the database
# This will create the database file using SQLAlchemy
db.create_all()

APPLICATION_NAME= "Restaurant Menu Application"

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'restaurant failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/restaurant.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('restaurant startup')

