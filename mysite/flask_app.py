#!/usr/bin/python2.7.6
from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
import os
import sys
import atexit
import time
import logging
import sys
sys.path.append('/home/trackfinity/.local/lib/python2.7/site-packages')
from flask.ext.cors import CORS     # pip show flask.ext.cors
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # enable cross domain requests
app.config['BINARY'] = '/home/trackfinity/.local/lib/python2.7/site-packages/youtube_dl'
app.config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))
app.config['DEST_DIR'] = '/home/trackfinity/mysite/tracks'
app.config['BASE_URL'] = 'http://trackfinity.pythonanywhere.com/'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DB_PATH'] = 'sqlite:///' + os.path.join(app.config['BASE_DIR'], 'app.db')



db = SQLAlchemy(app)

engine = create_engine(app.config['DB_PATH'], echo=True)
connection = engine.connect()

from controller import *
from models.trackModel import deleteTrack
from models.userModel import *




#called everytime index is called
def check_playlists():
	qry_str = 'SELECT * FROM playlist'

	results = connection.execute(qry_str)

	if results:
		for row in results.fetchall():
			time_created = str(row['id'])		# id of playlist is the unix time stampe

			time_interval = int(time.time()) - int(time_created)
			minutes = int(time_interval/60)		# get minutes passed by since time of creation

			if minutes > 1440:					# if playlist exists for more than 24 hours, delete
				print('DELETING PLAYLIST ' + time_created)
				# delete playlist
				qry_str = ("""DELETE FROM playlist WHERE id='%s'""" % (time_created))
				connection.execute(qry_str)

				# delete songs in the playlist
				qry_str = ("""SELECT * from tracks WHERE playlistid='%s'""" % (time_created))
				results = connection.execute(qry_str)

				for track in results.fetchall():
					deleteTrack(track['trackid'])
	else:
		raise Exception(sys.argv[0:])



@app.route("/")
def index():
	#check_playlists()
	message = request.args.get('rt_message')
	if message is None:
		message = ''
	return render_template('user.html', rt_message=message)




# Shutdown your cron thread if the web process is stopped
# atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == "__main__":
    app.run()
