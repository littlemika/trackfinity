from flask_app import app, connection, db
from flask import jsonify
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
import time
import os
import logging
import subprocess
import sys



# 	    CREATE TABLE tracks (
# 	        playlistid,
# 	        trackid,
# 	        artist,
# 	        track_name
# 	    );
# 	    """
#     )


# 	connection.execute(
# 		"""
# 		CREATE TABLE playlist(
# 			id VARCHAR PRIMARY KEY,
# 			name VARCHAR NOT NULL,
# 			owner VARCHAR NOT NULL
# 		);
# 		"""
# 	)

def saveTrack(youtubeURL, playlist_id, trackName, artistName):
    result_dict = dict()

    trackName = trackName.replace("'",'').replace('"','').replace('#','').replace('&','')
    artistName = artistName.replace("'",'').replace('"','')

    track_id = int(time.time())

    query_str = ("""INSERT INTO tracks (trackid, playlistid, artist, track_name) VALUES ('%s', '%s','%s','%s'); """ % (track_id, playlist_id, artistName, trackName))
    print("Saving Track: " + query_str)

    if connection.execute(query_str):
        query_str = ("""SELECT * FROM tracks WHERE track_name='%s' AND artist='%s'""" % (trackName, artistName))
        result = connection.execute(query_str)

        result_dict['artist'] = artistName
        result_dict['track_name'] = trackName
        result_dict['track_id'] = track_id

        count = 0
        for r in result.fetchall():
            count +=1

        if count<= 1:						# only need to save one copy of track
            try:
	            download(youtubeURL, artistName, trackName, track_id)
            except:
                print('download track: ' + trackName + ' failed')
        else:
            time.sleep(1)		# must sleep in case track is already downloaded, then track_id may yield duplicates if data is processed to quickly


    return result_dict


def deleteTrack(track_id):
	query_str = ("""SELECT * FROM tracks WHERE trackid='%s'""" % (track_id))
	result = connection.execute(query_str).fetchall()[0]
	artistName = result['artist']
	trackName = result['track_name']


	query_str = ("""DELETE FROM tracks WHERE trackid='%s'""" % (track_id))
	if connection.execute(query_str):
		query_str = ("""SELECT * FROM tracks WHERE track_name='%s' AND artist='%s'""" % (trackName, artistName))
		result = connection.execute(query_str)

		count = 0
		for r in result.fetchall():
		    count += 1

        # only delete file if track no longer exists in tracks table
		if count == 0:
			filename = getTrackName(artistName, trackName)
			path_to_track = ('"%s/%s"' % (app.config['DEST_DIR'], filename))
			cmd = ("""rm %s""" % (path_to_track))
			os.popen(cmd)
		rt_val = 1
	return rt_val



def createNewPlaylist(playlist_id, playlist_name, message, user):
	logging.warning('Creating playlist %s' % (playlist_id))
	rt_val = 0
	query_str = ("""INSERT INTO playlist (owner, message, id, name) VALUES ('%s', '%s','%s','%s'); """ % (user, message, playlist_id, playlist_name))
	if connection.execute(query_str):
		rt_val = 1

	return rt_val



def getPlaylistTracks(user, playlist_id):
    query_str = ("""SELECT artist, track_name, trackid FROM playlist INNER JOIN tracks ON tracks.playlistID=playlist.id WHERE playlist.id='%s' AND playlist.owner='%s' """ % (playlist_id,user))
    #result = connection.execute(query_str).fetchall()

    result_dict = dict()
    result_list= list()

    result = connection.execute(query_str)

    count = 0
    results = result.fetchall()
    for r in results:
        count += 1

    result_dict['tracks'] = None

    if count != 0:
        for row in results:
            row_dict = dict(row)
            result_list.append(row_dict)

        query_str = ("""SELECT name,owner,message FROM playlist WHERE id='%s' AND owner='%s' """ % (playlist_id, user))
        playlist_results = connection.execute(query_str).fetchall()[0]

        result_dict['tracks'] = result_list
        result_dict['owner'] = playlist_results['owner']
        result_dict['message'] = playlist_results['message']
        result_dict['playlist_name'] = playlist_results['name']

    return result_dict



# create a url for a client to send friend a playlist
def generatePlaylistURL(user_name, playlist_id):
	return ('%splaylist/%s/%s' % (app.config['BASE_URL'], user_name, playlist_id))


# this is the name of the mp3 saved on disk located at $OPENSHIFT_DATA_DIR
def getTrackName(artistName, trackName):
	return  ('%s - %s.mp3' % (trackName, artistName))



def download(URL, artistName, trackName, track_id):
	# name of file being saved on disk
    filename = ('%s - %s.%s' % (trackName, artistName,'%(ext)s'))
   # filename = ('%s - %s.%s' % (trackName, artistName,'mp3'))
    print('filename here ' + filename)

    outputTemplate = ('%s/%s' % (app.config['DEST_DIR'], filename))

    logging.warning('NOTE: downloading ' + filename + ' to ' + outputTemplate)

    # make audio format dynamic
    execution = ("""youtube-dl --extract-audio --verbose --audio-format mp3  --audio-quality  0  -o '%s' %s""" % (outputTemplate, URL))
   # execution = ("""youtube-dl -F -f 'bestaudio[ext=mp3]/bestaudio[ext=m4a]' --add-metadata --extract-audio --audio-format mp3 -o '%s' %s""" % (outputTemplate, URL))


    logging.warning(execution)


    os.system(execution)


    result_dict = dict()
    result_dict['artistName'] = artistName
    result_dict['trackName'] = trackName
    result_dict['filename'] = filename
    result_dict['track_id'] = track_id

    return jsonify(result_dict)




