// https://github.com/JMPerez/spotify-web-api-js


//spotifyApi.getPlaylistTracks("1212962782","2p7BVGlaCBJLmCcvOVF0XT").then(playlistCallback,playlistFail);

$(document).ready(function(){


    var spotifyApi = new SpotifyWebApi();
    var AUTHORIZE_ENDPOINT = 'https://accounts.spotify.com/authorize?';
    var TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token';
    var CLIENT_ID = '4330ca79e88449bc9927142229055cb7';

    function authorize(){
        var auth_params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': 'http://trackfinity.pythonanywhere.com/',
            'show_dialog': 'true',
            'scope': 'playlist-read-private'
        };

       // alert(AUTHORIZE_ENDPOINT+$.param(auth_params)+"&callback=?");
        alert('here');
       $.ajax({
           url: AUTHORIZE_ENDPOINT,
           dataType: 'jsonp',
           data: auth_params,
           success: function(data){
               alert('here');
              // alert(data);
           }
       })

        // var url ='https://accounts.spotify.com/en/authorize?client_id=4330ca79e88449bc9927142229055cb7&response_type=code&redirect_uri=http:%2F%2Ftrackfinity.pythonanywhere.com%2F&show_dialog=true&callback=?';
        // $.getJSON(url, function(data){
        //     alert(data);

        //     //scopes
        // });

    }

  //  authorize();

    function getAccessTokens(){
         $.getJSON(TOKEN_ENDPOINT+"?callback=?", function(result){
           //response data are now in the result variable
           alert(result);
        });
    }


    function playlistCallback(data){
        console.log(data);
    }


});






$(document).ready(function(){
     if( navigator.userAgent.match(/Android/i)
         || navigator.userAgent.match(/webOS/i)
         || navigator.userAgent.match(/iPhone/i)
         || navigator.userAgent.match(/iPad/i)
         || navigator.userAgent.match(/iPod/i)
         || navigator.userAgent.match(/BlackBerry/i)
         || navigator.userAgent.match(/Windows Phone/i)
     ){
        alert('Please View On Laptop/Computer');
      }

    if(window.innerWidth <= 800 && window.innerHeight <= 600) {
     alert('Please View On Laptop/Computer');
   }

});



var musicApp = angular.module('musicApp', []). config(['$interpolateProvider',
	function($interpolateProvider) {
		$interpolateProvider.startSymbol('[[');
    	$interpolateProvider.endSymbol(']]');
	}
]);


musicApp.controller('userCtrl', function($scope, $http){

	$scope.userURL = '/login';
	$scope.newUserSelected = false;


	$scope.updateURL = function(url){
		$scope.userURL = url;
	}

	$scope.userFunctions = function(newUserSelected){
		var params = {
			'un': $('#usernameIn').val(),
			'pw': $('#passwordIn').val()
		};

		// alert(newUserSelected);
		var request_url;
		if(newUserSelected){
			request_url = '/handleNewUser';
		}else{
			request_url = '/login';
		}

		$http({
			url: request_url,
			data:params,
			method: 'POST'
		}).then(function success(data){
			console.log('');
			window.location = data.data['url'];
		}, function failure(){
			alert('new user creation failed.');
		});
	}
});

