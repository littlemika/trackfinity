

from flask import request, jsonify, send_from_directory, redirect, url_for, render_template, Response, stream_with_context
from flask_cors import CORS, cross_origin
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

from flask_app import app, connection
import time
import logging
from models.userModel import createUser, getUser
from models.trackModel import  createNewPlaylist,saveTrack, getPlaylistTracks, getTrackName, generatePlaylistURL, deleteTrack
import subprocess
import sys
sys.path.append('/home/trackfinity/.local/lib/python2.7/site-packages')
import youtube_dl

CORS(app)


@app.route("/deleteTrack", methods=['POST'])
def deleteTrackHandler():
	track_id = request.args.get('track_id')
	deleteTrack(track_id)
	return jsonify({'message':'success'})


@app.route('/deleteGoogleExtTrack', methods=['GET'])
def deleteExtTrackHandler():
    track_id = request.args.get('track_id')
    print('deleteing track ' + track_id)
    deleteTrack(track_id)
    return jsonify({'message':'success'})


@app.route("/playlist/<user>/<playlist_id>", methods=['GET'])
def getPlaylist(user, playlist_id):
    playlist_data = getPlaylistTracks(user, playlist_id)
    template = ''
    tracks = owner = message = playlist_name = None

    if(playlist_data['tracks'] is None):
        message = "Playlist has expired or all tracks from this playlist have been downloaded already!"
        template = 'failure.html'
    else:
        tracks = playlist_data['tracks']
        owner = playlist_data['owner']
        message = playlist_data['message']
        template = 'playlist.html'
        playlist_name = playlist_data['playlist_name']

    return render_template(template, playlist=tracks, owner=owner, message=message, playlist_name=playlist_name)


@app.route("/music/<user>", methods=['GET'])
def music(user=''):
	message = 'Logged in as ' + user
	return render_template('music.html', rt_message=message, user=user)





@app.route("/downloadPlaylist", methods=['POST'])
def handlePlaylistDownload():
    playlist = request.get_json()
    tracks = playlist['tracks']
    playlist_name = playlist['name'].replace("'",'')
    message = playlist['message'].replace("'",'')
    owner = playlist['user']

    playlist_id = int(time.time())

	# create playlist
    createNewPlaylist(playlist_id, playlist_name, message, owner)

    for song in tracks:
        song['track'].replace('&','and').replace('&','and').replace('+','plus')
        saveTrack(song['url'], playlist_id, song['track'], song['artist'].replace('&','and').replace('+','plus'))


    playlistURL = generatePlaylistURL(owner, playlist_id)

    return jsonify({'playlistURL':playlistURL})



@app.route('/playlistSuccess', methods=['GET'])
def playlistSuccess(playlistURL=''):
	return render_template('success.html', playlistURL=playlistURL)



@app.route("/handleNewUser", methods=['POST'])
def handleNewUser():
	# un = request.form['usernameIn']
	# pw = request.form['passwordIn']

	data = request.get_json()
	un =data['un']
	pw = data['pw']

	rt_message = ''

	if createUser(un, pw) == 1:
		rt_message = ("Welcome %s, you can now create playlists and send it to a friend " % (un))
		url = ('%s/%s' % ('music', un))
	else:
		rt_message = 'Username already exists!'
		url = ('/?rt_message=%s' % (rt_message))


	return jsonify({'url':url,'un':un})


@app.route("/login", methods=["POST"])
def login():
	data = request.get_json()
	un =data['un']
	pw = data['pw']
	url = ''


	if getUser(un, pw) > 0:
		rt_message = ("Logged in as %s" % (un))
		url = ('%s/%s' % ('music', un))
	else:
		rt_message = ("Login credentials are invalid!")
		url = ('/?rt_message=%s' % (rt_message))

	return jsonify({'url':url,'un':un})


@app.route("/downloadSingleTrack", methods=['POST'])
def handleSingleTrackDownload():
	youtubeURL = request.args.get('youtubeURL')
	artistName = request.args.get('artistName').replace('&','and').replace('+','plus')
	trackName = request.args.get('trackName').replace('&','and').replace('+','plus')
	playlist_id = ''

	result_dict = saveTrack(youtubeURL, playlist_id, trackName, artistName)
	return jsonify(result_dict)



@app.route('/googleExtDownloadTrack', methods=['GET','OPTIONS'])
@cross_origin()
def getGoogleExtTrack():
    youtubeURL = request.args.get('youtubeURL')

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    info = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtubeURL)

    title = info['title']

    print("Extracted title from youtubedl: " + title)

    # download
    result_dict = saveTrack(youtubeURL, '', title, 'extTrack')
   # filename = result_dict['filename']

    return jsonify(result_dict)

    # return send_from_directory(app.config['DEST_DIR'],
    #                             filename,
    #                             as_attachment=True,
    #                             mimetype='audio/mpeg'
    #                             )


@app.route('/getTestTrack', methods=['GET'])
def getTestTrack():
	filename = 'girls love beyonce - zhu.mp3'
	return send_from_directory(app.config['DEST_DIR'],
                               filename,
                               as_attachment=True
                              )

@app.route('/getTrack', methods=['GET'])
def getTrack():
    artist = request.args.get('artist')
    track_name = request.args.get('track_name')
    filename = getTrackName(artist, track_name)
    attachment_fn = ''


    if "extTrack" in filename:
        attachment_fn = filename[0:len(filename)-14] + '.mp3'
    else:
        attachment_fn = filename

    print('Getting Track ' + attachment_fn + '.'+app.config['DEST_DIR'] +'.')
    return send_from_directory(app.config['DEST_DIR'],
                              filename,
                              as_attachment=True,
                              attachment_filename=attachment_fn,
                              mimetype='audio/mpeg'
                              )
