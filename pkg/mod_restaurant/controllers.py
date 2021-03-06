from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, Blueprint
from flask import session as login_session
from flask.ext.sqlalchemy import SQLAlchemy
from flask import make_response
from sqlalchemy import desc


import httplib2
import json
import requests
import random, string

from pkg import app
from pkg import db
from pkg.mod_auth.models import User
from pkg.mod_restaurant.models import Restaurant
from pkg.mod_menuitem.models import MenuItem

# Define the blueprint: 'restaurant', set its url prefix: app.url/restaurant
# mod_restaurant= Blueprint('restaurant', __name__, template_folder = '/restaurant')
mod_restaurant= Blueprint('restaurant', __name__, url_prefix = '/restaurant')


#JSON APIs to view Restaurant Information
@mod_restaurant.route('/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = app.db_session.query(Restaurant).filter_by(id = restaurant_id).first()
    items = app.db_session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@mod_restaurant.route('/JSON')
def restaurantsJSON():
    restaurants = app.db_session.query(Restaurant).all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


#Show all restaurants
@app.route('/')
@mod_restaurant.route('/')
def showRestaurants():
  restaurants = app.db_session.query(Restaurant).order_by(Restaurant.name)
  if 'user_id' in login_session:
    print ('user_id in login_session')
    return render_template('restaurant/restaurants.html', restaurants = restaurants)
  else:
    print ('user_id not in login_session')
    return render_template('restaurant/publicrestaurants.html', restaurants= restaurants)

#Create a new restaurant
@mod_restaurant.route('/new/', methods=['GET','POST'])
def newRestaurant():
  print("******!!!!!!!*********  in newRestaurant")
  print("login_session: {0}".format(login_session))
  if 'user_id' not in login_session:
    return redirect('/auth/login')
  if request.method == 'POST':
      newRestaurant = Restaurant(name = request.form['name'], user_id=login_session['user_id'])
      print("restaurant.user_id: {0}".format(newRestaurant.user_id))
      app.db_session.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      app.db_session.commit()
      return redirect(url_for('.showRestaurants'))
  else:
      return render_template('restaurant/newRestaurant.html')

#Edit a restaurant
@mod_restaurant.route('/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'user_id' not in login_session:
      return redirect('/auth/login')
    editedRestaurant = app.db_session.query(Restaurant).filter_by(id = restaurant_id).first()
    if editedRestaurant.user_id != login_session.get('user_id'):
        return redirect('/auth/login')
    if request.method == 'POST':
        print("request.method == POST")
        if request.form['name']:
          editedRestaurant.name = request.form['name']
          app.db_session.add(editedRestaurant)
          app.db_session.commit()
          flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
          return redirect(url_for('restaurant.showRestaurants'))
    else:
        print("request.method != POST")
        return render_template('restaurant/editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@mod_restaurant.route('/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
    if 'user_id' not in login_session:
        return redirect('/auth/login')
    restaurantToDelete = app.db_session.query(Restaurant).filter_by(id = restaurant_id).first()
    if restaurantToDelete.user_id != login_session.get('user_id'):
        return redirect('/auth/login')
    if request.method == 'POST':
        app.db_session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        app.db_session.commit()
        return redirect(url_for('restaurant.showRestaurants'))
    else:
        return render_template('restaurant/deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
@mod_restaurant.route('/<int:restaurant_id>/')
@mod_restaurant.route('/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = app.db_session.query(Restaurant).filter_by(id= restaurant_id).first()
    items = app.db_session.query(MenuItem).filter_by(restaurant_id= restaurant_id).all()
    creator = app.db_session.query(User).filter_by(id = restaurant.user_id).first()
    stored_user_id = login_session.get('user_id')
    if 'user_id' in login_session and restaurant.user_id == stored_user_id:
        print("about to render restaurant/menu.html")
        return render_template('restaurant/menu.html', items=items, restaurant=restaurant, creator=creator)
    else:
        print("about to render restaurant/publicmenu.html")
        return render_template('restaurant/publicmenu.html', items=items, restaurant=restaurant, creator= creator)
     


