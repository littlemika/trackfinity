
from flask_app import app, connection, db
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref


# command to access db: psql trackfinity adminvjvhien

class users(db.Model):
	__tablename__ = 'Users'
	__table_args__ = {'extend_existing': True}			# ONLY IF TABLE ALREADY EXISTS IN DATABASE

	username = Column(String, primary_key = True)
	password = Column(String)

	def __init__(self, username, password):
		self.username = username
		self.password = password



def createUser(un, pw):
    rt_message = 0

    query_str = ("""SELECT * FROM users WHERE username='%s' """ % (un))
    result = connection.execute(query_str)
    count = 0
    for r in result.fetchall():
        count +=1

    if count > 0:
    	rt_message = 0
    else:
    	query_str = ("""INSERT INTO users (username, password) VALUES ('%s', '%s'); """ % (un, pw))
    	if connection.execute(query_str):
    		rt_message = 1

    return rt_message

def getUser(un, pw):
    query_str = ("""SELECT * FROM users WHERE username='%s' AND password='%s'; """ % (un, pw))
    result = connection.execute(query_str)
    count = -1
    for r in result.fetchall():
        count = 1


    return count