$(document).ready(function() {
	$('.song_show dl dd a').click(function(){
		var link_id = $(this).attr('id').split('_');
		var song_id = link_id[2];
		
		if(link_id[1] == ('favorite' + favorite_action)) {
			$.ajax({
		       	type: 'GET',
		        contentType: 'application/json',
		        url: favorite_action=='add' ? favorite_add_url : favorite_remove_url,
		        data: 'song_id=' +song_id,
		        dataType: 'json',
		        beforeSend: function() {
		        	$('#link_favorite' + favorite_action + '_' + song_id).attr('disabled',true);
	            },
		        error: function (XmlHttpRequest, textStatus, errorThrown){
					   alert(errorThrown);
					   $('#link_favorite' + favorite_action + '_' + song_id).attr('disabled',false);
				}, 
		        success: function(jsonData) {
		        	
		        	if(jsonData.action == 'add') {
						
						var msg = '';
		        		var promptType = 'pass';
		        		if(jsonData.excuted) {
		        			msg = '收藏成功';
		        			$('#link_favoriteadd_' + song_id + ' span').text('已收藏');
		        		} else {
		        			msg = '此歌曲已经被收藏';
		        			promptType = '';
		        			$('#link_favoriteadd_' + song_id + ' span').text('已收藏');
		        		}
		        		
		        		$('#link_favorite' + favorite_action + '_' + song_id).validationEngine('showPrompt', msg, promptType, 'topRight', false);
			            setTimeout(function() {  
					        $('#link_favorite' + favorite_action + '_' + song_id).validationEngine('hide');  
					    }, 2000);
		        	} else {
		        		if(jsonData.excuted) {
		        			$('#div_song_' + song_id).slideUp();
		        		}
		        	}
				    
				    $('#link_favorite' + favorite_action + '_' + song_id).attr('disabled',false);
		        }
		     });
	     }
	});
});