# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
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
        if User.query.filter_by(name=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(name=new_nickname).first() is None:
                break
            version += 1
        return new_nickname
                    

