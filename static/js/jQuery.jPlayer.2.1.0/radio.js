/**
 * User: Alan
 * Date: 12-7-23
 * Time: am 12:35
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    var playingFlag = false;
    var recordedPlaylist = new Array();
    $.ajax({
        url: radion_song_url,
        type: 'GET',
        dataType: 'json',
        timeout: 3000,
        error: function(){

        },
        success: function(json_data){
            var myCirclePlayer = new CirclePlayer("#jquery_jplayer_1",
                {
                    mp3: json_data.url
                }, {
                    cssSelectorAncestor: "#cp_container_1",
                    swfPath: static_url + "js/jQuery.jPlayer.2.1.0/Jplayer.swf",
                    supplied: "mp3",
                    wmode: "window",
                    play: function() {
                        playingFlag = true;
                    },
                    ended: function() { // The $.jPlayer.event.ended event
                        getNextMedia();
                    },
                    error: function(event) {
                        //alert("Error Event: type = " + event.jPlayer.error.type);
                        reportBrokenMedia(json_data.id,json_data.title, event.jPlayer.error);
                        getNextMedia();
                    }
                });
        }
    });

    function reportBrokenMedia(playListId,title, error) {
        var ret = true;
        $.each(recordedPlaylist, function(key, val) {
            if(val == playListId) {
                ret = false;
            }
        });


        if(ret) {
            $.post(player_logs_url,{playlist_id : playListId, title : title, msg:error},function(result){
                recordedPlaylist.push(playListId);
            });
        }
    }

    function getNextMedia() {

        $.ajax({
            url: radion_song_url,
            type: 'GET',
            dataType: 'json',
            timeout: 3000,
            error: function(){

            },
            success: function(json_data){
                $('#jquery_jplayer_1').jPlayer("setMedia", {
                    mp3: json_data.url // Defines the mp3 url
                });

                if(playingFlag) {
                    $('#jquery_jplayer_1').jPlayer("play");
                }
            }
        });
    }

});