# flask_tracking/users/tests.py
from flask import Flask
from flask import Response
from flask import url_for
from flask import session as login_session

from pkg.test_base import BaseTestCase
from pkg import app, db
from pkg.mod_auth.models import User
from pkg import set_db_session, set_login_session_user_id

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase
import flask.ext.testing

#!flask/bin/python
import os
import unittest

from config import BASE_DIR
# from pkg import app, db
from pkg.mod_auth.models import User
from pkg.mod_auth.controllers import mod_auth
from pkg.mod_auth.controllers import mod_auth
from pkg.mod_menuitem.controllers import mod_menuitem 
from pkg.mod_restaurant.controllers import mod_restaurant 
from pkg.mod_menuitem.models import MenuItem
import pkg.test_base 
import requests
import json

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"



class UserViewsTests(TestCase):
    def create_app(self):
        app = self.app = Flask(__name__)
        app.register_blueprint(mod_auth)
        app.register_blueprint(mod_restaurant)
        app.register_blueprint(mod_menuitem)
        self.app.config['SECRET_KEY'] = 'super_secret_key'
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.db = SQLAlchemy(self.app)
        self.app.debug = True
        self.client = self.app.test_client(use_cookies = True)
        return self.app

    def setUp(self):
        self.db.create_all()
        # self.client = self.app.test_client()
        set_db_session(self.db.session)
        self.client = self.app.test_client(use_cookies = True)

    def tearDown(self):
        self.db.session.query(User).delete()
        self.db.session.remove()
        self.db.drop_all()
        self.db.session.commit()

    def test_make_unique_nickname(self):
        u = User(name='teddy', email='tb@example.com', picture="")
        self.db.session.add(u)
        self.db.session.commit()
        db = self.db
        pkg.db = db
        nickname = User.make_unique_nickname('john')
        assert nickname != 'john'
        u = User(name=nickname, email='susan@example.com', picture="")
        self.db.session.add(u)
        self.db.session.commit()
        nickname2 = User.make_unique_nickname('john')
        assert nickname2 != 'john'
        assert nickname2 != nickname

    def test_users_can_login(self):
        u = User(name='Joe', email='joe@joes.com', picture='12345')
        self.db.session.add(u)
        self.db.session.commit()

        response = app.test_client(self).get('/login',  follow_redirects=False)
        # response = self.client.post(url_for('auth.login'), data={'email': 'joe@joes.com', 'picture': '12345'})

        # self.assert_redirects(response, url_for('tracking.index'))
