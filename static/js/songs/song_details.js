$(document).ready(function() {
	$('.xRoundBox').attr('style','display: block;');
	
	$('#btn_comment').click(function () {
		var comment = $('#txt_comment').val();
		
		var comment_validate = true;
		if($.trim(comment) == '') {
			$('#comment_box').validationEngine('showPrompt', '评论不能为空!', '', 'topLeft', true);
			setTimeout(function() {  
				$('#comment_box').validationEngine('hide');  
			}, 2000);
					    
			comment_validate = false;
		}
					
		if(comment.length > 800) {
			$('#comment_box').validationEngine('showPrompt', '评论字数最多为800字!', '', 'topLeft', true);
			setTimeout(function() {  
				$('#comment_box').validationEngine('hide');  
			}, 2000);
					    
			comment_validate = false;
		}
		
		var reply_to_user = $('#txt_reply_to_user').val();
        var share_to_weibo = false;
        if($('#share_to_weibo').is(':checked')) {
            share_to_weibo = true;
        }

		if(comment_validate) {
			$.ajax({
					type: 'POST',
					contentType: 'application/json',
					url: comment_url,
					data: {'song_id':song_id, 'comment':comment, 'reply_to_user':reply_to_user, 'share_to_weibo':share_to_weibo},
					dataType: 'json',
					beforeSend: function() {
						$('#btn_comment').attr('disabled',true);
					},
					error: function (XmlHttpRequest, textStatus, errorThrown){
					}, 
					success: function(jsonData) {
						if(jsonData.commented) {
							$('#span_comments').text('评论(' + jsonData.comments_count + ')');
							$('#div_comments_count').html('<h3>' + jsonData.comments_count + ' 条评论</h3>');
							$('#txt_comment').val('');
							$('#txt_comment').attr('style','height: 120px;');
							update_comments();
							$('#btn_comment').attr('disabled',false);
						}
					}
			});
		}
	});
	
	function update_comments() {
		url = this_url;
		ajax_get_update();
	}
});

function comment_reply(obj) {
	var link_comment_user = $(obj).parent().children()[2];
	if($(link_comment_user).attr('class') == 'datetime')
		link_comment_user = $(obj).parent().children()[1];
	var user_name = $(link_comment_user).text();
	var user_id = $(link_comment_user).attr('id').split('_')[1];
	$('#txt_comment').val('回复 ' + user_name + '：');
	$('#txt_reply_to_user').val(user_id);
}

var del_song_comment_id;
function del_comment(song_comment_id) {
	del_song_comment_id = song_comment_id;
	$('#link_del_comment_dialog').trigger('click');
}

//ajax pagination for comments
function ajax_get_update() {
	   $('#div_comments_content').fadeOut();
       $.get(url, function(results){
          //get the parts of the result you want to update. Just select the needed parts of the response
          var comment_content = $(".comment_content", results);
          var span = $("span.step-links", results);

          //update the ajax_table_result with the return value
          $('#div_comments_content').html(comment_content);
          $('#div_comments_content').fadeIn();
          $('.step-links').html(span);
        }, "html");
    }

//bind the corresponding links in your document to the ajax get function
$( document ).ready( function() {
    $( '.step-links #prev' ).click( function(e) {
        e.preventDefault();
        url = ($( '.step-links #prev' )[0].href);
        ajax_get_update();
    });
    $( '.step-links #next' ).click( function(e) {
        e.preventDefault();
        url = ($( '.step-links #next' )[0].href);
        ajax_get_update();
    });
});

//since the links are reloaded we have to bind the links again
//to the actions
$( document ).ajaxStop( function() {
    $( '.step-links #prev' ).click( function(e) {
        e.preventDefault();
        url = ($( '.step-links #prev' )[0].href);
        ajax_get_update();
    });
    $( '.step-links #next' ).click( function(e) {
        e.preventDefault();
        url = ($( '.step-links #next' )[0].href);
        ajax_get_update();
    });
});