$(document).ready(function() {
	
	$('.song_show dl dd a').click(function(){
		var link_id = $(this).attr('id').split('_');
		var song_id = link_id[2];
		
		if(link_id[1] == 'bury') {
			$.ajax({
		       	type: 'GET',
		        contentType: 'application/json',
		        url: bury_url,
		        data: 'song_id=' +song_id,
		        dataType: 'json',
		        beforeSend: function() {
		        	$('#link_bury_' + song_id + ' span').text('正在难听之...');
		        	$('#div_song_' + song_id).attr('disabled', true);
	            },
		        error: function (XmlHttpRequest, textStatus, errorThrown){
					   alert(errorThrown);
				}, 
		        success: function(jsonData) {
		        	var exist_bury_msg = false;
		        	
		        	if(jsonData.buried) {
		        		if(hide_bury) {
		        			$('#div_song_' + song_id).slideUp();
		        		} else {
		        			exist_bury_msg = true;
		        		}
		            } else {
		            	exist_bury_msg = true;
		            }
		            
		            if(exist_bury_msg) {
			            $('#link_bury_' + song_id + ' img').remove();
			        	$('#link_bury_' + song_id + ' span').text('已难听');
			        	$('#link_bury_' + song_id).attr('id', '#link_buried_' + song_id);
			        }
		        }
		     });
	     }
	});
});