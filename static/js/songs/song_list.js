$(document).ready(function() {
	$('.song_show dl dd a').click(function(){
		var link_id = $(this).attr('id').split('_');
		var song_id = link_id[2];
		
		if(link_id[1] == 'comments') {
			if($.trim($('#slide_content_' + song_id).html()) == '') {
				content_html = $('#xRoundBox_html').html();
				$('#slide_content_' + song_id).html(content_html);
				
				$('#slide_content_' + song_id + ' .xRoundBox .btn').click(function(){
					$(this).prev().attr('id', 'id_comment_' + song_id);
					comment = $(this).prev().val();
					
					var comment_validate = true;
					if($.trim(comment) == '') {
						$('#slide_content_' + song_id).validationEngine('showPrompt', '评论不能为空!', '', 'topLeft', true);
						setTimeout(function() {  
					        $('#slide_content_' + song_id).validationEngine('hide');  
					    }, 2000);
					    
					    comment_validate = false;
					}
					
					if(comment.length > 800) {
						$('#slide_content_' + song_id).validationEngine('showPrompt', '评论字数最多为800字!', '', 'topLeft', true);
						setTimeout(function() {  
					        $('#slide_content_' + song_id).validationEngine('hide');  
					    }, 2000);
					    
					    comment_validate = false;
					}
					
					if(comment_validate) {
						$.ajax({
						       	type: 'POST',
						        contentType: 'application/json',
						        url: comment_url,
						        data: {'song_id':song_id, 'comment':comment},
						        dataType: 'json',
						        beforeSend: function() {
						        	$('#slide_content_' + song_id + ' .xRoundBox .btn').attr('disabled',true);
					            },
						        error: function (XmlHttpRequest, textStatus, errorThrown){
								}, 
						        success: function(jsonData) {
						        	if(jsonData.commented) {
						        		$('#slide_content_' + song_id + ' .xRoundBox .btn').attr('disabled',false);
						        		$('#span_comments_' + song_id).text('评论(' + jsonData.comments_count + ')');
						        		$('#slide_content_' + song_id).validationEngine('showPrompt', '评论成功！', 'pass', 'topLeft', true);
						        		setTimeout(function() {  
									        $('#slide_content_' + song_id).validationEngine('hide');  
									    }, 2000);
						        		$('#id_comment_' + song_id).val('');
						        		$('#id_comment_' + song_id).attr('style','height: 40px;');
						        	}
						      	}
						     });
						}
						
					});
			}
			
			$('.xRoundBox').slideUp();
			
			if(!$('#slide_content_' + song_id + ' .xRoundBox').is(':visible')) {
				$('#slide_content_' + song_id + ' .xRoundBox').slideDown();
			} else {
				$('#slide_content_' + song_id + ' .xRoundBox').slideUp();
			}
	     }
	});
	
	$('input[name="rd_ord"]').click(function(){
		songs_ord_field_url
		
		$.ajax({
	       	type: 'POST',
	        contentType: 'application/json',
	        url: songs_ord_field_url,
	        data: {'rd_ord':$(this).val()},
	        dataType: 'json',
	        beforeSend: function() {
	        	$('#sp_ord_msg').text('正在重排序,请稍候...');
            },
	        error: function (XmlHttpRequest, textStatus, errorThrown){
			}, 
	        success: function(jsonData) {
	        	if(jsonData.saved) {
	        		window.location.href = window.location.href;
	        	}
	      	}
	     });
	});
	
});