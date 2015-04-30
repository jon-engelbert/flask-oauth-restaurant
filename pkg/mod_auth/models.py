# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from pkg import db
from pkg import app
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

    @staticmethod
    def find_by_id(record_id):
        return query.filter_by(id = record_id).first()

    @staticmethod
    def find_all():
        return query.all()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
    # New instance instantiation procedure
    def __init__(self, name, email, picture):

        self.name     = name
        self.email    = email
        self.picture = picture

    def __repr__(self):
        return '<User %r>' % (self.name)    

    @staticmethod
    def make_unique_nickname(nickname):
        if app.db_session.query(User).filter_by(name=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if app.db_session.query(User).filter_by(name=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    @staticmethod
    def create(login_session):
        newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
        app.db_session.add(newUser)
        app.db_session.commit()
        user = app.db_session.query(User).filter_by(email = login_session['email']).first()
        return user.id

    @staticmethod
    def find_id_by_email(email):
        try:
            user = app.db_session.query(User).filter_by(email = email).first()
            return user.id
        except:
            return None


