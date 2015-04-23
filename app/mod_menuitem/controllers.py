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

# Define the blueprint: 'menuitem', set its url prefix: app.url/menuitem
mod_menuitem= Blueprint('menuitem', __name__, url_prefix = '/menuitem')


#Create a new menu item
@mod_menuitem.route('/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
    stored_gplus_id = login_session.get('gplus_id')
    if 'username' not in login_session or ('gplus_id' in login_session and restaurant.user_id == stored_gplus_id):
        return redirect('/login')
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id, user_id=restaurant.user_id)
        MenuItem.add(newItem)
        MenuItem.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item
@mod_menuitem.route('/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    stored_gplus_id = login_session.get('gplus_id')
    if 'username' not in login_session or ('gplus_id' in login_session and restaurant.user_id == stored_gplus_id):
        return redirect('/login')
    editedItem = MenuItem.query.filter_by(id = menu_id).one()
    restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        MenuItem.add(editedItem)
        MenuItem.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


#Delete a menu item
@mod_menuitem.route('/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    stored_gplus_id = login_session.get('gplus_id')
    if 'username' not in login_session or ('gplus_id' in login_session and restaurant.user_id != stored_gplus_id):
        return redirect('/login')
    # restaurant = Restaurant.query.filter_by(id = restaurant_id).one()
    itemToDelete = MenuItem.query.filter_by(id = menu_id).one() 
    if request.method == 'POST':
        MenuItem.delete(itemToDelete)
        MenuItem.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)
