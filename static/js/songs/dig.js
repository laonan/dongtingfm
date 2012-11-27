$(document).ready(function() {
	
	$('.song_show ul li a').click(function(){
		var link_id = $(this).attr('id').split('_');
		var song_id = link_id[2];
		
		if(link_id[1] == 'dig') {
			$.ajax({
		       	type: 'GET',
		        contentType: 'application/json',
		        url: dig_url,
		        data: 'song_id=' +song_id,
		        dataType: 'json',
		        beforeSend: function() {
	            },
		        error: function (XmlHttpRequest, textStatus, errorThrown){
					   alert(errorThrown);
				}, 
		        success: function(jsonData) {
		        	if(jsonData.dug) {
		        		$('#span_digs_' + song_id).text(jsonData.digs);
		            	$('#span_digs_' + song_id).effect('pulsate', {times:3}, 1000);
		            } else {
		            	$('#span_digs_' + song_id).validationEngine('showPrompt', '您已经动听过此歌曲', '', 'topRight', false);
		            	setTimeout(function() {  
				            $('#span_digs_' + song_id).validationEngine('hide');  
				        }, 2000);
		            }
		        }
		     });
	     }
	});
});