musicApp.controller('trackDownloadCtrl', function($scope, $http){

    $scope.downloadAvailable = false;
    $scope.downloadLinks = true;
    $scope.downloadMessage = '';
    $scope.currentTrack = {
    	'downloadAvailable': false,
    	'trackName': undefined,
    	'artistName': undefined,
    	'filename': ''
    }

	$scope.playlistTracks = [];
	$scope.playlistURL = '';
	$scope.curPlaylistTrackURL = '';
	$scope.curPlaylistTrackArtist = '';
	$scope.curPlaylistTrack = '';


	$scope.generatePlaylist = function(name, message){
		//var playlist =  angular.toJson($scope.playlistTracks);
		var playlist = {};
		playlist['tracks'] = $scope.playlistTracks;
		playlist['name'] = name;
		if(message==undefined){message='';}
		playlist['message'] = message;
		playlist['user'] = $('#user').val();



		// var stream_url = '/streamPlaylistDownload?parameters=' + encodeURIComponent(JSON.stringify(playlist));
		// var source = new EventSource(stream_url);
		// var chunk_size = parseInt(100/playlist['tracks'].length);
		// var progress_width = 0;
  //       source.addEventListener('message', function callback(event){
  //       	alert(event.data);
  //       	if(progress_width<100){
  //       		progress_width = parseInt($('.progress-bar').width()) + chunk_size;
  //       		$('.progress-bar').css('width', progress_width + '%').attr('aria-valuenow', progress_width);
  //       	}else{
  //       		$scope.playlistURL = event.data;
  //       	}
  //       });

  //       return;
  		$('#playlistSuccessModal').modal('show');

		$.ajax({
	        type: 'POST',
	        url: '/downloadPlaylist',
	        dataType:'json',
	        contentType: "application/json",
	        data:  JSON.stringify(playlist),
	        success: function(data) {
	        	console.log(data['playlistURL']);

	        	$scope.$apply(function(){
	        		$scope.playlistURL = data['playlistURL'];
	        	});
	        },
	        error: function(jqXHR, exception) {
	            if (jqXHR.status === 0) {
	                alert('Not connect.\n Verify Network.');
	            } else if (jqXHR.status == 404) {
	                alert('Requested page not found. [404]');
	            } else if (jqXHR.status == 500) {
	                alert('Internal Server Error [500].');
	            } else if (exception === 'parsererror') {
	                alert('Requested JSON parse failed.');
	            } else if (exception === 'timeout') {
	                alert('Time out error.');
	            } else if (exception === 'abort') {
	                alert('Ajax request aborted.');
	            } else {
	                alert('Uncaught Error.\n' + jqXHR.responseText);
	            }
		    }
    	});
	}

	$scope.addTrackToPlaylist = function(curPlaylistTrackURL, curPlaylistTrackArtist, curPlaylistTrack){
    	var song = {
    	    'url': curPlaylistTrackURL,
    	    'artist': curPlaylistTrackArtist,
        	'track': curPlaylistTrack
    	}

    	$scope.curPlaylistTrackURL = '';
    	$scope.curPlaylistTrackArtist = '';
    	$scope.curPlaylistTrack = '';

    	$scope.playlistTracks.push(song);
	}

	$scope.swapMusicSection = function($event, sectionID){
		var currElement =  $(angular.element($event.currentTarget));

		// handle section
		$('.m-section').hide();
		$(sectionID).show();

		// handle menu tab
		$('.m-tab').removeClass('active');
		$(currElement).addClass('active');


		if($event.target.id == 'playlistSectionA'){
			$('#playlistInfoModal').modal('show');
		}else{
			$('#playlistInfoModal').modal('hide');
		}
	}

    $scope.getTrackUrl = function(){
        $scope.currentTrack.trackName = $scope.currentTrack.trackName.replace("#","");
    	var url = '/getTrack?artist=' + $scope.currentTrack.artistName  + '&track_name=' + $scope.currentTrack.trackName + '&track_id=' + $scope.currentTrack.track_id;
    	return encodeURI(url);
    }

	$scope.getTrack = function(youtubeURL, trackName, artistName){

		var data = $.param({
	        youtubeURL: "youtubeURL",
	        trackName: "trackName",
	        artistName: "artistName"
        });

        var params = {};
        params['youtubeURL'] = youtubeURL;
        params['trackName'] = trackName;
        params['artistName'] = artistName;

        $http({
        	method: 'POST',
        	url: '/downloadSingleTrack',
        	params: params
        	// paramSerializer: '$httpParamSerializerJQLike'
        }).then(function success(data){
            $scope.currentTrack.downloadAvailable = true;
            $scope.currentTrack.trackName = data.data['track_name'];
            $scope.currentTrack.artistName = data.data['artist'];
            $scope.currentTrack.track_id = data.data['track_id'];

            $scope.trackName = '';
            $scope.artistName = '';
            $scope.youtubeURL = '';

            $scope.downloadMessage = data.data['track_name'] + ' by ' + data.data['artist'];
        //	$('#downloadTrackButton').removeClass('disabled');

            console.log('download successful');
        }, function failure(){

        });

	};

	$scope.deleteTrack = function($event, track_id){
			var params = {};
			params['track_id'] = track_id;

			var currElement =  $(angular.element($event.currentTarget));


		    $scope.downloadLinks = false;

            setTimeout(function(){
                $http({
    				method: 'POST',
    				url: '/deleteTrack',
    				params: params
    				// paramSerializer: '$httpParamSerializerJQLike'
    			}).then(function success(data){
    			    console.log('track deleted');
    				location.reload();
    			}, function failure(){

    			});
            }, 3000);


	};
});




function printJSON(json){
    alert(JSON.stringify(json, null, 2));
    console.log(JSON.stringify(json, null, 2));
}
