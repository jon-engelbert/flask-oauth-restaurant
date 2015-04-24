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



#Create anti-forgery state token
@mod_auth.route('/login/', methods = ['GET'])
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
  login_session['state'] = state
  #return "The current session state is %s" % login_session['state']
  return render_template('auth/login.html', STATE = state)


@mod_auth.route('/fbconnect', methods=['POST'])
def fbconnect():
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  request.get_data()
  access_token = request.data.decode('utf-8')
  print("access token received %s "% access_token)

  #Exchange client token for long-lived server-side token
 ## GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token} 
  app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
  app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
  print("app_id: {0}".format(app_id))
  print("app_secret: {0}".format(app_secret))
  url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id,app_secret,access_token)
  h = httplib2.Http()
  # Submit request, parse response - Python3 compatible 
  response = h.request(url, 'GET')[1]
  print("response: {0}".format(response))
  str_response = response.decode('utf-8')
  print("str_response: {0}".format(str_response))

  #Use token to get user info from API 
  #strip expire tag from access token
  token = str_response.split("&")[0]
  
  url = 'https://graph.facebook.com/v2.2/me?%s' % token
  h = httplib2.Http()
  # Submit request, parse response - Python3 compatible 
  response = h.request(url, 'GET')[1]
  str_response = response.decode('utf-8')
  data = json.loads(str_response)
  #print "url sent for API access:%s"% url
  #print "API JSON result: %s" % result
  login_session['provider'] = 'facebook'
  login_session['username'] = data["name"]
  login_session['email'] = data["email"]
  login_session['facebook_id'] = data["id"]
  #Get user picture
  url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
  h = httplib2.Http()
  # Submit request, parse response - Python3 compatible 
  response = h.request(url, 'GET')[1]
  str_response = response.decode('utf-8')
  data = json.loads(str_response)
  login_session['picture'] = data["data"]["url"]
  # see if user exists
  user_id = User.find_id_by_email(login_session['email'])
  if not user_id:
    user_id = User.create(login_session)
  login_session['user_id'] = user_id
    
  output = ''
  output +='<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output +=' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash ("Now logged in as %s" % login_session['username'])
  return output

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
  #ADD PROVIDER TO LOGIN SESSION
  login_session['provider'] = 'google'

  #see if user exists, if it doesn't make a new one
  user_id = User.find_id_by_email(data["email"])
  if not user_id:
    user_id = User.create(login_session)
  login_session['user_id'] = user_id

  output = "success"
  # flash("you are now logged in as %s"%login_session['username'])
  # print "done!"
  return output


@mod_auth.route('/fbdisconnect')
def fbdisconnect():
  facebook_id = login_session.get('facebook_id')
  url = 'https://graph.facebook.com/%s/permissions' % facebook_id
  h = httplib2.Http()
  result = h.request(url, 'DELETE')[1] 
  return "you have been logged out"


#DISCONNECT - Revoke a current user's token and reset their login_session
@mod_auth.route('/gdisconnect/')
def gdisconnect():
    #Only disconnect a connected user.
  access_token = login_session.get('credentials_access_token')
  print("login_session: {0}".format(login_session))
  if access_token is None:
    response = make_response(json.dumps('Current user not connected.'),401)
    response.headers['Content-Type'] = 'application/json'
    return response 
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  response = h.request(url, 'GET')
  result = response[0]
  if result['status'] != '200':
    # For whatever reason, the given token was invalid.
    response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response

#Disconnect based on provider
@mod_auth.route('/disconnect')
def disconnect():
  print("login_session: {0}".format(login_session))
  if 'username' in login_session:
    if not('provider' in login_session) or login_session['provider'] == 'google':
      gdisconnect()
      del login_session['gplus_id']
      del login_session['credentials_access_token']
    elif login_session['provider'] == 'facebook':
      fbdisconnect()
      del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    flash("You have successfully been logged out.")
    return redirect(url_for('showRestaurants'))
  else:
    flash("You were not logged in")
    return redirect(url_for('showRestaurants'))

