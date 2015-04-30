# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from pkg import db
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from pkg.mod_auth.models import User
from pkg.mod_auth.models import Base 


class Restaurant(Base):
    __tablename__ = 'restaurant'
   
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
 
