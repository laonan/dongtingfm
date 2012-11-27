$(document).ready(function() {
	$('.btns a').click(function(){
		var playlist_id = $(this).attr('id').split('_')[1];
		$.ajax({
		       	type: 'GET',
		        contentType: 'application/json',
		        url: remove_playlist_url,
		        data: 'playlist_id=' + playlist_id,
		        dataType: 'json',
		        beforeSend: function() {
	            },
		        error: function (XmlHttpRequest, textStatus, errorThrown){
					   alert(errorThrown);
				}, 
		        success: function(jsonData) {
		        	if(jsonData.deleted) {
		        		$('#link_' + jsonData.id ).parent().parent().slideUp();
		            }
		        }
		     });
	});
});