$(document).ready(function() {
	
	$('#link_radio_dig').click(function(){
			
			var title = $('#jp_playlist_2 a.jp-playlist-current').text();
			
			$.ajax({
		       	type: 'GET',
		        contentType: 'application/json',
		        url: radio_dig_url,
		        data: 'title=' +title,
		        dataType: 'json',
		        beforeSend: function() {
	            },
		        error: function (XmlHttpRequest, textStatus, errorThrown){
					   //alert(errorThrown);
				}, 
		        success: function(jsonData) {
		        	//alert(jsonData.dug);
		        }
		     });
	});
});