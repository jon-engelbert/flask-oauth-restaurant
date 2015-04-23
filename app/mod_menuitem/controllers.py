from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, Blueprint
from flask import session as login_session
import random, string

#IMPORTS FOR THIS STEP
import httplib2
import json
from flask import make_response
import requests

from app import db
from app.mod_auth.models import User
from app.mod_restaurant.models import Restaurant
from app.mod_menuitem.models import MenuItem

# Define the blueprint: 'menuitem', set its url prefix: app.url/menuitem
mod_menuitem= Blueprint('menuitem', __name__, url_prefix = '/menuitem')


#Create a new menu item
@mod_menuitem.route('/<int:restaurant_id>/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
    stored_user_id = login_session.get('user_id')
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    print ("stored_user_id {0}".format(stored_user_id))
    print("login_session: {0}".format(login_session))
    print("restaurant.user_id: {0}".format(restaurant.user_id))
    if 'user_id' not in login_session or ('user_id' in login_session and restaurant.user_id != stored_user_id):
        return redirect('/auth/login')
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id, user_id=restaurant.user_id)
        db.session.add(newItem)
        db.session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        print("menuitem url: {0}".format(url_for('restaurant.showMenu', restaurant_id=restaurant_id)))
        return redirect(url_for('restaurant.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('menuitem/newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item
@mod_menuitem.route('/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(menu_id):
    stored_user_id = login_session.get('user_id')
    editedItem = MenuItem.query.filter_by(id = menu_id).first()
    restaurant = Restaurant.query.filter_by(id=editedItem.restaurant_id).first()
    if 'user_id' not in login_session or ('user_id' in login_session and restaurant.user_id != stored_user_id):
        return redirect('/auth/login')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        db.session.add(editedItem)
        db.session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('restaurant.showMenu', restaurant_id=restaurant.id))
    else:
        return render_template('menuitem/editmenuitem.html', restaurant_id=restaurant.id, menu_id=menu_id, item=editedItem)


#Delete a menu item
@mod_menuitem.route('/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(menu_id):
    stored_user_id = login_session.get('user_id')
    itemToDelete = MenuItem.query.filter_by(id = menu_id).first() 
    restaurant = Restaurant.query.filter_by(id=itemToDelete.restaurant_id).first()
    if 'user_id' not in login_session or ('user_id' in login_session and restaurant.user_id != stored_user_id):
        return redirect('/auth/login')
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('restaurant.showMenu', restaurant_id=restaurant.id))
    else:
        return render_template('menuitem/deleteMenuItem.html', item=itemToDelete)
