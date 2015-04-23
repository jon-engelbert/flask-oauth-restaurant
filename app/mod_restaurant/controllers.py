from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, Blueprint
from flask import session as login_session
from flask.ext.sqlalchemy import SQLAlchemy
from flask import make_response
from sqlalchemy import desc


import httplib2
import json
import requests
import random, string

from app import app
from app import db
from app.mod_auth.models import User
from app.mod_restaurant.models import Restaurant
from app.mod_menuitem.models import MenuItem

# Define the blueprint: 'restaurant', set its url prefix: app.url/restaurant
mod_restaurant= Blueprint('restaurant', __name__, url_prefix = '/restaurant')


#JSON APIs to view Restaurant Information
@mod_restaurant.route('/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    items = MenuItem.query.filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@mod_restaurant.route('/JSON')
def restaurantsJSON():
    restaurants = Restaurant.query.all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


#Show all restaurants
@app.route('/')
@mod_restaurant.route('/')
def showRestaurants():
  restaurants = Restaurant.query.order_by(Restaurant.name)
  if 'user_id' in login_session:
    return render_template('restaurant/restaurants.html', restaurants = restaurants)
  else:
    return render_template('restaurant/publicrestaurants.html', restaurants= restaurants)

#Create a new restaurant
@mod_restaurant.route('/new/', methods=['GET','POST'])
def newRestaurant():
  if 'username' not in login_session:
    return redirect('/login')
  if request.method == 'POST':
      newRestaurant = Restaurant(name = request.form['name'], user_id=login_session['user_id'])
      Restaurant.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      session.commit()
      return redirect(url_for('restaurant/showRestaurants'))
  else:
      return render_template('restaurant/newRestaurant.html')

#Edit a restaurant
@mod_restaurant.route('/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
      return redirect('/auth/login')
    editedRestaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    if editedRestaurant.user_id == login_session.get('user_id'):
        return redirect('/auth/login')
    if request.method == 'POST':
        if request.form['name']:
          editedRestaurant.name = request.form['name']
          flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
          return redirect(url_for('restaurant/showRestaurants'))
    else:
      return render_template('restaurant/editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@mod_restaurant.route('/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/auth/login')
    restaurantToDelete = Restaurant.query.filter_by(id = restaurant_id).first()
    if restaurantToDelete.user_id != login_session.get('user_id'):
        return redirect('/auth/login')
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('restaurant/showRestaurants', restaurant_id = restaurant_id))
    else:
        return render_template('restaurant/deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
@mod_restaurant.route('/<int:restaurant_id>/')
@mod_restaurant.route('/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id= restaurant_id).first()
    items = MenuItem.query.filter_by(restaurant_id= restaurant_id).all()
    creator = User.query.filter_by(id = restaurant.user_id).first()
    stored_gplus_id = login_session.get('gplus_id')
    if 'gplus_id' in login_session and restaurant.user_id == stored_gplus_id:
        return render_template('restaurant/menu.html', items=items, restaurant=restaurant, creator=creator)
    else:
        return render_template('menuitem/publicmenu.html', items=items, restaurant=restaurant, creator= creator)
     


