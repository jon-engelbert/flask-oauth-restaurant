from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, Blueprint
from flask import session as login_session
from flask.ext.sqlalchemy import SQLAlchemy
from flask import make_response

#IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random, string

from app import db
from app.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix = '/auth')

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

#User Helper Functions
def createUser(login_session):
  newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
  db.session.add(newUser)
  db.session.commit()
  user = User.query.filter_by(email = login_session['email']).first()
  return user.id

def getUserInfo(user_id):
  user = User.query.filter_by(id = user_id).first()
  return user

def getUserID(email):
  try:
      user = User.query.filter_by(email = email).first()
      return user.id
  except:
      return None


#Create anti-forgery state token
@mod_auth.route('/login/', methods = ['GET'])
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
  login_session['state'] = state
  #return "The current session state is %s" % login_session['state']
  return render_template('auth/login.html', STATE = state)


@mod_auth.route('/gconnect', methods=['POST'])
def gconnect():
#Validate state token 
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  #Obtain authorization code, now compatible with Python3
  request.get_data()
  code = request.data.decode('utf-8')
  
  try:
    # Upgrade the authorization code into a credentials object
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  
  # Check that the access token is valid.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
         % access_token)
  # Submit request, parse response - Python3 compatible 
  h = httplib2.Http()
  response = h.request(url, 'GET')[1]
  str_response = response.decode('utf-8')
  result = json.loads(str_response)

  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'

  print("result")
  print(result)
  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  print("gplus_id")
  print(gplus_id)
  if result['user_id'] != gplus_id:
    print("result['user_id']")
    response = make_response(
        json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
    response = make_response(
        json.dumps("Token's client ID does not match app's."), 401)
    print("Token's client ID does not match app's.")
    response.headers['Content-Type'] = 'application/json'
    return response

  stored_credentials = login_session.get('credentials_access_token')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('Current user is already connected.'),
                             200)
    response.headers['Content-Type'] = 'application/json'
    return response
    
  print("stored_credentials")
  print(stored_credentials)
  
  # Store the access token in the session for later use.
  login_session['credentials_access_token'] = access_token
  login_session['gplus_id'] = gplus_id
 
  
  #Get user info
  userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt':'json'}
  answer = requests.get(userinfo_url, params=params)
  print("answer")
  print(answer)
  
  data = answer.json()
  print("data")
  print(data)

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']
 
  #see if user exists, if it doesn't make a new one
  user_id = getUserID(data["email"])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = "success"
  # flash("you are now logged in as %s"%login_session['username'])
  # print "done!"
  return output


#DISCONNECT - Revoke a current user's token and reset their login_session
@mod_auth.route('/gdisconnect/')
def gdisconnect():
    #Only disconnect a connected user.
  access_token = login_session.get('credentials_access_token')
  if access_token is None:
    response = make_response(json.dumps('Current user not connected.'),401)
    response.headers['Content-Type'] = 'application/json'
    return response 
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  print("url: " + url)
  h = httplib2.Http()
  response = h.request(url, 'GET')
  result = response[0]

  if result['status'] == '200':
    #Reset the user's sesson.
    del login_session['credentials_access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  else:
    # For whatever reason, the given token was invalid.
    response = make_response(
        json.dumps('Failed to revoke token for given user.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response
