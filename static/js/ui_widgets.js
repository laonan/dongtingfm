$(document).ready(function() {
	//search box
	$('#txt_seek_key').focus(function() {
		$(this).val('');
	});
	
	$('#txt_seek_key').blur(function() {
		if($(this).val() == '')
			$(this).val('输入歌名、专辑或音乐人...');
	});
	
	$('#btn_seek').click(function() {
		var q = $('#txt_seek_key').val();
		if(q != '输入歌名、专辑或音乐人...')
			window.location.href = search_url + '?q=' + encodeURIComponent(q);
	});
	
	//follow someone
	$('#link_follow').click(function(){
		$.ajax({
	                type: 'GET',
	                contentType: 'application/json',
	                url: follow_url,
	                data: 'following_userid=' + following_userid,
	                dataType: 'json',
	                beforeSend: function()
                    {
                    	$('#link_follow').attr('disabled',true);
                    },
	                error: function (XmlHttpRequest, textStatus, errorThrown){
				       alert(errorThrown);
				    }, 
	                success: function(jsonData) {
	                	if(jsonData.excuted ) {
		                	var msg;
		                	if (jsonData.action == 'follow'){
		                		$('#link_follow').text('[取消关注]');
		                		msg = '关注成功!';
		                		
		                	} else {
		                		$('#link_follow').text('[关注]');
		                		msg = '取消关注成功!';
		                	}
		                	
		                	$('#link_follow').validationEngine('showPrompt', msg, 'pass', 'topLeft', false);
				            setTimeout(function() {  
						        $('#link_follow').validationEngine('hide');  
						    }, 2000);
		                	
		                	$('#span_followers').text('被 ' + jsonData.followers + ' 个人关注');
		                }
	                	$('#link_follow').attr('disabled',false);
	                }
	            });
	});
	
	//notes
	$.ajax({
		type: 'GET',
		contentType: 'application/json',
		url: private_mails_count_url,
		dataType: 'json',
		beforeSend: function() {
		},
		error: function (XmlHttpRequest, textStatus, errorThrown){
		}, 
		success: function(jsonData) {
			
			if(jsonData.unread_mails > 0) {
				creatMailsQtip(jsonData.unread_mails);
			} 
			
			if($('#link_user_box_mails_count').length > 0) {
				var count_msg = '私信(一共：' + jsonData.all_mails + '条，未读：<span style="color:red">' + jsonData.unread_mails + '</span>条)'; 
				$('#link_user_box_mails_count').html(count_msg);
			}
		}
	});
	
	$.ajax({
		type: 'GET',
		contentType: 'application/json',
		url: unread_comments_url,
		dataType: 'json',
		beforeSend: function() {
		},
		error: function (XmlHttpRequest, textStatus, errorThrown){
		}, 
		success: function(jsonData) {
			creatUserQtip(new_followers,jsonData.unread_comments);
		}
	});
	
	
	function creatMailsQtip(mails) {
		$('#link_mails').qtip({
   				content: {
      			text: '<a href="' + my_mails_url + '">' + mails + '条未读私信</a>'
   			},
   			show: {
               event: false, // Don't specify a show event...
               ready: true // ... but show the tooltip when ready
            },
            hide: false,
            style: {
			      tip: {
			         corner: true,
			         offset: 20 // Give it 20px offset from the side of the tooltip
			      }
			}
		});
	}
	
	function creatUserQtip(follower_num,comments_num) {
		var txt = '';
		var corner = 'top right';
		var opposite_corner = 'bottom left';
		
		if(follower_num > 0) {
			txt += '<a href="' + my_followers_url + '">' + follower_num + '个新的关注者</a> ';
		}
		if(comments_num > 0) {
			txt +=  (follower_num > 0 ? '|':'') + ' <a href="' + comments_for_me_url + '">' + comments_num + '条新评论</a>';
		}
		
		if(follower_num > 0 || comments_num > 0) {
			$('#link_user').qtip({
	   			content: {
	      			text: txt
	   			},
	   			show: {
	               event: false, // Don't specify a show event...
	               ready: true // ... but show the tooltip when ready
	            },
	            hide: false,
	            position: {
					my: corner, // Use the corner...
					at: opposite_corner // ...and opposite corner
				},
	            style: {
	            	  tip: {
				         offset: 20, // Give it 5px offset from the side of the tooltip
				      }
				}
			});
		}
	}
	// end notes
	
	//roll to top
	$('#roll').hide();
	$(window).scroll(function() {
		if($(window).scrollTop() >= 100){
				$('#roll').fadeIn(400);
	    } else {
	    	$('#roll').fadeOut(200);
	    }
	 });
	$('#roll_top').click(function(){$('html,body').animate({scrollTop: '0px'}, 800);});
	$('#roll_bottom').click(function(){$('html,body').animate({scrollTop:$('#footer').offset().top}, 800);});

});