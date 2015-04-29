# source ../ud330/py3env/bin/activate
from pkg import app, db, create_app
if __name__ == "__main__":
    # Because we did not initialize Flask-SQLAlchemy with an application
    # it will use `current_app` instead.  Since we are not in an application
    # context right now, we will instead pass in the configured application
    # into our `create_all` call.
	create_app(app, db, debug=True)
    # Build the database
    # This will create the database file using SQLAlchemy
	db.create_all()
	app.run(host='0.0.0.0', port = 5000)
