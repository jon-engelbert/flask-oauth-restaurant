# flask_tracking/users/tests.py
from flask import url_for

from app.test_base import BaseTestCase
from app import app, db
from app.mod_auth.models import User


#!flask/bin/python
import os
import unittest

from config import BASE_DIR
from app import app, db
from app.mod_auth.models import User
from app.mod_auth.controllers import mod_auth
from app.mod_restaurant.models import Restaurant
from app.mod_menuitem.models import MenuItem

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        # app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_make_unique_nickname(self):
        u = User(name='john', email='john@example.com', picture="")
        db.session.add(u)
        db.session.commit()
        nickname = User.make_unique_nickname('john')
        assert nickname != 'john'
        u = User(name=nickname, email='susan@example.com', picture="")
        db.session.add(u)
        db.session.commit()
        nickname2 = User.make_unique_nickname('john')
        assert nickname2 != 'john'
        assert nickname2 != nickname

    def test_add_menuitem(self):
        u = User(name='john', email='john@example.com', picture="")
        db.session.add(u)
        db.session.commit()
        r = Restaurant(name='soups r Us', user_id = u.id)
        db.session.add(r)
        db.session.commit()
        mod_auth.newMenuItem(r.id)
        assert MenuItem.query.all() != None

class UserViewsTests(BaseTestCase):
    def test_users_can_login(self):
        User.create(name='Joe', email='joe@joes.com', picture='12345')

        response = self.client.post(url_for('auth.login'),
                                    data={'email': 'joe@joes.com', 'picture': '12345'})

        self.assert_redirects(response, url_for('tracking.index'))