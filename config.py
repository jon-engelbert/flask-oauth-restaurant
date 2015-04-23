# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
	DEBUG = False
	TESTING = False
	# Secret key for signing cookies
	SECRET_KEY = 'insecure-secret'
	HASH_ROUNDS = 100000
	# Define the database - we are working with 
	# SQLite for this example
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'restaurantmenuwithusers.db')
	SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
	SQLALCHEMY_ECHO = True
	DATABASE_CONNECT_OPTIONS = {}

	# Application threads.  A common general assumption is
	# using 2 per available processor cores - to handle
	# incoming requests using one and performing background 
	# operations using the other.
	THREADS_PER_PAGE = 2

	# Enable protection against *Cross-site Request Forgery (CSRF)*
	CSRF_ENABLED     = True

	# Use a secure, unique and absolutely secret key for
	# signing the data. 
	CSRF_SESSION_KEY = "secret"


	# mail server settings
	MAIL_SERVER = 'localhost'
	MAIL_PORT = 25
	MAIL_USERNAME = None
	MAIL_PASSWORD = None

	# administrator list
	ADMINS = ['jon_engelbert@hotmail.com']

class TestConfiguration(BaseConfiguration):
	TESTING = True
	# WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # + join(_cwd, 'testing.db')

	# Since we want our unit tests to run quickly
	# we turn this down - the hashing is still done
	# but the time-consuming part is left out.
	HASH_ROUNDS = 1

class DebugConfiguration(BaseConfiguration):
    DEBUG = True

