# flask_tracking/users/tests.py
from flask import Flask
from flask import Response
from flask import url_for
from flask import session as login_session
# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase
import flask.ext.testing

# from pkg import app, db
from pkg.test_base import BaseTestCase
from pkg import set_db_session, set_login_session_user_id

from pkg import app
#!flask/bin/python
import os
import unittest
import urllib

from config import BASE_DIR
from pkg import create_app
from pkg.mod_auth.models import User
from pkg.mod_restaurant.models import Restaurant
from pkg.mod_menuitem.models import MenuItem
import pkg.test_base 
import requests
import json

from pkg.mod_auth.controllers import mod_auth as auth_module
from pkg.mod_menuitem.controllers import mod_menuitem as menuitem_module
from pkg.mod_restaurant.controllers import mod_restaurant as restaurant_module


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

class TestCase(TestCase):
    def create_app(self):
        app = self.app = Flask(__name__)
        # self.app_context = self.app.app_context()
        # self.app_context.push()
        app.register_blueprint(auth_module)
        app.register_blueprint(restaurant_module)
        app.register_blueprint(menuitem_module)
        self.app.config['SECRET_KEY'] = 'super_secret_key'
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.db = SQLAlchemy(self.app)
        self.app.debug = True
        with self.app.test_client().session_transaction() as sess:
            sess['user_id'] = 1
        with self.app.test_request_context():
            set_login_session_user_id(1)
            print("In create_app, login_session: {}".format(login_session))
        return self.app

    def setUp(self):
        render_templates = False
        self.db.create_all()
        # self.client = self.app.test_client()
        set_db_session(self.db.session)
        self.client = self.app.test_client(use_cookies = True)
        set_login_session_user_id(1)
        print("In setUp, login_session: {}".format(login_session))

    def tearDown(self):
        self.db.session.query(Restaurant).delete()
        self.db.session.query(MenuItem).delete()
        self.db.session.query(User).delete()
        self.db.session.remove()
        self.db.drop_all()
        self.db.session.commit()

        # self.app_context.pop()


    # def setUp(self):
    #     print("in TestCase:setUp")
    #     self.app = app
    #     self.app.config['TESTING'] = True
    #     # app.config['WTF_CSRF_ENABLED'] = False
    #     self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
    #     db = self.db = SQLAlchemy(self.app)
    #     self.create_app()
    #     self.debug = True
    #     db.create_all()
    #     self.client = self.app.test_client()

    # def tearDown(self):
    #     print("in TestCase: tearDown")
    #     db.session.remove()
    #     db.drop_all()

    def test_add_restaurant(self):
        u = User(name='john', email='john@example.com', picture="")
        self.db.session.add(u)
        self.db.session.commit()
        # newMenuItem(r.id)
        # self.app.app_context().session['user_id'] = 1
        # set_login_session_user_id(1)
        with self.app.test_client(self) as c:
            # login_session['user_id'] = 1
            with c.session_transaction() as sess:
                sess['user_id'] = 1
            response = c.post('/restaurant/new/', data={'name': 'soups r us'}, follow_redirects=False)
            # response = c.post('/restaurant/new/', data={'name': 'soups r us'}, follow_redirects=True)

        # response = app.test_client().post(url_for('restaurant.newRestaurant'), data = {'name': "big daddy's"})
            print("response: {}".format(response.__dict__))
            # assert(Response.status_code == 302)
        lastItem = self.db.session.query(Restaurant).order_by(Restaurant.id.desc()).first()
        print("Restaurant last: {}".format(lastItem.__dict__))
        assert lastItem.name == 'soups r us'

    def test_add_menuitem(self):
        u = User(name='john', email='john@example.com', picture="")
        self.db.session.add(u)
        self.db.session.commit()
        r = Restaurant(name='jons brews')
        self.db.session.add(r)
        self.db.session.commit()
        # newMenuItem(r.id)
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
            response = c.post('/menuitem/1/new/', data=dict(name = 'yummy dog', description= 'you must try this', price= 1, course = 'dessert'), follow_redirects=False)
            print("response: {}".format(response.__dict__))
            # assert(Response.status_code == 302)
        lastItem = self.db.session.query(MenuItem).order_by(MenuItem.id.desc()).first()
        print("menu item last: {}".format(lastItem.__dict__))
        assert lastItem.name == 'yummy dog'

    # def test_list_routes(self):
    #     output = []
    #     for rule in app.url_map.iter_rules():

    #         options = {}
    #         for arg in rule.arguments:
    #             options[arg] = "[{0}]".format(arg)

    #         methods = ','.join(rule.methods)
    #         # url = url_for(rule.endpoint, **options)
    #         # line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
    #         line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
    #         output.append(line)

    #     for line in sorted(output):
    #         print (line)
# class UserViewsTests(BaseTestCase):
#     def test_users_can_login(self):
#         self.app = Flask(__name__)
#         create_app(app, debug=True)
#         User.create(name='Joe', email='joe@joes.com', picture='12345')

#         response = self.client.post(url_for('auth.login'),
#                                     data={'email': 'joe@joes.com', 'picture': '12345'})

#         self.assert_redirects(response, url_for('tracking.index'))

if __name__ == '__main__':
    unittest.main()
