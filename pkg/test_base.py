# flask_testing/test_base.py
from flask.ext.testing import TestCase
from flask import Flask
from pkg import app, db
from pkg.mod_auth.models import Base 
from pkg.mod_auth.models import User
from pkg.mod_auth.controllers import mod_auth
from pkg.mod_restaurant.controllers import mod_restaurant
from pkg.mod_menuitem.controllers import mod_menuitem

import os
import unittest

from config import BASE_DIR
# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class BaseTestCase(TestCase):
	"""A base test case for flask-tracking."""
	# def create_app(self):
	#     app.config.from_object('config.TestConfiguration')
	#     return app

	def create_app(self):
		print("in BaseTestCase: create_app")
		# Define the WSGI application object

		# Configurations
		app.config.from_object('config.TestConfiguration')

		# Define the database object which is imported 
		# by modules and controllers


		# Register blueprint(s)
		app.register_blueprint(mod_auth)
		app.register_blueprint(mod_restaurant)
		app.register_blueprint(mod_menuitem)
		return app

	APPLICATION_NAME= "Restaurant Menu Application"
	def setUp(self):
		print("in BaseTestCase: setUp")
		app = Flask(__name__)
		self.app = app
		self.app.config['TESTING'] = True
		# app.config['WTF_CSRF_ENABLED'] = False
		# self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
		db = SQLAlchemy(app)
		self.debug = True
		print("BaseTestCase: about to db.create_all")
		self.client = self.app.test_client()
		db.create_all()		
		u = User(name='XXXXXXXXXXXXX', email='john@example.com', picture="")
		print("test_add_menuitem: about to db.session.add")
		db.session.add(u)
		print("test_add_menuitem: about to db.session.commit")
		db.session.commit()

		# engine = create_engine('sqlite:///restaurantmenuwithusers.db')
		# Bind the engine to the metadata of the Base class so that the
		# declaratives can be accessed through a DBSession instance
		# Base.metadata.bind = engine

		# session = sessionmaker(bind=engine)
		# A DBSession() instance establishes all conversations with the database
		# and represents a "staging zone" for all the objects loaded into the
		# database session object. Any change made against the objects in the
		# session won't be persisted into the database until you call
		# session.commit(). If you're not happy about the changes, you can
		# revert all of them back to the last commit by calling
		# session.rollback()
		# db.session = session()

	def tearDown(self):
		print("in BaseTestCase: tearDown")
		db.session.remove()
		db.drop_all()
